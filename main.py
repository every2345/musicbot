from pickle import TRUE
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from charaiPY.AsyncPyCAI2 import PyAsyncCAI2 # IMPORT THE LIB
import tls_client as tls # IMPORT LIB
import re
import random

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix='!', intents=intents) #Syntax for bot using command
music_queue = [] #Music queue to contain music list
authorized_users = []  #To save the user permission
pausemusic = False

owner_id = 'Owner_Token' # TOKEN 
char = "Char_ID" # CHAR ID
chat_id = "Chat_ID" # CHAT ID
client = PyAsyncCAI2(owner_id) # IMPORT OWNER ID
vol = 100 #default volume

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

#Play music Core.
async def play_music(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'audio-format': 'wav',
        'quiet': True,
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': True,
        'source_address': '0.0.0.0',
        'socket_timeout': 1000,
        'retries': 10,
        'retry_on_error': True,
        'hls_prefer_native': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav', 'preferredquality': '320'}],
        'no_warnings': True
         }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info.get('url')
        source = discord.FFmpegPCMAudio(URL, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

    voice_client = ctx.guild.voice_client
    if voice_client is not None: #Voice client still available
        if not voice_client.is_playing():
            voice_client.play(discord.PCMVolumeTransformer(source))
            player = voice_client.source
            player.volume = vol / 100
            await ctx.send(f'Đang chơi nhạc: {info["title"]} :minidisc:, âm lượng {vol}%')

        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(0.5)
        
        if len(music_queue) >= 0 and not pausemusic:
            music_queue.pop(0)  # Remove the currently playing song
            if len(music_queue) >= 0:
                await play_music(ctx, music_queue[0]['webpage_url'])  # Play the next song
            else:
                voice_client = ctx.guild.voice_client
                if voice_client is not None and voice_client.is_playing():
                    await voice_client.pause()
        else:
            voice_client = ctx.guild.voice_client
            if voice_client is not None and voice_client.is_playing():
                await voice_client.pause()
    else:
        await ctx.send("Bot chưa được mời vào kênh thoại...")

#Join command to invite bot join voice channel.
@bot.command()
async def join(ctx):
    voice_channel = getattr(ctx.author.voice, 'channel', None)
    if voice_channel is None:
        await ctx.send("Bạn cần kết nối tới kênh thoại trước khi mời bot!")
        return
    await voice_channel.connect()
    await ctx.send(f"Bot đã được mời vào kênh thoại: {voice_channel.name} Nya~~~")
    
#Command to show how to use bot.
@bot.command()
async def guide(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("Bot chưa được mời vào kênh thoại...")
        return
    else:
        await ctx.send('''Hướng dẫn sửa dụng bot và các lệnh cơ bản
- Lưu ý: Bạn phải cấp quyền người dùng chỉ định cho bot để có thể sử dụng các lệnh.
- Thông tin các lệnh hiện tại của bot:
- !chat: Sử dụng để trò chuyện tới mình ₍^ >ヮ<^₎                       
- !join: Sử dụng để mời bot vào kênh thoại.
- !permission <id user>: Sử dụng để cấp quyền sử dụng bot cho một người dùng chỉ định
- !play <link youtubbe>: Sử dụng để chơi nhạc thông qua địa chỉ video youtube được chỉ định
- !show: Sử dụng để xem tất cả các bài nhạc đang nằm trong playlist
- !clear: Sử dụng để xóa tất cả nhạc trong playlist
- !skip: Sử dụng để chuyển sang bài nhạc tiếp theo trong playlist 
- !volume: Tăng giảm âm ượng bài nhạc đang phát hiện tại (Giới hạn âm lượng 0 - 100)
- !pause: Tạm dừng bài nhạc đang phát
- !resume: Tiếp tục bài nhạc đang phát
- !shuffle: Trộn danh sách phát nhạc                       
- !stop: Dừng nhạc và thoát bỏ (khuyến nghị sử dụng khi không còn xài bot nữa)''')

#command to permission who can use this bot
@bot.command()
async def permission(ctx, member: commands.MemberConverter):
    if not member:
        await ctx.send("Không tìm thấy người dùng.")
        return

    if member.id == ctx.author.id:  # Kiểm tra nếu người dùng yêu cầu tự ủy quyền cho chính họ
        if member not in authorized_users:
            authorized_users.append(member)
            await ctx.send(f"{member.name} đã tự ủy quyền cho chính mình để sử dụng bot.")
        else:
            await ctx.send(f"{member.name} đã được tự ủy quyền sử dụng bot từ trước đó.")
        return

    if member in authorized_users:
        await ctx.send(f"{member.name} đã được ủy quyền để sử dụng bot.")
        return

    if authorized_users:
        old_user = authorized_users.pop()
        await ctx.send(f"{old_user.name} đã bị gỡ bỏ quyền ủy quyền sử dụng bot.")

    authorized_users.append(member)
    await ctx.send(f"{member.name} đã được ủy quyền để sử dụng bot.")
    
@bot.command()
async def chat(ctx, *, message: str):
    # The message will be obtained from the command parameters rather than input
    author_id = str(ctx.author.id)  # Get the author's ID from the context
    message_content = message

    aut_set ={
        "author_id": "Creator_ID", # CREATOR ID
        "is_human": True,
        "name": "<WRITE YOUR C.AI NAME>"
    }

    async with client.connect(owner_id) as chat2:
        r = await chat2.send_message(char, chat_id, message_content, aut_set, Return_name=True)
        # Send message content obtained from the command
        # Print the response
        await ctx.send(r[16:])

#command "!play" to play the music 
@bot.command()
async def play(ctx, url):
    # Check if the URL is a valid YouTube playlist
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if re.match(r'^https?://(?:www\.)?(?:youtube\.com/playlist\?list=)([\w-]+)', url):
        await handle_playlist(ctx, url)
    elif re.match(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', url):
        await handle_song(ctx, url)
    else:
        await ctx.send("Cú pháp không hợp lệ. Vui lòng nhập một liên kết YouTube hợp lệ. Đếu đây là dang sách, hãy kiểm tra xem dang sách đó có công khai hay không?")
        
#function to play list
async def handle_playlist(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'audio-format': 'wav',
        'quiet': True,
        'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        for entry in playlist_info['entries']:
            music_queue.append(entry)

    if len(music_queue) > 0:
        await play_music(ctx, music_queue[0]['webpage_url'])
    else:
        await ctx.send(f'Danh sách nhạc "{playlist_info["title"]}" đã được thêm vào hàng đợi.')

#function to play single song
async def handle_song(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'audio-format': 'wav',
        'quiet': True,
        'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        music_queue.append(info)

    if len(music_queue) > 0:
        await play_music(ctx, info['webpage_url'])
    else:
        await ctx.send(f'Bài nhạc "{info["title"]}" đã được thêm vào hàng đợi.')
        
#Command "!pause" to pause the current music playing
@bot.command()
async def pause(ctx):
    global pausemusic 
    
    pausemusic = True
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Bài nhạc đã được tạm dừng.")
    else:
        await ctx.send("Bot không đang phát bài nhạc.")
        
#Command "!resume" to continue the current music playing
@bot.command()
async def resume(ctx):
    global pausemusic 
    
    pausemusic = False
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return


    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Bài nhạc đã được tiếp tục.")
        await play_music(ctx, music_queue[0]['webpage_url']) 
    else:
        await ctx.send("Bot đang không bị tạm dừng.")

#command "!show" to show all music availabel in queue
@bot.command()
async def show(ctx):
    
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if len(music_queue) == 0:
        await ctx.send("Hàng đợi đang trống")
    else:
        queue_msg = "Hàng đợi hiện tại:\n"
        for i, song in enumerate(music_queue):
            queue_msg += f"{i+1}. {song['title']} - {song['uploader']} ({song['duration']})\n"
        await ctx.send(queue_msg)

#command "!shuffle" to shuffle music playlist
@bot.command()
async def shuffle(ctx):
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if len(music_queue) < 1:
        await ctx.send("Cần ít nhất 2 bài nhạc để trộn.")
        return

    random.shuffle(music_queue)
    await ctx.send("Đã trộn ngẫu nhiên thứ tự các bài nhạc trong hàng đợi.")

#Command "!clear" to clear all music in queue
@bot.command()
async def clear(ctx):
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    global music_queue
    if len(music_queue) > 1:
        music_queue = music_queue[:1]
        await ctx.send("Hàng đợi nhạc đã được xóa.")
    elif voice_client and voice_client.is_playing():
        music_queue = []
        voice_client.stop()
        await ctx.send("Đang phát nhạc hiện tại đã bị dừng và hàng đợi nhạc đã được xóa.")
    else:
        music_queue = []
        await ctx.send("Không có bài hát nào trong hàng đợi.")

#Command "!skip" to foward next music in queue
@bot.command()
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if voice_client.is_playing():
        if len(music_queue) >= 0:
            voice_client.pause()
            await ctx.send("Bot đã chuyển sang bài nhạc khác trong hàng đợi.")
            music_queue.pop(0)
            if len(music_queue) >= 0:
                next_song_info = music_queue[0]
                await play_music(ctx, next_song_info['webpage_url'])
        else:
            await ctx.send("Hết bài nhạc trong hàng đợi.")
            
    elif len(music_queue) > 0:
        next_song_info = music_queue[0]
        await play_music(ctx, next_song_info['webpage_url']) 
    else:
        await ctx.send("Hàng đợi nhạc rỗng.")

#Command "!volume" to change the music volume
@bot.command()        
async def volume(ctx, volume: int):
    global vol 
    if not 0 <= volume <= 100:
        await ctx.send("Giá trị âm lượng không hợp lệ. Vui lòng nhập giá trị từ 0 đến 100.")
        return
    
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return
    
    if voice_client and voice_client.is_playing():
        player = voice_client.source
        if not isinstance(player, discord.PCMVolumeTransformer):
            voice_client.source = discord.PCMVolumeTransformer(player)
            player = voice_client.source
        player.volume = volume / 100
        vol = volume
        await ctx.send(f"Đã thiết lập âm lượng của bài nhạc thành {vol}%")
    else:
        await ctx.send("Không có bài nhạc đang được chơi trên voice channel")


#Command "!stop" to stop and bot will exit voice channel
@bot.command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if ctx.author not in authorized_users:
        await ctx.send(f"{ctx.author.mention}, bạn không được phép sử dụng lệnh này.")
        return

    if voice_client.is_paused() or not voice_client.is_playing():
        voice_client.stop()
        await voice_client.disconnect()
        await ctx.send("Bot đã ngừng phát nhạc và đi ngủ đây Nya~~~.")
  
    else:
        await ctx.send("Bạn cần dừng bài nhạc hiện đang chơi để sử dụng lệnh này!")

#Token of this bot
bot.run('Bot_Token')
