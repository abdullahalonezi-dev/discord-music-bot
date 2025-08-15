#!/usr/bin/env python3
"""
إعداد بوت Discord الموسيقي
"""

import os
import sys
import subprocess

def install_requirements():
    """تثبيت المكتبات المطلوبة"""
    print("📦 جاري تثبيت المكتبات المطلوبة...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت المكتبات بنجاح!")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المكتبات")
        return False

def check_ffmpeg():
    """التحقق من وجود FFmpeg"""
    print("🔍 التحقق من وجود FFmpeg...")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg مثبت ومتوفر")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg غير مثبت")
        print("📥 يرجى تثبيت FFmpeg من: https://ffmpeg.org")
        return False

def create_config():
    """إنشاء ملف الإعدادات"""
    config_file = "config.py"
    if os.path.exists(config_file):
        print("✅ ملف config.py موجود بالفعل")
        return True
    
    print("📝 إنشاء ملف config.py...")
    config_content = '''# إعدادات البوت
DISCORD_TOKEN = "your_discord_bot_token_here"

# إعدادات الصوت
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "192"

# إعدادات البوت
COMMAND_PREFIX = "!"
BOT_STATUS = "🎵 !help للمساعدة"

# ألوان الرسائل
COLORS = {
    "SUCCESS": 0x00ff00,    # أخضر
    "ERROR": 0xff0000,      # أحمر
    "WARNING": 0xffff00,    # أصفر
    "INFO": 0x0099ff,       # أزرق
    "NEUTRAL": 0x808080     # رمادي
}
'''
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ تم إنشاء ملف config.py")
        print("⚠️  يرجى تحديث DISCORD_TOKEN في الملف")
        return True
    except Exception as e:
        print(f"❌ فشل في إنشاء ملف config.py: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎵 مرحباً بك في إعداد بوت Discord الموسيقي!")
    print("=" * 50)
    
    # التحقق من Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 أو أحدث مطلوب")
        return
    
    print(f"✅ Python {sys.version.split()[0]} متوفر")
    
    # تثبيت المكتبات
    if not install_requirements():
        return
    
    # التحقق من FFmpeg
    if not check_ffmpeg():
        return
    
    # إنشاء ملف الإعدادات
    if not create_config():
        return
    
    print("\n🎉 تم الإعداد بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("1. اذهب إلى https://discord.com/developers/applications")
    print("2. أنشئ تطبيق جديد")
    print("3. انسخ رمز البوت (Token)")
    print("4. افتح ملف config.py واستبدل your_discord_bot_token_here")
    print("5. شغل البوت باستخدام: python music_bot.py")
    
    print("\n🚀 استمتع بالموسيقى!")

if __name__ == "__main__":
    main()
