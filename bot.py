
import logging
import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from yt_dlp import YoutubeDL

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8548605981:AAGKUCz6qG8VHx8HpTu79LVmiujlTA_rc50"

# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Send me a YouTube link and I'll download the video for you."
    )

async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me a YouTube link, optionally with metadata like 'title: My Song, artist: John Doe'.")

async def download_video(update: Update, context) -> None:
    """Downloads a YouTube video and sends it to the user."""
    message_text = update.message.text
    chat_id = update.effective_chat.id

    youtube_url_match = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+", message_text)

    if not youtube_url_match:
        await update.message.reply_text("Please send a valid YouTube link.")
        return

    youtube_url = youtube_url_match.group(0)
    metadata_text = message_text.replace(youtube_url, "").strip()

    await update.message.reply_text("Downloading... This might take a moment.")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'cookiefile': 'cookies.txt',  # ဒီစာကြောင်းကို အသစ်ထည့်လိုက်ပါ
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'addmetadata': True,
        'writethumbnail': False,
        'prefer_ffmpeg': True,
        'referer': 'https://www.google.com/',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }



    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            # Check estimated file size before downloading
            # Telegram's limit is 50MB (50 * 1024 * 1024 bytes)
            file_size_limit = 50 * 1024 * 1024
            
            # Try to find a suitable format that is under the size limit
            selected_format = None
            formats = info_dict.get('formats', [])
            # Sort formats by file size in ascending order, prioritizing mp4
            formats.sort(key=lambda x: x.get('filesize', float('inf')))

            for f in formats:
                if f.get('ext') == 'mp4' and f.get('filesize') and f['filesize'] <= file_size_limit:
                    selected_format = f['format_id']
                    break
            
            if not selected_format:
                # If no mp4 under limit, try any format under limit
                for f in formats:
                    if f.get('filesize') and f['filesize'] <= file_size_limit:
                        selected_format = f['format_id']
                        break

            if not selected_format:
                await update.message.reply_text("Video is too large (over 50MB) and no smaller format could be found. Please try a different video.")
                return

            ydl_opts["format"] = selected_format
            with YoutubeDL(ydl_opts) as ydl_download:
                download_info_dict = ydl_download.extract_info(youtube_url, download=True)
                video_file = ydl_download.prepare_filename(download_info_dict)

        if os.path.exists(video_file):
            # Extract metadata
            title = download_info_dict.get('title', 'N/A')
            artist = download_info_dict.get('artist', download_info_dict.get('channel', 'N/A'))
            uploader = download_info_dict.get('uploader', 'N/A')

            caption = f"Title: {title}\nArtist: {artist}\nUploader: {uploader}"

            if metadata_text:
                caption += f"\n\nUser provided metadata: {metadata_text}"

            await context.bot.send_video(chat_id=chat_id, video=open(video_file, 'rb'), caption=caption)
            os.remove(video_file)
        else:
            await update.message.reply_text("Failed to download the video.")

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        if "Unsupported URL" in str(e):
            await update.message.reply_text("The provided URL is not a valid YouTube link or is unsupported.")
        elif "Private video" in str(e) or "unavailable" in str(e):
            await update.message.reply_text("This video is private or unavailable.")
        else:
            await update.message.reply_text(f"An error occurred during download: {e}")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # On non command i.e. message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
