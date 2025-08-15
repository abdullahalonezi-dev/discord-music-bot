import os
from music_bot import bot

# تشغيل البوت
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ خطأ: يرجى تعيين DISCORD_TOKEN في متغيرات البيئة")
    else:
        bot.run(TOKEN)
