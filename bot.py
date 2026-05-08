import logging
import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from yt_dlp import YoutubeDL

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8548605981:AAGKUCz6qG8VHx8HpTu79LVmiujlTA_rc50"

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hi! Send me a YouTube link to download.")

async def download_video(update: Update, context) -> None:
    youtube_url = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[\w\?=\&-]+", update.message.text)
    if not youtube_url:
        await update.message.reply_text("Please send a valid YouTube link.")
        return

    await update.message.reply_text("Downloading... Please wait.")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url.group(0), download=True)
            video_file = ydl.prepare_filename(info)
        
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_file, 'rb'))
        os.remove(video_file)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == "__main__":
    main()
  
