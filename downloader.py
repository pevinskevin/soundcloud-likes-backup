import aiohttp
import asyncio
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class SoundCloudDownloader:
    def __init__(self, download_dir):
        self.download_dir = Path(download_dir)
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def download_track(self, track):
        """Download a track using available download services."""
        sanitized_title = self._sanitize_filename(track['title'])
        artist_dir = self.download_dir / self._sanitize_filename(track['artist'])
        artist_dir.mkdir(exist_ok=True)
        
        output_path = artist_dir / f"{sanitized_title}.mp3"
        
        if output_path.exists():
            logger.info(f"Track already exists: {output_path}")
            return

        # Try different download services
        download_services = [
            self._try_scdownloader,
            self._try_soundcloudmp3,
            self._try_downloadsound
        ]

        for service in download_services:
            try:
                success = await service(track['url'], output_path)
                if success:
                    logger.info(f"Successfully downloaded: {output_path}")
                    return
            except Exception as e:
                logger.error(f"Error with service {service.__name__}: {e}")
                continue

        logger.error(f"Failed to download track: {track['title']}")

    def _sanitize_filename(self, filename):
        """Sanitize filename to be safe for all operating systems."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        return filename[:200]

    async def _try_scdownloader(self, url, output_path):
        """Try downloading using scdownloader.io."""
        try:
            async with self.session.get(f"https://scdownloader.io/download?url={quote(url)}") as response:
                if response.status != 200:
                    return False
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find download button and extract direct URL
                download_button = soup.find('a', {'class': 'download-btn'})
                if not download_button:
                    return False
                
                direct_url = download_button.get('href')
                if not direct_url:
                    return False
                
                # Download the file
                async with self.session.get(direct_url) as download_response:
                    if download_response.status != 200:
                        return False
                    
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await download_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                
                return True
        except Exception as e:
            logger.error(f"Error in scdownloader: {e}")
            return False

    async def _try_soundcloudmp3(self, url, output_path):
        """Try downloading using soundcloudmp3.org."""
        try:
            async with self.session.get(f"https://soundcloudmp3.org/download?url={quote(url)}") as response:
                if response.status != 200:
                    return False
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find download button and extract direct URL
                download_button = soup.find('a', {'class': 'download-button'})
                if not download_button:
                    return False
                
                direct_url = download_button.get('href')
                if not direct_url:
                    return False
                
                # Download the file
                async with self.session.get(direct_url) as download_response:
                    if download_response.status != 200:
                        return False
                    
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await download_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                
                return True
        except Exception as e:
            logger.error(f"Error in soundcloudmp3: {e}")
            return False

    async def _try_downloadsound(self, url, output_path):
        """Try downloading using downloadsound.cloud."""
        try:
            async with self.session.get(f"https://downloadsound.cloud/download?url={quote(url)}") as response:
                if response.status != 200:
                    return False
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find download button and extract direct URL
                download_button = soup.find('a', {'class': 'download-link'})
                if not download_button:
                    return False
                
                direct_url = download_button.get('href')
                if not direct_url:
                    return False
                
                # Download the file
                async with self.session.get(direct_url) as download_response:
                    if download_response.status != 200:
                        return False
                    
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await download_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                
                return True
        except Exception as e:
            logger.error(f"Error in downloadsound: {e}")
            return False 