from discord import Intents, Client, app_commands
from discord.ext import commands
import discord   # pip install discord
import openai  # pip install openai
import os

# Used for retrieving BOT_KEY from .env
from decouple import config   # pip install python-decouple

# ========================================
# Response Features
# ========================================
import functions.responses as responses
import functions.steam as steam
import functions.fortnite as fortnite
import functions.playmusic as playmusic
import functions.polls as polls
import functions.events as events
import functions.qr_generator as qr
import functions.get_gif as gifs

# Fetch Credentials from local .env variables 
# Constants
BOT_KEY = config('BOT_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')
knowledge: dict = responses.load_knowledge('./knowledge/knowledge2.json')

# Bot Constants
intents = Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) # Initialize bot
gptClient = openai.OpenAI(api_key=OPENAI_API_KEY)

# Start bot
@bot.event
async def on_ready():
  await bot.tree.sync()
  print(f"{bot.user} is now running!")


# ========================================
# COMMANDS
# ========================================
# Simple example command
@bot.command(name='hello')
async def hello_command(ctx):
  await ctx.send(f'Hello, {ctx.author.name}!')

@bot.command(name='help')
async def help_command(ctx):
  embed = discord.Embed(
    # title='Cpt. Bot Commands',
    color=discord.Color.red()
  )
  # Add fields to the embed (optional)
  embed.set_author(name="King Bob's Commands", url="https://github.com/GabeDiniz", icon_url="https://imgur.com/nH32raP.png")
  embed.set_thumbnail(url="https://i.imgur.com/nH32raP.png")
  embed.add_field(name='See Music Commands', value='`!help-music`', inline=False)
  embed.add_field(name='CS2 Stats', value='`!cs2 <name>`', inline=True)
  embed.add_field(name='Today\'s Fortnite Shop', value='`!fn-shop`', inline=True)
  embed.add_field(name='Create a QR', value='Color-code should be in Hex format (#FFFFFF)\n`!qr <link> <optional: fg-color> <optional: bg-color>`', inline=False)
  embed.add_field(name='Random GIF', value='`!gif`', inline=True)
  embed.add_field(name='Create polls!', value='`/poll`', inline=True)
  embed.add_field(name='Create events!', value='`/event`', inline=True)
        
  # Send the embed message to the same channel where the command was issued
  await ctx.channel.send(embed=embed)

@bot.command(name='help-music')
async def help_command(ctx):
  embed = discord.Embed(
    color=discord.Color.red()
  )
  embed.set_author(name="Music Commands", url="https://github.com/GabeDiniz", icon_url="https://imgur.com/nH32raP.png")
  embed.set_thumbnail(url="https://i.imgur.com/nH32raP.png")
  embed.add_field(name='Play or queue a song', value='`!play <song-query>`', inline=False)
  embed.add_field(name='Skip current song', value='`!skip`', inline=False)
  embed.add_field(name='Kick bot from VC', value='`!leave`', inline=False)

  # Send the embed message to the same channel where the command was issued
  await ctx.channel.send(embed=embed)


@bot.command(name='cs2')
async def steam_command(ctx, *, message: str):
  embed = steam.get_user_stats(ctx, message)
  await ctx.channel.send(embed=embed)
  
@bot.command(name='fn-shop')
async def play_command(ctx):
  embed = fortnite.get_shop_items()
  await ctx.channel.send(embed=embed)

@bot.command(name='qr')
async def play_command(ctx, *, message: str):
  qr_code_file = qr.generate(message)   # Returns QR file
  if qr_code_file:
    with open(qr_code_file, 'rb') as f:   # Open in Binary format
      image = discord.File(f)
      embed = discord.Embed(
        title='Created New QR',
        color=discord.Color.red()
      )
      embed.set_image(url=f"attachment://{qr_code_file}")
      await ctx.channel.send(file=image, embed=embed)
  else:
    await ctx.channel.send("Failed to generate QR code.")
  os.remove("qr.png")

@bot.command(name='gif')
async def play_command(ctx):
  gif = gifs.random_gif()
  await ctx.channel.send(gif)

# WIP: NO FUNCTIONING AS IT COSTS MONEY
@bot.command(name='gpt')
async def chatgpt(ctx, *, query: str):
  await ctx.typing()  # Show typing indicator while processing

  try:
    response = gptClient.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": query}
      ]
    )
    print(response)
    answer = response.choices[0].message
    await ctx.send(answer)
  except Exception as e:
    await ctx.send(f"An error occurred: {e}")


@bot.tree.command(name="poll", description="Create a poll", guild=None)
async def poll_slash_command(interaction: discord.Interaction, question: str):
  await polls.create_poll(interaction, question)

@bot.tree.command(name="event", description="Create an event", guild=None)
@app_commands.describe(date="Date of the event (YYYY-MM-DD)", time="Event time (HH:MM, 24-hour format)", description="Description of event")
async def create_event(interaction: discord.Interaction, date: str, time: str, description: str):
  await events.create_event(interaction, date, time, description)
# @bot.event
# async def on_reaction_add(reaction, user):
#   await events.on_reaction_add(reaction, user)


# ========================================
# PLAY MUSIC
# ========================================
@bot.command(name='play')
async def play_command(ctx, *, message: str):
  print(ctx)
  embed = await playmusic.play_music(ctx, message, bot)
  await ctx.channel.send(embed=embed)

@bot.command(name='leave')
async def leave_command(ctx):
  embed = await playmusic.leave_channel(ctx)
  await ctx.channel.send(embed=embed)

@bot.command(name='skip')
async def skip_command(ctx):
  await playmusic.skip_song(ctx, bot) 


# ========================================
# CHAT RESPONSES
# ========================================
@bot.event
async def on_message(ctx):
  print(f"USER: {ctx.author}")
  # [TESTING] Check for messages sent by a specific user
  # if str(ctx.author) == "emili03x":
  #   response: str = "msg here"
  # elif str(ctx.author) == "<@206888163875094528>" or str(ctx.author) == "@206888163875094528" or str(ctx.author) == "rickeydickey":
  #   response: str = "msg here"

  if ctx.content and ctx.author != bot.user:
    print(f'[ {ctx.channel} ] {ctx.author}: "{ctx.content}"')
    response = responses.get_response(ctx.content, knowledge=knowledge)
    if response:
      await ctx.channel.send(response)

  # Process commands if they are present
  await bot.process_commands(ctx)


# ========================================
# RUN BOT
# ========================================
bot.run(token=BOT_KEY)