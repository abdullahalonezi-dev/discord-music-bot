#!/usr/bin/env python3
"""
أداة إضافة بوت Discord للخادم
"""

def create_bot_invite():
    """إنشاء رابط دعوة البوت"""
    print("🎵 مرحباً بك في أداة إضافة البوت!")
    print("=" * 50)
    
    # طلب Client ID
    client_id = input("📝 أدخل Client ID الخاص بك: ").strip()
    
    if not client_id:
        print("❌ يجب إدخال Client ID")
        return
    
    # الصلاحيات المطلوبة
    permissions = "3148800"  # Send Messages, Connect, Speak, Embed Links, Attach Files
    
    # إنشاء الرابط
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"
    
    print("\n🎉 تم إنشاء رابط الدعوة!")
    print("=" * 50)
    print(f"🔗 الرابط: {invite_url}")
    print("\n📋 الخطوات التالية:")
    print("1. انسخ الرابط أعلاه")
    print("2. افتحه في المتصفح")
    print("3. اختر خادمك")
    print("4. اضغط 'Authorize'")
    print("5. تأكد من الصلاحيات المطلوبة")
    print("6. اضغط 'Authorize' مرة أخرى")
    
    print("\n✅ تم إضافة البوت بنجاح!")
    print("🎵 الآن يمكنك تشغيل البوت باستخدام: python music_bot.py")

if __name__ == "__main__":
    create_bot_invite()
