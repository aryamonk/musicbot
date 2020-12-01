import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import asyncio

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='?')  #Prefix for commands for the Bot

status = ['?help', 'Playing music!', 'Europa']  #List of statuses the Bot randomly cycles through in its lifetime
queue = [] #Empty queue initialized so that we can store songs in it for later

@client.event
async def on_ready(): #This runs whenever the script of the Bot is run
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(member): #This runs every time a new member joins the server
    channel = discord.utils.get(member.guild.channels, name='bot')
    await channel.send(f'Welcome {member.mention} to the server! Type ?help for details on how to use the bot.')
        
@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency is: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['hello', 'Hello, whats up??', 'Hello, how are you?', 'Hi', 'Hey there!!']
    await ctx.send(choice(responses)) #'Choice' randomly selects a response and sends it as a reply to ?hello

@client.command(name='8ball', help='This command summons the magical 8 ball')
async def eightball(ctx):
    responses = ['It is certain', 'Without a doubt', 'Yes definitely', 'As I see it, yes', 'Signs point to yes', 'Concentrate and ask again','My reply is no','Better not tell you now','Outlook not so good','Very doubtful','Cannot predict now']
    await ctx.send(choice(responses))

@client.command(name='die', help='This command returns a random last words')
async def die(ctx):
    responses = ['why have you brought my short life to an end', 'i could have done so much more', 'i have a family, kill them instead']
    await ctx.send(choice(responses))

@client.command(name='diceroll', help='This command returns a random number from 1 to 6')
async def diceroll(ctx):
    responses = ['You rolled a 1!', 'You rolled a 2!', 'You rolled a 3!','You rolled a 4!', 'You rolled a 5!', 'You rolled a 6!']
    await ctx.send(choice(responses))

@client.command(name='spam', help='spam')
async def spam(ctx):
    responses = [f"hello, {ctx.author.mention}",f"hello how can i help you, {ctx.author.mention}",f"I have been summonned, {ctx.author.mention}",f"This is your punishment, {ctx.author.mention}",f"Is it ok if i ping you, {ctx.author.mention}?"]
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))
    await asyncio.sleep(0.2)
    await ctx.send(choice(responses))


@client.command(name='echo', help='This command returns the statement written after it as a reply')
async def echo(ctx, *, content:str):
    await ctx.send(content)

@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

@client.command(name='remove', help='This command removes an item from the list')
async def remove(ctx, number):
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')
    
    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')
        
@client.command(name='play', help='This command plays songs')
async def play(ctx, url):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))
    del(queue[0])

@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')

@client.command(name='leave', help='This command stops makes the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

@tasks.loop(seconds=20)
async def change_status(): #This lets the Bot change its status every 20 seconds
    await client.change_presence(activity=discord.Game(choice(status)))
client.run('TOKEN:') #This is a unique code that is confidential and should not be shared with people not working on this project.
