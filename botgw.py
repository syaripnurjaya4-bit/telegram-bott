from uuid import uuid4
user_links = {}
import subprocess
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- HANDLERS ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Yo! Drop me a YouTube, TikTok, or Instagram link, I’ll snag the audio for ya\n'
        'Use /start for a welcome message.'
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Yo! Drop me a YouTube, TikTok, or Instagram link, I’ll snag the audio for ya'
    )

def extract_url(text):
    url_pattern = r'(https?://[\w\-\.\?\=\&\/%#]+)'
    urls = re.findall(url_pattern, text)
    for url in urls:
        if any(site in url for site in ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com']):
            return url
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    url = extract_url(text)
    if not url:
        await update.message.reply_text('Yo! drop me a YouTube, TikTok, or Instagram link, I’ll snag the audio for ya')
        return
    await update.message.reply_text("Snatchin' your damn track, sit yo ass down.")
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            file_path = os.path.splitext(filename)[0] + '.mp3'
            title = info.get('title', 'Unknown')
            duration = int(info.get('duration', 0))
            mins, secs = divmod(duration, 60)
            await update.message.reply_text(f"Title: {title}\nDuration: {mins}:{secs:02d}")
            await update.message.reply_audio(audio=open(file_path, 'rb'))
            os.remove(file_path)  # auto-delete
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

# --- MAIN ---
def main():
    try:
        subprocess.run(["python", "-m", "yt_dlp", "-U"], check=True)
    except Exception:
        print("Warning: Could not update yt-dlp automatically.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('Bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main()
