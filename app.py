import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Telegram token'ını ortam değişkenlerinden al
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

# Webhook'u başlat
async def main():
    # Portu ortam değişkenlerinden al, varsayılan olarak 8443 kullan
    port = int(os.environ.get("PORT", 8443))

    # Webhook URL'inizi buraya yazın (örneğin Render kullanıyorsanız)
    # Örnek: "https://your-app-name.onrender.com/webhook"
    webhook_url = os.environ.get("WEBHOOK_URL", f"https://your-app-name.onrender.com/webhook")

    # Application nesnesini başlat
    await application.initialize()

    # Webhook'u ayarla
    await application.bot.set_webhook(url=webhook_url)

    # Webhook'u çalıştır
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="/webhook",
        webhook_url=webhook_url
    )

    print(f"Bot webhook ile çalışıyor: {webhook_url}")

# Uygulamayı başlat
if __name__ == "__main__":
    asyncio.run(main())