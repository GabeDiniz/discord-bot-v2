import discord
from discord.ext import commands
# Requires:
# pip install yt_dlp
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
      # Search for the video using YT dlp
      info = ydl.extract_info(f"ytsearch:{query}", download=False)
      # Retrives the first video that shows up from info
      #   If multiple entries come back -> retrieve the first entry
      #   Otherwise, only 1 entry exists -> retrieve its url
      url = info['entries'][0]['url'] if 'entries' in info else info['url']

      # Additional FFmpeg options
      ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
      }

      vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
      return discord.Embed(
          title=f":musical_note: Now playing: {query}",
          color=discord.Color.fuchsia()
      )
      
    except youtube_dl.utils.DownloadError as e:
      print(f"{'*' * 30}\n[ERROR]:\n{e}")
      return await message.channel.send("Error: Unable to find or play the requested video.")