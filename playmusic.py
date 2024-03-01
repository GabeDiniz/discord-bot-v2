import discord
from discord.ext import commands
import youtube_dl

def playmusic(message):
  print("in function")
  
  query = message.content.strip("!play ")
  print(f"Message: {message}")
  print(f"User: {message.author}")
  print(f"VC?: {message.author.voice}")
  voice = message.author.voice
  print("here")
  if voice:
    print("in VCCCC")
    vc = voice.channel.connect()
    message.send(f'Connected to {voice.channel}')
  # [ERROR] Not in voice channel -> Return Error
  else:
    print("here2")
    embed = discord.Embed(
    title=":bangbang: ERROR :bangbang: ",
    description="You are not in a voice channel.",
    color=discord.Color.fuchsia()
    )
    return embed

  # Search for and play the requested video
  with youtube_dl.YoutubeDL() as ydl:
    info = ydl.extract_info(f"ytsearch:{query}", download=False)
    url = info['entries'][0]['url'] if 'entries' in info else info['url']
    vc.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Finished playing: {e}"))