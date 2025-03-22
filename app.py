import os
import asyncio
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Application nesnesini oluştur
application = Application.builder().token(TOKEN).build()

# Videoyu indirme fonksiyonu
async def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[filesize<50M]+bestaudio/best[filesize<50M]',
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
            try:
                # Telegram'a video gönderme
                with open(video_file, 'rb') as video:
                    await context.bot.send_video(chat_id=chat_id, video=video, supports_streaming=True)
            except Exception as e:
                await update.message.reply_text(f"Video gönderilirken hata oluştu: {str(e)}")
            finally:
                # Dosyayı her durumda temizle
                if os.path.exists(video_file):
                    os.remove(video_file)
        else:
            await update.message.reply_text(video_file)  # Hata mesajı
    else:
        await update.message.reply_text("Lütfen geçerli bir video linki gönder (örneğin: YouTube, Instagram, TikTok).")

# Handler'ları ekle
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint'i
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Gelen JSON verisini al ve Update nesnesine çevir
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Asenkron işlemi çalıştır
        # Flask asenkron bir framework olmadığı için asyncio.run kullanıyoruz
        asyncio.run(application.process_update(update))
        
        return 'OK', 200
    except Exception as e:
        print(f"Webhook hatası: {str(e)}")
        return 'Error', 500

# Flask sunucusunu başlat
if __name__ == '__main__':
    # Uygulamayı başlatmadan önce botu yapılandır
    port = int(os.environ.get("PORT", 5000))
    
    # Webhook'u ayarla (Render veya başka bir platformda çalışıyorsanız)
    # Not: Webhook URL'inizi platformunuza göre ayarlamalısınız
    # Örneğin: application.bot.set_webhook(url=f"https://your-app.onrender.com/webhook")
    
    app.run(host='0.0.0.0', port=port)