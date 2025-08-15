import os
import discord
from music_bot import bot

# إعدادات Render
PORT = int(os.environ.get('PORT', 10000))

# تشغيل البوت
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ خطأ: يرجى تعيين DISCORD_TOKEN في متغيرات البيئة")
    else:
        print(f"🚀 بدء تشغيل البوت على المنفذ {PORT}")
        bot.run(TOKEN)
