import asyncio
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
}

# Additional FFmpeg options
ffmpeg_options = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
  'options': '-vn'
}

# Global Dictionary -> Holds queue for each server
queue = {}  # Example: {"server-id": [[song1 info], [song2 info], [song3 info]]}  

def check_queue(client, message, guild_id):
  if queue[guild_id]:
    # Get next song
    song_info = queue[guild_id].pop(0)
    title = song_info['title']
    url = song_info['url']
    thumbnail = song_info['thumbnails'][-1]['url']

    # Send embed once song starts playing
    async def send_now_playing():
      embed = discord.Embed(
        title=f":musical_note: Now playing:",
        description=title,
        color=discord.Color.fuchsia()
      )
      embed.set_image(url=thumbnail)
      await message.channel.send(embed=embed)

    # Schedule the send_now_playing coroutine
    client.loop.create_task(send_now_playing())
    
    # Play the next song and set the callback to check_queue with updated parameters
    message.guild.voice_client.play(
      discord.FFmpegPCMAudio(url, **ffmpeg_options),
      after=lambda e: check_queue(client, message, guild_id)
    )


async def playmusic(message, client):
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
      info = ydl.extract_info(query if query.startswith("https://") else f"ytsearch:{query}", download=False)

      # Retrives the first video that shows up from info
      #   If multiple entries come back -> retrieve the first entry
      #   Otherwise, only 1 entry exists -> retrieve its url
      video_info = info['entries'][0] if 'entries' in info else info
      title = video_info['title']
      url = video_info['url']
      thumbnail = video_info['thumbnails'][-1]['url']

      # If BOT is already playing music
      if vc.is_playing():
        # If a queue already exists for that server
        if message.guild.id in queue:
          queue[message.guild.id].append(video_info)
        # Otherwise -> create new queue
        else:
          queue[message.guild.id] = [video_info]
        # Return QUEUE embed
        embed = discord.Embed(
          title=f":musical_note: Song added to queue...",
          color=discord.Color.fuchsia()
        )
        return embed
      else:
        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after = lambda e: check_queue(client, message, message.guild.id))

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
    return embed

async def skipsong(message, client):
  guild_id = message.guild.id   # Retrieve guild.id
  
  # Check if the bot is playing music
  if message.guild.voice_client is not None and message.guild.voice_client.is_playing():
    # Stop the current song
    message.guild.voice_client.stop()
    
    # Check if there are songs in the queue and play the next one
    if guild_id in queue and len(queue[guild_id]) > 0:
      embed = discord.Embed(
        title=":track_next: Skipping song",
        color=discord.Color.fuchsia()
      )
      await message.channel.send(embed=embed)
      # Check queue to play the next song
      check_queue(client, message, guild_id)
    else:
      # Otherwise, the queue is empty
      embed = discord.Embed(
        title=":musical_note: Queue is empty",
        description="Use `!play <query or url>` to play another song.",
        color=discord.Color.fuchsia()
      )
      await message.channel.send(embed=embed)
  else:
    # Create and send an embed message to indicate the bot is not playing music
    embed = discord.Embed(
      title=":bangbang: ERROR :bangbang: ",
      description="I am not currently in a voice channel",
      color=discord.Color.red()
    )
    await message.channel.send(embed=embed)