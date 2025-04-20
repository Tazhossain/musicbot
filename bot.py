import os
from dotenv import load_dotenv
import tempfile
import logging
import shutil
import asyncio
import subprocess
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch
from pytubefix import YouTube
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
DOWNLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

search_cache = {}

WELCOME_MSG = """
👋 *Welcome to T2MusicBot!*
Developed by *Taz*

✨ *Features:*
• Type any song name (e.g. *Blinding Lights*)
• Get ULTRA HIGH QUALITY MP3 downloads (320kbps)
• Tracks include album artwork thumbnails
• Smart search handles typos and partial names

Simply send a song name to get started!
"""

HELP_MSG = """
*T2MusicBot Commands & Tips*

• `/start` - Welcome message
• `/help` - Display this help info
• `/about` - About this bot
• Send any song name to search

*Pro Tips:*
• Include artist name for better results
• The bot works with most popular tracks
• Ultra high quality audio (320kbps)
• Music includes album art thumbnails

Example: `Blinding Lights The Weeknd`
"""

ABOUT_MSG = """
🎵 *T2MusicBot* 🎵

A lightning-fast music downloader bot that delivers premium quality MP3s (320kbps) with album artwork directly to your Telegram.

*Developed by:* Taz
*Version:* 2.0.0

Powered by advanced streaming technology for instant downloads.
"""

@bot.message_handler(commands=['start'])
async def handle_start(message):
    await bot.send_message(message.chat.id, WELCOME_MSG, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
async def handle_help(message):
    await bot.send_message(message.chat.id, HELP_MSG, parse_mode='Markdown')

@bot.message_handler(commands=['about'])
async def handle_about(message):
    await bot.send_message(message.chat.id, ABOUT_MSG, parse_mode='Markdown')

async def search_songs(query, max_results=6):
    try:
        videos_search = VideosSearch(query, limit=max_results)
        results = videos_search.result()
        
        songs = []
        for i, video in enumerate(results['result']):
            song = {
                "index": str(i+1),
                "title": video['title'],
                "artist": video['channel']['name'],
                "duration": video['duration'],
                "video_id": video['id'],
                "thumbnail": video['thumbnails'][0]['url']
            }
            songs.append(song)
        
        return songs
    except Exception as e:
        logger.error(f"Error searching songs: {e}")
        return []

@bot.message_handler(func=lambda msg: True)
async def handle_song_search(message):
    query = message.text.strip()
    logger.info(f"Searching for: {query}")
    
    status_msg = await bot.send_message(message.chat.id, "🎵 *Finding your music...*", parse_mode='Markdown')
    
    try:
        songs = await search_songs(query)
        
        if not songs:
            await bot.edit_message_text("❌ No results found. Try another song name.", 
                                 message.chat.id, 
                                 status_msg.message_id)
            return
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        search_cache[message.chat.id] = songs
        
        for song in songs:
            label = f"{song['title']} - {song['artist']} [{song['duration']}]"
            if len(label) > 60:
                label = label[:57] + "..."
                
            keyboard.add(InlineKeyboardButton(label, callback_data=f"song_{song['index']}"))
        
        await bot.edit_message_text(f"🎵 *Select a song to download:*",
                             message.chat.id, 
                             status_msg.message_id,
                             reply_markup=keyboard,
                             parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Search error: {e}")
        await bot.edit_message_text("❌ Search error. Please try again later.", 
                             message.chat.id, 
                             status_msg.message_id)

def convert_to_high_quality(input_file, output_file):
    try:
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-b:a', '320k',
            '-metadata', 'comment=T2MusicBot',
            '-y',
            output_file
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        logger.error(f"FFmpeg conversion error: {e}")
        return False

async def download_song(video_id):
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(video_url)
        
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        if not audio_streams:
            audio_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        if not audio_streams or len(audio_streams) == 0:
            raise Exception("No valid stream found")
            
        high_quality_stream = audio_streams[0]
        
        tmp_dir = tempfile.mkdtemp()
        tmp_path = high_quality_stream.download(output_path=tmp_dir)
        
        original_mp3 = os.path.splitext(tmp_path)[0] + '_original.mp3'
        os.rename(tmp_path, original_mp3)
        
        final_mp3 = os.path.splitext(tmp_path)[0] + '.mp3'
        
        if shutil.which('ffmpeg'):
            success = convert_to_high_quality(original_mp3, final_mp3)
            if not success:
                os.rename(original_mp3, final_mp3)
        else:
            os.rename(original_mp3, final_mp3)
        
        thumbnail_url = yt.thumbnail_url
        thumbnail_path = None
        
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img = img.convert('RGB')
                    thumbnail_path = os.path.join(tmp_dir, "thumbnail.jpg")
                    img.save(thumbnail_path, "JPEG", quality=95)
            except Exception as e:
                logger.error(f"Thumbnail error: {e}")
                thumbnail_path = None
        
        return {
            "file_path": final_mp3,
            "title": yt.title,
            "performer": yt.author.replace(" - Topic", "").strip() if yt.author else "Unknown",
            "duration": yt.length,
            "thumbnail": thumbnail_path,
            "tmp_dir": tmp_dir,
            "bitrate": "320kbps"
        }
    except Exception as e:
        logger.error(f"Download error: {e}")
        if 'tmp_dir' in locals():
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except:
                pass
        return None

@bot.callback_query_handler(func=lambda call: call.data.startswith('song_'))
async def handle_song_selection(call):
    chat_id = call.message.chat.id
    data_parts = call.data.split("_")
    
    if len(data_parts) < 2 or chat_id not in search_cache:
        await bot.answer_callback_query(call.id, "Session expired. Please search again.")
        return
    
    song_index = data_parts[1]
    
    selected_song = None
    for song in search_cache[chat_id]:
        if song['index'] == song_index:
            selected_song = song
            break
    
    if not selected_song:
        await bot.answer_callback_query(call.id, "Song not found. Please search again.")
        return
    
    await bot.answer_callback_query(call.id)
    
    status_msg = await bot.edit_message_text(
        f"⬇️ *Downloading... Wait For It Man*",
        chat_id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    async def download_and_send():
        download_result = await download_song(selected_song['video_id'])
        
        if not download_result:
            await bot.edit_message_text(
                f"❌ *Download failed.* Please try another song.",
                chat_id,
                status_msg.message_id,
                parse_mode='Markdown'
            )
            return
        
        try:
            with open(download_result['file_path'], 'rb') as audio_file:
                thumbnail_file = None
                if download_result['thumbnail']:
                    thumbnail_file = open(download_result['thumbnail'], 'rb')
                
                await bot.send_audio(
                    chat_id,
                    audio_file,
                    caption=f"🎵 {download_result['title']} - {download_result['performer']}",
                    title=download_result['title'],
                    performer=download_result['performer'],
                    duration=download_result['duration'],
                    thumb=thumbnail_file,
                    reply_to_message_id=call.message.reply_to_message.message_id if call.message.reply_to_message else None
                )
                
                if thumbnail_file:
                    thumbnail_file.close()
                
            await bot.delete_message(chat_id, status_msg.message_id)
            
        except Exception as e:
            logger.error(f"Send error: {e}")
            await bot.edit_message_text(
                f"❌ *Error sending file.* Please try again.",
                chat_id,
                status_msg.message_id,
                parse_mode='Markdown'
            )
        finally:
            try:
                shutil.rmtree(download_result['tmp_dir'], ignore_errors=True)
            except:
                pass
    
    asyncio.create_task(download_and_send())

async def main():
    logger.info("T2MusicBot is starting...")
    me = await bot.get_me()
    logger.info(f"Bot started as @{me.username}")
    await bot.polling(non_stop=True, timeout=60)

if __name__ == '__main__':
    asyncio.run(main())
