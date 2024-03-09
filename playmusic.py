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
  voice_state  = message.author.voice

  # Check if the USER is in a voice channel
  if voice_state:
    # Check if the BOT is in a VC
    if message.guild.voice_client:
      # Check if the BOT is in a different voice channel
      if message.guild.voice_client.channel != voice_state.channel:
        embed = discord.Embed(
          title=":bangbang: ERROR :bangbang: ",
          description="You are not in a voice channel.",
          color=discord.Color.red()
        )
        return embed
      # Otherwise -> the BOT is in the same voice channel
      else: 
        # The BOT is in the same voice channel
        vc = message.guild.voice_client
    # Otherwise -> the BOT is NOT in a voice channel
    else:
      vc = await voice_state.channel.connect()

  # Search for and play the requested video
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    try:
      # Search for the video using YT dlp
      info = ydl.extract_info(f"ytsearch:{query}", download=False)
      # Retrives the first video that shows up from info
      #   If multiple entries come back -> retrieve the first entry
      #   Otherwise, only 1 entry exists -> retrieve its url
      video_info = info['entries'][0] if 'entries' in info else info
      title = video_info['title']
      url = video_info['url']
      thumbnail = video_info['thumbnails'][-1]['url']

      # Additional FFmpeg options
      ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
      }

      vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
      embed = discord.Embed(
        title=f":musical_note: Now playing:",
        description=title,
        color=discord.Color.fuchsia()
      )
      embed.set_image(url=thumbnail)
      return embed
    
    except youtube_dl.utils.DownloadError as e:
      print(f"{'*' * 30}\n[ERROR]:\n{e}")
      return await message.channel.send("Error: Unable to find or play the requested video.")
    
async def stopmusic(message):
  # Check if the bot is connected to a voice channel in the guild
  if message.guild.voice_client is not None:
    # Disconnect the bot from the voice channel
    await message.guild.voice_client.disconnect()

    # Create and send an embed message to indicate successful disconnection
    embed = discord.Embed(
      title="Disconnected",
      description="I've left the voice channel.",
      color=discord.Color.fuchsia()
    )
    await message.channel.send(embed=embed)
