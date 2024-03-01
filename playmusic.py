import discord
from discord.ext import commands
# Requires:
# pip install youtube_dl
# pip install pynacl
import youtube_dl  

async def playmusic(message):
  print("in function")
  

  query = message.content.strip("!play ")
  print(f"Message: {message}")
  print(f"User: {message.author}")
  print(f"VC?: {message.author.voice}")
  voice = message.author.voice
  print("here")

  # [SUCCESS] In a voice channel -> Connect to VC
  if voice:
    vc = await voice.channel.connect()
    embed = discord.Embed(
    title=f"Connected to {voice.channel}",
    description="Connected..",
    color=discord.Color.fuchsia()
    )

  # [ERROR] Not in voice channel -> Return Error
  else:
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