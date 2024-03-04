import discord
from discord.ext import commands
# Requires:
# pip install youtube_dl or pip install yt_dlp
# pip install pynacl
import yt_dlp as youtube_dl

# Define youtube_dl options
ydl_opts = {
  'format': 'bestaudio/best',
  'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
  }],
  'verbose': True
}

async def playmusic(message):
  query = message.content.strip("!play ")
  print(f"Query: {query}")
  voice = message.author.voice

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
    color=discord.Color.red()
    )
    return embed

  # Search for and play the requested video
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    try:
      info = ydl.extract_info(f"ytsearch:{query}", download=False)
      url = info['entries'][0]['url'] if 'entries' in info else info['url']
      # print(f"****YT Info: {info}")
      # print(f"****YT URL: {url}")
      vc.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Finished playing: {e}"))
    except youtube_dl.utils.DownloadError as e:
      print(f"{'*' * 30}\n[ERROR]:\n{e}")
      return await message.channel.send("Error: Unable to find or play the requested video.")