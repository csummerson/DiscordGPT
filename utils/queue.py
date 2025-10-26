import asyncio
import discord
import yt_dlp
import random
from collections import defaultdict

guild_queues = defaultdict(list)
queue_locks = defaultdict(asyncio.Lock)

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -compression_level 10 -application audio'
}

ytdl_format_options = {
        'format': 'bestaudio[ext=webm][acodec=opus]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def extract_youtube_info(url: str):
    loop = asyncio.get_running_loop()
    try:
        info = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if not info:
            return None
        if "entries" in info and info["entries"]:
            info = info["entries"][0]

        formats = info.get("formats") or [info]
        stream_url = None
        for f in formats:
            if f.get("acodec") != "none" and f.get("protocol") != "sabr":
                stream_url = f.get("url")
                break
        if not stream_url:
            stream_url = info.get("url")

        return {
            "url": stream_url,
            "title": info.get("title", "Unknown Track"),
            "thumbnail": info.get("thumbnail"),
            "webpage": info.get("webpage_url") or url
        }
    except Exception as e:
        print(f"[Queue] yt_dlp extraction failed: {e}")
        return None


async def enqueue(bot, interaction, url, title=None):
    guild_id = interaction.guild.id
    should_start = False
    was_playing = False
    request_channel = interaction.channel
    request_user = interaction.user

    info = await extract_youtube_info(url)
    if info:
        url = info["url"] or url
        title = info.get("title", title or "Unknown Track")
    else:
        title = title or "Unknown Track"

    async with queue_locks[guild_id]:
        vc = interaction.guild.voice_client
        was_playing = bool(vc and vc.is_playing())

        guild_queues[guild_id].append((request_channel, request_user, url, title))
        if not was_playing:
            should_start = True

    if should_start:
        await play_next(bot, interaction.guild)

    return was_playing



async def play_next(bot, guild):
    guild_id = guild.id

    async with queue_locks[guild_id]:
        if not guild_queues[guild_id]:
            print(f"[Queue] Queue empty for guild {guild_id}")
            return
        channel, requester, url, title = guild_queues[guild_id].pop(0)

    vc = guild.voice_client
    if not vc:
        print(f"[Queue] No voice client for guild {guild_id}")
        return

    info = None
    if "youtube.com" in url or "youtu.be" in url or "http" in url:
        info = await extract_youtube_info(url)
        if not info:
            try:
                await channel.send(embed=discord.Embed(
                    description=f"Could not extract audio from: {url}",
                    color=0xFF0000))
            except Exception as e:
                print(f"[Queue] Failed to send extract error message: {e}")
            await play_next(bot, guild)
            return
        stream_url = info["url"]
        title = info.get("title", title or "Unknown Track")
        thumbnail = info.get("thumbnail")
        webpage = info.get("webpage")
    else:
        stream_url = url
        thumbnail = None
        webpage = url

    # sneaky little rick roll
    if random.random() < 0.01:
        r_info = await extract_youtube_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        if r_info:
            stream_url = r_info["url"]
            title = r_info.get("title", title)
            thumbnail = r_info.get("thumbnail")
            webpage = r_info.get("webpage")

    try:
        source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_opts)
    except Exception as e:
        print(f"[Queue] FFmpeg failed to open source: {e}")
        try:
            await channel.send(embed=discord.Embed(
                description="FFmpeg failed to open the audio source.",
                color=0xFF0000))
        except Exception:
            pass
       
        await play_next(bot, guild)
        return

    try:
        def after_playback(err):
            if err:
                print(f"[Queue] Playback error: {err}")
            
            try:
                asyncio.run_coroutine_threadsafe(play_next(bot, guild), bot.loop)
            except Exception as ex:
                print(f"[Queue] Failed to schedule next track: {ex}")

        vc.play(source, after=after_playback)
    except Exception as e:
        print(f"[Queue] Failed to start playback: {e}")
        await play_next(bot, guild)
        return

    print(f"[Queue] Now playing: {title}")

    embed = discord.Embed(
        title=f"Now Playing: {title}",
        description=f"[Open]({webpage})" if webpage else None,
        color=0x00FF00,
    )
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f"Requested by {getattr(requester, 'display_name', 'Unknown')}")

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[Queue] Failed to send now playing embed: {e}")


async def skip_track(guild):
    vc = guild.voice_client
    if vc and vc.is_playing():
        vc.stop()


async def stop_all(guild):
    guild_id = guild.id
    vc = guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
    async with queue_locks[guild_id]:
        guild_queues[guild_id].clear()


async def get_queue(guild):
    guild_id = guild.id
    async with queue_locks[guild_id]:
        return list(guild_queues[guild_id])
