import logging
import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from yt_dlp import YoutubeDL

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_BOT_TOKEN = "8548605981:AAGKUCz6qG8VHx8HpTu79LVmiujlTA_rc50"

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hi! Send me a YouTube link to download.")

async def download_video(update: Update, context) -> None:
    message_text = update.message.text
    youtube_url_match = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[\w\?=\&-]+", message_text)

    if not youtube_url_match:
        await update.message.reply_text("Please send a valid YouTube link.")
        return

    youtube_url = youtube_url_match.group(0)
    await
  
