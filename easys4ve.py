import os
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

# Bot token'ınızı buraya ekleyin
TOKEN = "7733905960:AAF52DBRKmwJ-49PgNbitkJMmo8FcXrfw8Y"

# Videoyu indirme fonksiyonu
async def download_video(url):
    ydl_opts = {
        'format': 'best',  # Birleştirme gerektirmeyen en iyi formatı seç
        'outtmpl': 'video.%(ext)s',  # Çıktı dosya adı
        'quiet': True,  # Gereksiz çıktıları gizle
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "video.mp4"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# /start komutu için handler
async def start(update: Update, context):
    await update.message.reply_text("Merhaba! Bana herhangi bir video linki gönder, en yüksek kalitede indireyim (YouTube, Instagram, TikTok, vb.).")

# Mesaj handler'ı - Link geldiğinde çalışır
async def handle_message(update: Update, context):
    message = update.message.text
    chat_id = update.message.chat_id

    # URL kontrolü (basit bir doğrulama)
    if "http" in message:
        await update.message.reply_text("Video indiriliyor, lütfen bekle...")
        video_file = await download_video(message)

        if os.path.exists(video_file):
            # Telegram'a video gönderme
            with open(video_file, 'rb') as video:
                await context.bot.send_video(chat_id=chat_id, video=video, supports_streaming=True)
            os.remove(video_file)  # Dosyayı temizle
        else:
            await update.message.reply_text(video_file)  # Hata mesajı
    else:
        await update.message.reply_text("Lütfen geçerli bir video linki gönder (örneğin: YouTube, Instagram, TikTok).")

# Ana fonksiyon
def main():
    # Application oluştur
    app = Application.builder().token(TOKEN).build()

    # Komut ve mesaj handler'larını ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botu başlat
    app.run_polling()

if __name__ == '__main__':
    main()