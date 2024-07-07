from discord import Intents, Client
from discord.ext import commands
import discord   # pip install discord
# Used for retrieving BOT_KEY from .env
from decouple import config   # pip install python-decouple

# ========================================
# Response Features
# ========================================
import responses
import steam
import fortnite
import playmusic
import polls

# Fetch Credentials from local .env variables 
# Constants
BOT_KEY = config('BOT_KEY')
knowledge: dict = responses.load_knowledge('./knowledge/knowledge2.json')

# Bot Constants
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Start bot
@bot.event
async def on_ready():
  print(f"{bot.user} is now running!")


# ========================================
# CHAT RESPONSES
# ========================================
@bot.event
async def on_message(ctx):
  response = None   # Default Bot Response -> None
  # If Message is sent by a user
  if ctx.content and ctx.author != bot.user:
    print(f'[ {ctx.channel} ] {ctx.author}: "{ctx.content}"')

    # COMMAND: Basic text responses
    response: str = responses.get_response(ctx.content, knowledge=knowledge)
    if response:
      # Sending message
      await ctx.channel.send(response)


# ========================================
# COMMANDS
# ========================================
# Simple example command
@bot.command(name='hello')
async def hello_command(ctx):
  await ctx.send(f'Hello, {ctx.author.name}!')

@bot.command(name='commands')
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
  embed.add_field(name='Create polls!', value='`!poll <poll-query>`', inline=False)
        
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

@bot.command(name='poll')
async def poll_command(ctx, *, message: str = ""):
  await polls.create_poll(ctx, message, bot)


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


def run_bot():
  # Every time a new message appears -> handle msg
  @bot.event
  async def on_message(message):
    # Make sure the message being read is not from the bot
    if message.author == bot.user:
      return
    
    # ========================================
    # Handle Responses
    # ========================================
    # Check for specific user
    # if str(message.author) == "username here":
    #   response: str = "Oh hello there... I've been expecting you"
    
    
    # Potential error: i.e., missing permissions to access message.content
    else:
      print("[Error] Could not read the message. Make sure you have intents enabled!")

# Run the bot
bot.run(token=BOT_KEY)

if __name__ == "__main__":
  run_bot()