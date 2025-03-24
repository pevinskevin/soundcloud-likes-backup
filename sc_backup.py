#!/usr/bin/env python3
import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
import subprocess
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['downloads', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def download_liked_tracks(username, output_dir="downloads"):
    """Download all liked tracks from a SoundCloud user using yt-dlp."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the URL for the user's likes
    likes_url = f"https://soundcloud.com/{username}/likes"
    logger.info(f"Downloading liked tracks from: {likes_url}")
    
    # Set up yt-dlp command with appropriate options
    cmd = [
        "yt-dlp",
        "--extract-audio",                          # Extract audio only
        "--audio-format", "mp3",                    # Convert to mp3
        "--audio-quality", "0",                     # Best quality
        "--embed-thumbnail",                        # Embed thumbnail in audio file
        "--add-metadata",                           # Add metadata to file
        "-o", f"{output_dir}/%(uploader)s/%(title)s.%(ext)s",  # Output filename template
        "--no-playlist-reverse",                    # Process in order
        likes_url                                   # URL to download from
    ]
    
    # Run the command
    try:
        logger.info("Starting download process...")
        subprocess.run(cmd, check=True)
        logger.info("Download completed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading tracks: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Backup SoundCloud liked tracks using yt-dlp")
    parser.add_argument("--username", help="SoundCloud username (can also be set in .env file)")
    parser.add_argument("--output-dir", default="downloads", help="Directory to save downloaded tracks")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Get username from command line or environment
    username = args.username or os.getenv("SOUNDCLOUD_USERNAME")
    if not username:
        parser.error("Username must be provided either via --username argument or in .env file")
    
    # Create necessary directories
    create_directories()
    
    # Download tracks
    download_liked_tracks(username, args.output_dir)

if __name__ == "__main__":
    main() 