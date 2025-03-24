#!/usr/bin/env python3
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp
from tqdm import tqdm
from downloader import SoundCloudDownloader

# Create necessary directories first
directories = ['downloads', 'logs', 'data']
for directory in directories:
    Path(directory).mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/soundcloud_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SoundCloudBackup:
    def __init__(self, username, password=None):
        self.username = username
        self.password = password
        self.base_url = f"https://soundcloud.com/{username}/likes"
        self.download_dir = Path("downloads")
        self.setup_directories()
        self.setup_selenium()

    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        directories = ['downloads', 'logs', 'data']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    def setup_selenium(self):
        """Initialize Selenium WebDriver with Brave browser."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set Brave binary location
        brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        if not os.path.exists(brave_path):
            raise Exception("Brave browser not found. Please install Brave browser first.")
        
        chrome_options.binary_location = brave_path
        
        # Try to find an existing ChromeDriver in the current directory or PATH
        chromedriver_path = None
        # Check current directory
        if os.path.exists("./chromedriver"):
            chromedriver_path = "./chromedriver"
        # Check common locations on macOS
        elif os.path.exists("/usr/local/bin/chromedriver"):
            chromedriver_path = "/usr/local/bin/chromedriver"
        elif os.path.exists(os.path.expanduser("~/chromedriver")):
            chromedriver_path = os.path.expanduser("~/chromedriver")
        
        if not chromedriver_path:
            logger.error("Could not find ChromeDriver. Please download it manually and place it in the project directory.")
            logger.error("You can download ChromeDriver from: https://chromedriver.chromium.org/downloads")
            raise Exception("ChromeDriver not found. See log for details.")
        
        logger.info(f"Using ChromeDriver at: {chromedriver_path}")
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    async def login(self):
        """Login to SoundCloud if credentials are provided."""
        if not self.password:
            return

        try:
            logger.info("Attempting to login to SoundCloud...")
            self.driver.get("https://soundcloud.com/login")
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Fill in login form
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Submit form
            password_field.submit()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "header__userMenu"))
            )
            
            logger.info("Successfully logged in to SoundCloud")
        except Exception as e:
            logger.error(f"Failed to login to SoundCloud: {e}")
            raise

    async def fetch_liked_tracks(self):
        """Fetch liked tracks from the SoundCloud profile."""
        logger.info(f"Fetching liked tracks for user: {self.username}")
        
        # Login if credentials are provided
        if self.password:
            await self.login()
        
        self.driver.get(self.base_url)
        
        # Wait for the tracks to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "trackItem"))
        )
        
        # Scroll to load more tracks
        await self._scroll_to_load_more()
        
        # Parse the page
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tracks = self._extract_track_info(soup)
        
        return tracks

    async def _scroll_to_load_more(self):
        """Scroll the page to load more tracks."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)  # Wait for content to load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _extract_track_info(self, soup):
        """Extract track information from the page."""
        tracks = []
        track_elements = soup.find_all("div", class_="trackItem")
        
        for track in track_elements:
            try:
                title = track.find("a", class_="trackItem__trackTitle").text.strip()
                url = track.find("a", class_="trackItem__trackTitle")["href"]
                artist = track.find("a", class_="trackItem__username").text.strip()
                
                tracks.append({
                    "title": title,
                    "url": url,
                    "artist": artist
                })
            except Exception as e:
                logger.error(f"Error extracting track info: {e}")
                continue
                
        return tracks

    async def process_tracks(self, tracks):
        """Process all tracks and download them."""
        async with SoundCloudDownloader(self.download_dir) as downloader:
            for track in tqdm(tracks, desc="Downloading tracks"):
                try:
                    await downloader.download_track(track)
                except Exception as e:
                    logger.error(f"Error downloading track {track['title']}: {e}")

    def cleanup(self):
        """Clean up resources."""
        self.driver.quit()

async def main():
    parser = argparse.ArgumentParser(description="Backup SoundCloud liked tracks")
    parser.add_argument("--username", help="SoundCloud username (can also be set in .env file)")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Get username from command line or environment
    username = args.username or os.getenv("SOUNDCLOUD_USERNAME")
    if not username:
        parser.error("Username must be provided either via --username argument or in .env file")
    
    # Get password from environment
    password = os.getenv("SOUNDCLOUD_PASSWORD")

    backup = SoundCloudBackup(username, password)
    try:
        tracks = await backup.fetch_liked_tracks()
        await backup.process_tracks(tracks)
    finally:
        backup.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 