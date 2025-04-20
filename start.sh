#!/bin/bash

if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Installing..."
    apt-get update && apt-get install -y ffmpeg
fi

python telegram-music-bot.py
