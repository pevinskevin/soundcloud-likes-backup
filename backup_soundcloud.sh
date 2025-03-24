#!/bin/bash

# Simple wrapper script for the SoundCloud Backup Tool

# Check if yt-dlp is installed
if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp is not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: ffmpeg is not installed."
    echo "Please install ffmpeg first:"
    echo "  • Mac: brew install ffmpeg"
    echo "  • Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  • Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

# Execute the Python script
python sc_backup.py "$@"

echo ""
echo "Downloads completed! Your tracks are in the 'downloads' directory."
echo "Tracks are organized by artist." 