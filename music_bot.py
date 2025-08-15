import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import config

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# إعدادات yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}

# قائمة قوائم التشغيل لكل خادم
playlists = {}

class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.current_song = None
        self.voice_client = None
        self.is_playing = False
        self.loop = False

    async def add_to_queue(self, url, ctx):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'title': info.get('title', 'أغنية غير معروفة'),
                    'url': url,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'requester': ctx.author
                }
                self.queue.append(song_info)
                return song_info
        except Exception as e:
            print(f"خطأ في استخراج معلومات الفيديو: {e}")
            print(f"URL: {url}")
            return None

    async def play_next(self):
        if self.queue and self.voice_client and self.voice_client.is_connected():
            self.current_song = self.queue.pop(0)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.current_song['url'], download=False)
                    audio_url = info.get('url')
                    if audio_url:
                        try:
                            # محاولة استخدام FFmpeg
                            self.voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), bot.loop))
                            self.is_playing = True
                            print(f"✅ تم تشغيل: {self.current_song['title']}")
                        except Exception as play_error:
                            print(f"خطأ في تشغيل الأغنية: {play_error}")
                            # محاولة ثانية مع خيارات مختلفة
                            try:
                                self.voice_client.play(discord.FFmpegPCMAudio(audio_url, options='-vn'), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), bot.loop))
                                self.is_playing = True
                                print(f"✅ تم تشغيل (محاولة ثانية): {self.current_song['title']}")
                            except Exception as e2:
                                print(f"فشل في تشغيل الأغنية: {e2}")
                                await self.play_next()
                    else:
                        print("لم يتم العثور على رابط الصوت")
                        await self.play_next()
            except Exception as e:
                print(f"خطأ في تشغيل الأغنية: {e}")
                await self.play_next()

# إنشاء قائمة قوائم التشغيل
def get_player(guild_id):
    if guild_id not in playlists:
        playlists[guild_id] = MusicPlayer()
    return playlists[guild_id]

@bot.event
async def on_ready():
    print(f'✅ {bot.user} تم تسجيل الدخول بنجاح!')
    await bot.change_presence(activity=discord.Game(name=config.BOT_STATUS))

@bot.command(name='join')
async def join(ctx):
    """🎧 الانضمام إلى قناة الصوت"""
    if ctx.author.voice is None:
        embed = discord.Embed(
            title="❌ خطأ",
            description="يجب أن تكون في قناة صوتية أولاً!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    channel = ctx.author.voice.channel
    try:
        voice_client = await channel.connect()
        player = get_player(ctx.guild.id)
        player.voice_client = voice_client
        
        embed = discord.Embed(
            title="🎧 تم الانضمام",
            description=f"تم الانضمام إلى {channel.name} بنجاح!",
            color=config.COLORS["SUCCESS"]
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ",
            description=f"فشل في الانضمام: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='play')
async def play(ctx, url):
    """▶️ تشغيل أغنية من رابط YouTube"""
    if ctx.author.voice is None:
        embed = discord.Embed(
            title="❌ خطأ",
            description="يجب أن تكون في قناة صوتية أولاً!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    player = get_player(ctx.guild.id)
    
    # الانضمام إذا لم يكن البوت متصل
    if not player.voice_client or not player.voice_client.is_connected():
        channel = ctx.author.voice.channel
        try:
            voice_client = await channel.connect()
            player.voice_client = voice_client
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"فشل في الانضمام: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

    # إضافة الأغنية إلى القائمة
    song_info = await player.add_to_queue(url, ctx)
    if song_info:
        embed = discord.Embed(
            title="🎵 تمت الإضافة",
            description=f"**{song_info['title']}**\nتمت الإضافة إلى قائمة التشغيل",
            color=config.COLORS["SUCCESS"]
        )
        embed.set_thumbnail(url=song_info['thumbnail'])
        embed.add_field(name="المدة", value=f"{song_info['duration']//60}:{song_info['duration']%60:02d}", inline=True)
        embed.add_field(name="طلب بواسطة", value=song_info['requester'].mention, inline=True)
        await ctx.send(embed=embed)

        # تشغيل إذا لم تكن هناك أغنية تعمل
        if not player.is_playing:
            await player.play_next()
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="فشل في استخراج معلومات الأغنية",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='pause')
async def pause(ctx):
    """⏸️ إيقاف الأغنية مؤقتاً"""
    player = get_player(ctx.guild.id)
    if player.voice_client and player.voice_client.is_playing():
        player.voice_client.pause()
        player.is_playing = False
        
        embed = discord.Embed(
            title="⏸️ تم الإيقاف المؤقت",
            description="تم إيقاف الأغنية مؤقتاً",
            color=config.COLORS["WARNING"]
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="لا توجد أغنية تعمل حالياً",
            color=config.COLORS["ERROR"]
        )
        await ctx.send(embed=embed)

@bot.command(name='resume')
async def resume(ctx):
    """▶️ استئناف الأغنية"""
    player = get_player(ctx.guild.id)
    if player.voice_client and player.voice_client.is_paused():
        player.voice_client.resume()
        player.is_playing = True
        
        embed = discord.Embed(
            title="▶️ تم الاستئناف",
            description="تم استئناف الأغنية",
            color=config.COLORS["SUCCESS"]
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="لا توجد أغنية متوقفة مؤقتاً",
            color=config.COLORS["ERROR"]
        )
        await ctx.send(embed=embed)

@bot.command(name='stop')
async def stop(ctx):
    """⏹️ إيقاف الأغنية"""
    player = get_player(ctx.guild.id)
    if player.voice_client:
        player.voice_client.stop()
        player.is_playing = False
        player.current_song = None
        
        embed = discord.Embed(
            title="⏹️ تم الإيقاف",
            description="تم إيقاف الأغنية",
            color=config.COLORS["ERROR"]
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="البوت غير متصل بقناة الصوت",
            color=config.COLORS["ERROR"]
        )
        await ctx.send(embed=embed)

@bot.command(name='skip')
async def skip(ctx):
    """⏭️ تخطي الأغنية الحالية"""
    player = get_player(ctx.guild.id)
    if player.voice_client and player.is_playing:
        player.voice_client.stop()
        embed = discord.Embed(
            title="⏭️ تم التخطي",
            description="تم تخطي الأغنية الحالية",
            color=config.COLORS["SUCCESS"]
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="لا توجد أغنية تعمل حالياً",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='queue')
async def queue(ctx):
    """📋 عرض قائمة التشغيل"""
    player = get_player(ctx.guild.id)
    
    if not player.queue and not player.current_song:
        embed = discord.Embed(
            title="📋 قائمة التشغيل فارغة",
            description="لا توجد أغاني في قائمة التشغيل",
            color=config.COLORS["NEUTRAL"]
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="📋 قائمة التشغيل",
        color=config.COLORS["SUCCESS"]
    )

    # الأغنية الحالية
    if player.current_song:
        embed.add_field(
            name="🎵 الآن تعمل:",
            value=f"**{player.current_song['title']}**\nطلب بواسطة: {player.current_song['requester'].mention}",
            inline=False
        )

    # قائمة الانتظار
    if player.queue:
        queue_text = ""
        for i, song in enumerate(player.queue[:10], 1):
            queue_text += f"{i}. **{song['title']}** - {song['requester'].mention}\n"
        
        if len(player.queue) > 10:
            queue_text += f"\n... و {len(player.queue) - 10} أغنية أخرى"
        
        embed.add_field(
            name=f"⏭️ قائمة الانتظار ({len(player.queue)} أغنية):",
            value=queue_text,
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='leave')
async def leave(ctx):
    """🚪 مغادرة قناة الصوت"""
    player = get_player(ctx.guild.id)
    if player.voice_client and player.voice_client.is_connected():
        await player.voice_client.disconnect()
        player.voice_client = None
        player.is_playing = False
        player.current_song = None
        player.queue.clear()
        
        embed = discord.Embed(
            title="🚪 تم المغادرة",
            description="تم مغادرة قناة الصوت",
            color=config.COLORS["ERROR"]
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ خطأ",
            description="البوت غير متصل بقناة صوتية",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='clear')
async def clear(ctx):
    """🗑️ مسح قائمة التشغيل"""
    player = get_player(ctx.guild.id)
    player.queue.clear()
    
    embed = discord.Embed(
        title="🗑️ تم المسح",
        description="تم مسح قائمة التشغيل",
        color=config.COLORS["SUCCESS"]
    )
    await ctx.send(embed=embed)

@bot.command(name='loop')
async def loop(ctx):
    """🔁 تفعيل/إلغاء التكرار"""
    player = get_player(ctx.guild.id)
    player.loop = not player.loop
    
    status = "مفعل" if player.loop else "ملغي"
    color = config.COLORS["SUCCESS"] if player.loop else config.COLORS["ERROR"]
    
    embed = discord.Embed(
        title="🔁 التكرار",
        description=f"تم {status} التكرار",
        color=color
    )
    await ctx.send(embed=embed)

@bot.command(name='test')
async def test(ctx):
    """🧪 اختبار البوت"""
    embed = discord.Embed(
        title="🧪 اختبار البوت",
        description="البوت يعمل بشكل طبيعي! ✅",
        color=config.COLORS["SUCCESS"]
    )
    await ctx.send(embed=embed)

@bot.command(name='music_help')
async def help_command(ctx):
    """❓ عرض قائمة الأوامر"""
    embed = discord.Embed(
        title="🎵 بوت الموسيقى - قائمة الأوامر",
        description="جميع الأوامر المتاحة لاستخدام البوت",
        color=config.COLORS["SUCCESS"]
    )
    
    commands_list = [
        ("🎧 !join", "الانضمام إلى قناة الصوت"),
        ("▶️ !play <رابط>", "تشغيل أغنية من YouTube"),
        ("⏸️ !pause", "إيقاف الأغنية مؤقتاً"),
        ("▶️ !resume", "استئناف الأغنية"),
        ("⏹️ !stop", "إيقاف الأغنية"),
        ("⏭️ !skip", "تخطي الأغنية الحالية"),
        ("📋 !queue", "عرض قائمة التشغيل"),
        ("🚪 !leave", "مغادرة قناة الصوت"),
        ("🗑️ !clear", "مسح قائمة التشغيل"),
        ("🔁 !loop", "تفعيل/إلغاء التكرار"),
        ("❓ !help", "عرض هذه القائمة")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="🎵 استمتع بالموسيقى!")
    await ctx.send(embed=embed)

# تشغيل البوت
if __name__ == "__main__":
    TOKEN = config.DISCORD_TOKEN
    if TOKEN == "your_discord_bot_token_here":
        print("❌ خطأ: يرجى تحديث DISCORD_TOKEN في ملف config.py")
        print("احصل على رمز البوت من: https://discord.com/developers/applications")
    else:
        bot.run(TOKEN)
