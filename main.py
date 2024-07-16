from discord import Intents, Client, app_commands
from discord.ext import commands
import discord   # pip install discord
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
import functions.qr_generator as qr

# Fetch Credentials from local .env variables 
# Constants
BOT_KEY = config('BOT_KEY')
knowledge: dict = responses.load_knowledge('./knowledge/knowledge2.json')

# Bot Constants
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) # Initialize bot

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
  embed.add_field(name='Play Music!', value='`!play <song-query>`', inline=False)
  embed.add_field(name='CS2 Stats', value='`!cs2 <name>`', inline=True)
  embed.add_field(name='Today\'s Fortnite Shop', value='`!fn-shop`', inline=True)
  embed.add_field(name='Create a QR', value='`!qr <link>`', inline=True)
  embed.add_field(name='Create polls!', value='`/poll <poll-query>`', inline=False)
        
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
  qr_code_file = qr.generate(message)
  if qr_code_file:
    with open(qr_code_file, 'rb') as f:
      image = discord.File(f)
      embed = discord.Embed(
        title='Created New QR',
        color=discord.Color.red()
      )
      embed.set_image(url=f"attachment://{qr_code_file}")
      await ctx.channel.send(file=image, embed=embed)
  else:
    await ctx.channel.send("Failed to generate QR code.")

@bot.tree.command(name="poll", description="Create a poll", guild=None)
async def poll_slash_command(interaction: discord.Interaction, question: str):
  await polls.create_poll(interaction, question)


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