import discord
from discord.ext import commands
import youtube_dl

def playmusic(message):
  async def play(message):
    query = message.strip("!play ")
    voice_channel = message.author.voice.channel
    if voice_channel:
      vc = await voice_channel.connect()
      await message.send(f'Connected to {voice_channel}')
    else:
      await message.send("You are not in a voice channel.")

    # Search for and play the requested video
    with youtube_dl.YoutubeDL() as ydl:
      info = ydl.extract_info(f"ytsearch:{query}", download=False)
      url = info['entries'][0]['url'] if 'entries' in info else info['url']
      vc.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Finished playing: {e}"))