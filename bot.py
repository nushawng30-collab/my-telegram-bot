import logging
import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from yt_dlp import YoutubeDL
from flask import Flask
from threading import Thread

# Render ရဲ့ Port Binding အတွက် Flask ကို သုံးထားပါတယ်
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render ကပေးတဲ့ Port ကိုယူမယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Logging ပြုလုပ်ခြင်း
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# သင်ပေးထားတဲ့ Token ကို ဤနေရာတွင် ထည့်သွင်းထားပါသည်
TELEGRAM_BOT_TOKEN = "8548605981:AAGKUCz6qG8VHx8HpTu79LVmiujlTA_rc50"

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hi! Send me a YouTube link to download.")

async def download_video(update: Update, context) -> None:
    message_text = update.message.text
    # YouTube URL ကို ရှာဖွေခြင်း
    match = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+", message_text)

    if not match:
        await update.message.reply_text("Chyeju hte jaw ai YouTube link sa ya rit.")
        return

    youtube_url = match.group(0) 
    status_msg = await update.message.reply_text("Downloading... myit galu ai hte ala ya rit.")
    
    # Error မတက်အောင် Format ကို ပြင်ဆင်ထားပါတယ်
    ydl_opts = {
        'format': 'best', # အဆင်ပြေဆုံး format ကို အလိုအလျောက်ယူရန်
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
    }

    try:
        # downloads folder မရှိရင် ဆောက်မယ်
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_file = ydl.prepare_filename(info)
        
        # Telegram ဆီသို့ ဗီဒီယို ပြန်ပို့ခြင်း
        with open(video_file, 'rb') as video:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)
        
        # ပို့ပြီးရင် ဖိုင်ကို ပြန်ဖျက်မယ် (Storage မပြည့်အောင်)
        os.remove(video_file)
        await status_msg.delete() 

    except Exception as e:
        await update.message.reply_text(f"Error တက်သွားပါတယ်- {e}")
        print(f"Error detail: {e}")

def main():
    # Render မှာ Bot အမြဲနိုးနေစေဖို့ Web Server စတင်ခြင်း
    keep_alive() 
    
    # Bot ကို စတင်ခြင်း
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
