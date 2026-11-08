from __future__ import annotations

import asyncio

import discord   # pip install "discord.py[voice]"  (includes PyNaCl + davey for voice)
import yt_dlp    # pip install yt_dlp

# yt-dlp options: we only need the stream URL, nothing is downloaded
ydl_opts = {
  'format': 'bestaudio/best',
  'noplaylist': True,
  'quiet': True,
  'no_warnings': True,
}

# Additional FFmpeg options (reconnect keeps long streams from dying mid-song)
ffmpeg_options = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
  'options': '-vn'
}

# Global Dictionary -> Holds queue for each server
queue = {}  # Example: {guild_id: [{song1 info}, {song2 info}, {song3 info}]}


# ========================================
# Helpers
# ========================================
def _format_duration(seconds) -> str:
  '''Turns 185 -> "3:05", 3725 -> "1:02:05". Live streams have no duration.'''
  if not seconds:
    return "Live"
  seconds = int(seconds)
  hours, remainder = divmod(seconds, 3600)
  minutes, secs = divmod(remainder, 60)
  if hours:
    return f"{hours}:{minutes:02d}:{secs:02d}"
  return f"{minutes}:{secs:02d}"


def _error_embed(description: str) -> discord.Embed:
  return discord.Embed(
    title=":bangbang: E R R O R",
    description=description,
    color=discord.Color.red()
  )


def _now_playing_embed(song: dict) -> discord.Embed:
  embed = discord.Embed(
    title=":musical_note: Now playing:",
    description=song['title'],
    color=discord.Color.fuchsia()
  )
  embed.add_field(name='', value=f"Duration: `{song['duration']}`", inline=False)
  if song['thumbnail']:
    embed.set_image(url=song['thumbnail'])
  return embed


def _search(query: str) -> dict | None:
  '''
  Blocking yt-dlp lookup. Always call through asyncio.to_thread so the bot
  keeps responding (and current audio keeps playing) while it searches.
  '''
  search = query if query.startswith(("https://", "http://")) else f"ytsearch:{query}"
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(search, download=False)

  # Searches come back as a list of entries -> take the first result
  if 'entries' in info:
    entries = list(info['entries'])
    if not entries:
      return None
    info = entries[0]

  thumbnails = info.get('thumbnails') or []
  return {
    "title": info.get('title', 'Unknown title'),
    "url": info['url'],
    "thumbnail": thumbnails[-1]['url'] if thumbnails else None,
    "duration": _format_duration(info.get('duration')),
  }


def _start_playback(bot, guild, channel, song: dict):
  '''Plays a song and, when it ends (finished, skipped or stopped), moves on to the next one.'''
  def after_song(error):
    # discord.py calls this from its audio thread, not the bot's event loop,
    # so hand the work back to the loop in a thread-safe way.
    if error:
      print(f"[ ERROR ] Music player error in {guild.name}: {error}")
    asyncio.run_coroutine_threadsafe(_play_next(bot, guild, channel), bot.loop)

  guild.voice_client.play(discord.FFmpegPCMAudio(song['url'], **ffmpeg_options), after=after_song)


async def _play_next(bot, guild, channel):
  '''Plays the next queued song, if there is one.'''
  vc = guild.voice_client
  if vc is None or not vc.is_connected():
    queue.pop(guild.id, None)
    return
  if vc.is_playing() or vc.is_paused():
    return
  if not queue.get(guild.id):
    queue.pop(guild.id, None)
    return

  song = queue[guild.id].pop(0)
  try:
    _start_playback(bot, guild, channel, song)
  except discord.ClientException as e:
    print(f"[ ERROR ] Could not start next song in {guild.name}: {e}")
    return
  await channel.send(embed=_now_playing_embed(song))


# ========================================
# Commands
# ========================================
async def play_music(ctx, query: str, bot) -> discord.Embed:
  '''!play <query or url> -> plays immediately, or adds to the queue if something is already playing.'''
  voice_state = ctx.author.voice

  # Check if the USER is in a voice channel
  if not voice_state or not voice_state.channel:
    return _error_embed("You are not in a voice channel.")

  # Check if the BOT is in a different voice channel
  vc = ctx.guild.voice_client
  if vc and vc.channel != voice_state.channel:
    return _error_embed("You are not in the **correct** voice channel.")

  # Search for the requested video (off the event loop)
  async with ctx.typing():
    try:
      song = await asyncio.to_thread(_search, query)
    except Exception as e:
      print(f"{'*' * 30}\n[ ERROR ] yt-dlp failed for '{query}':\n{e}")
      return _error_embed("Unable to find or play the requested video.")

  if song is None:
    return _error_embed(f"No results found for **{query}**.")

  # Join the user's voice channel if the bot isn't connected yet
  vc = ctx.guild.voice_client
  if vc is None:
    vc = await voice_state.channel.connect(timeout=30, reconnect=True)

  # Something is already playing (or waiting to play) -> add to queue
  if vc.is_playing() or vc.is_paused() or queue.get(ctx.guild.id):
    queue.setdefault(ctx.guild.id, []).append(song)
    embed = discord.Embed(
      title=":musical_note: Song added to queue...",
      description=f"{song['title']} (`{song['duration']}`)",
      color=discord.Color.fuchsia()
    )
    embed.set_footer(text=f"Position in queue: {len(queue[ctx.guild.id])}")
    return embed

  _start_playback(bot, ctx.guild, ctx.channel, song)
  return _now_playing_embed(song)


async def leave_channel(ctx) -> discord.Embed:
  '''!leave -> clears the queue and disconnects.'''
  vc = ctx.guild.voice_client
  if vc is None:
    return _error_embed("I am not currently in a voice channel.")

  # Clear the queue first so the song-ended callback doesn't start the next song
  queue.pop(ctx.guild.id, None)
  await vc.disconnect()

  return discord.Embed(
    title=":mute: Disconnected",
    description="I've left the voice channel.",
    color=discord.Color.fuchsia()
  )


async def skip_song(ctx):
  '''!skip -> stops the current song; the song-ended callback starts the next one.'''
  vc = ctx.guild.voice_client
  if vc is None or not (vc.is_playing() or vc.is_paused()):
    await ctx.channel.send(embed=_error_embed("Nothing is playing right now."))
    return

  has_next = bool(queue.get(ctx.guild.id))
  vc.stop()   # Triggers after_song -> _play_next, which plays + announces the next song

  if has_next:
    embed = discord.Embed(
      title=":track_next: Skipping song",
      color=discord.Color.fuchsia()
    )
  else:
    embed = discord.Embed(
      title=":track_next: Skipped - queue is empty",
      description="Use `!play <query or url>` to play another song.",
      color=discord.Color.fuchsia()
    )
  await ctx.channel.send(embed=embed)
