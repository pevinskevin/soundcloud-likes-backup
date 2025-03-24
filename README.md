# SoundCloud Backup Tool

A simple Python tool to backup your liked tracks from SoundCloud.

## Features

- Downloads all liked tracks from a SoundCloud profile
- Converts tracks to high-quality MP3 format
- Organizes downloads by artist
- Embeds thumbnails and metadata in the files
- Simple terminal-based operation

## Prerequisites

1. Python 3.8 or higher
2. FFmpeg (required for audio conversion)
   - Mac: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## Setup

1. Install Python 3.8 or higher
2. Install FFmpeg (see above)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your SoundCloud username (optional):
   ```bash
   # Create a .env file in the project root directory
   echo "SOUNDCLOUD_USERNAME=your_username" > .env
   ```

## Usage

You can run the tool in two ways:

1. Using the shell script (recommended):
   ```bash
   # Make the script executable (first time only)
   chmod +x backup_soundcloud.sh
   
   # Run with username
   ./backup_soundcloud.sh --username YOUR_SOUNDCLOUD_USERNAME
   
   # Or if username is in .env file
   ./backup_soundcloud.sh
   ```

2. Using Python directly:
   ```bash
   python sc_backup.py --username YOUR_SOUNDCLOUD_USERNAME
   # Or if username is in .env file
   python sc_backup.py
   ```

## Downloads

All downloaded tracks are saved in the `downloads` directory in your project folder. The tracks are organized by artist:

```
downloads/
├── Artist1/
│   ├── Track1.mp3
│   └── Track2.mp3
├── Artist2/
│   ├── Track3.mp3
│   └── Track4.mp3
└── ...
```

You can find the downloads directory at:
- Full path: `~/Documents/YOUR_PROJECT_NAME/downloads`
   (Replace `YOUR_PROJECT_NAME` with whatever you named your project directory)
- Or navigate to it in Finder by pressing Cmd+Shift+G and pasting the path

## How it Works

This tool uses [yt-dlp](https://github.com/yt-dlp/yt-dlp), a powerful media downloader, to fetch your liked tracks from SoundCloud. It:

1. Accesses your public likes page (no login required)
2. Downloads all tracks in high-quality audio
3. Organizes them by artist in the downloads directory
4. Embeds artwork and metadata in the files

## Common Issues

1. **FFmpeg not found**
   - Solution: Install FFmpeg using the instructions in the Prerequisites section

2. **Rate limiting**
   - Solution: Wait a while and try again if you hit SoundCloud's rate limits

3. **FileNotFoundError**
   - Solution: The script automatically creates necessary directories. Check file permissions if issues persist.

## Note

This tool is for personal use only. Please respect SoundCloud's terms of service and artists' rights. 