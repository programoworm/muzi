import discord
from discord.ext import commands,tasks
import youtube_dl as yt
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN=os.getenv("DISCORD_TOKEN")
yt.utils.bug_reports_message=lambda: ''
bot=commands.Bot(command_prefix='')

ytdl_format_options={
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options={
    'options': '-vn'
}

ytdl=yt.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data=data
        self.title=data.get('title')
        self.url=""
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data=data['entries'][0]
        file=data['title'] if stream else ytdl.prepare_filename(data)
        return file

@bot.event
async def on_ready():
	channel=bot.get_channel(578511881044754451)
	await channel.send('Hey, this is MUZI\n I was created by Programoworm')

@bot.command(name='p')
async def play(ctx,url):
	if not ctx.message.author.voice:
		await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
		return
	else:
		channel=ctx.message.author.voice.channel
		await channel.connect()
		server=ctx.message.guild
		voice=server.voice_client
		
		async with ctx.typing():
			file=await YTDLSource.from_url(url, loop=bot.loop)
			voice.play(discord.FFmpegPCMAudio(executable="ffmpeg",source=file))
		await ctx.send('**Playing:** {}'.format(file))
	#except:
	#	await ctx.send("The bot is not connected to a voice channel")

@bot.command(name='dc')
async def dc(ctx):
	voice=ctx.message.guild.voice_client
	if voice.is_connected():
		await voice.disconnect()
	else:
		await ctx.send("Muzi is currently not connected to any voice channel")
bot.run(TOKEN)
