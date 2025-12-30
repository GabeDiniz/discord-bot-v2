import json
from discord import Intents, Client, app_commands
from discord.ext import commands, tasks    # pip install discord-ext-bot
import discord   # pip install discord
import openai  # pip install openai
import os
import requests
from transformers import pipeline  # pip install transformers
import argparse

# Used for retrieving BOT_KEY from .env
from decouple import config

# ========================================
# Response Features
# ========================================
import functions.responses as responses
import functions.steam as steam
import functions.fortnite as fortnite
import functions.playmusic as playmusic
import functions.events as events
import functions.qr_generator as qr
import functions.get_gif as gifs
import functions.sport_details as sport_details
import functions.currency_conversion as currency

# Fetch Credentials from local .env variables
# Constants
BOT_KEY = config('BOT_KEY')
# OPENAI_API_KEY = config('OPENAI_API_KEY')
HUGGING_FACE_API_URL = "https://router.huggingface.co/together/v1/chat/completions"
HF_HEADER = {"Authorization": f"Bearer {config('HUGGING_FACE_API_KEY')}"}

# Load Knowledge Base
try:
  knowledge: dict = responses.load_knowledge('./resources/knowledge2.json')
except FileNotFoundError:
  knowledge: dict = responses.load_knowledge('./resources/knowledge.json')
  print("[ WARN ] Knowledge 2 file not found, using base knowledge.")

# Bot Constants
intents = Intents.default()
intents.message_content = True
intents.voice_states = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) # Initialize bot
# gptClient = openai.OpenAI(api_key=OPENAI_API_KEY)

# Argument Parser for CLI flags
parser = argparse.ArgumentParser()
parser.add_argument('--testing', action='store_true', help='Enable testing mode')
args = parser.parse_args()
TESTING_MODE = args.testing
print("[ LOG ] Testing Mode is", "ON" if TESTING_MODE else "OFF")
ON_START = True # Used to prevent certain actions on bot restart

# Start bot
@bot.event
async def on_ready():
  load_wishlist()
  await steam_sale.start()  # Enable/disable Steam sale notification
  await bot.tree.sync()
  print(f"{bot.user} is now running!")

# ========================================
# FUNCTIONS
# ========================================
def save_wishlist():
  global server_wishlists
  # Relative path to the file
  file_path = os.path.join('resources', 'wishlist.json')
  with open(file_path, 'w') as f:
    json.dump(server_wishlists, f)
  print("[ SAVED ] Wishlist saved successfully")

def save_default_channel():
  '''Set the server's default text channel based on where the !addwishlist command was run.'''
  global default_channel
  # Relative path to the file
  file_path = os.path.join('resources', 'default_channel.json')
  with open(file_path, 'w') as f:
    json.dump(default_channel, f)
    print("[ SAVED ] Default wishlist channel saved successfully")

def load_wishlist():
  '''Load wishlist if existing, create a new one if none available.'''
  global server_wishlists
  global default_channel
  try:
    print("[ LOG ] Loading Server Wishlist...")
    # Relative path to the file
    file_path = os.path.join('resources', 'wishlist.json')
    with open(file_path, 'r') as f:
      server_wishlists = json.load(f)
    print("[ LOG ] LOADED existing Wishlist")

    print("[ LOG ] Loading channel data...")
    # Relative path to the file
    file_path = os.path.join('resources', 'default_channel.json')
    with open(file_path, 'r') as f:
      default_channel = json.load(f)
    print("[ LOG ] LOADED channel data")
  except FileNotFoundError:
    print("[ LOG ] wishlist.json or default_channel.json not found, starting with an empty wishlist.")
    server_wishlists = {}
    default_channel = {}


@tasks.loop(hours=24)
async def steam_sale():
  if ON_START:
    print("[ ON START ] Don't check for sales on bot start")
    ON_START = False
    return
  if TESTING_MODE:
    print("[ LOG ] Loop-task: TESTING MODE - Skipping steam sale check")
  else:
    print("[ LOG ] Loop-task: checking for server steam wishlist sale")
    await steam.check_sale(bot, server_wishlists, default_channel)

@steam_sale.before_loop
async def before_check_sales():
  '''Ensure the bot is ready before starting the steam_sale loop'''
  await bot.wait_until_ready()

# ========================================
# ! COMMANDS
# ========================================
# Simple example command
@bot.command(name="hello", description="Example command for easy copying and pasting.")
async def hello_command(ctx):
  await ctx.send(f'Hello, {ctx.author.name}!')

# #####################
@bot.command(name="help", description="Displays the bot's available commands.")
async def help_command(ctx):
  embed = discord.Embed(
    # title='Cpt. Bot Commands',
    color=discord.Color.red()
  )
  # Add fields to the embed (optional)
  embed.set_author(name="King Bob's Commands", url="https://github.com/GabeDiniz", icon_url="https://i.imgur.com/WcdJrv4.png")
  embed.set_thumbnail(url="https://i.imgur.com/WcdJrv4.png")
  embed.add_field(name='See Music Commands', value='`!help-music`', inline=False)
  embed.add_field(name='Search for a Game', value='`!steamgame <name>`', inline=True)
  embed.add_field(name='Steam Server Wishlist', value='`!wishlist` `!addwishlist <game-name>` `!removewishlist <game-name>`', inline=False)
  embed.add_field(name='AI Prompt!', value='`!p <prompt>`', inline=True)
  embed.add_field(name='CS2 Stats', value='`!cs2 <name>`', inline=True)
  embed.add_field(name='Today\'s Fortnite Shop', value='`!fn-shop`', inline=True)
  embed.add_field(name='Create a QR', value='Color-code should be in Hex format (#FFFFFF)\n`!qr <link> <optional: fg-color> <optional: bg-color>`', inline=False)
  embed.add_field(name='Random GIF', value='`!gif`', inline=True)
  embed.add_field(name='Currency Converter', value='`!convert <amount> <from-currency> <to-currency>`', inline=False)
  embed.add_field(name='Create events!', value='`/event`', inline=True)

  # Send the embed message to the same channel where the command was issued
  await ctx.channel.send(embed=embed)

# #####################
@bot.command(name='cs2', description='Display Counter-strike 2 stats (only setup for some players).')
async def steam_command(ctx, *, message: str):
  embed = steam.get_user_stats(ctx, message)
  await ctx.channel.send(embed=embed)

# #####################
@bot.command(name='fn-shop')
async def play_command(ctx):
  embed = fortnite.get_shop_items()
  await ctx.channel.send(embed=embed)

# #####################
@bot.command(name='qr', description="Generate QR image based on given prompt")
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

# #####################
@bot.command(name='gif', description="Send a random GIF in the chat")
async def play_command(ctx):
  gif = gifs.random_gif()
  await ctx.channel.send(gif)

# #####################
@bot.command(name="steamgame", description="Search for a Steam game and return game details")
async def steamgame(ctx, *, game_name: str):
  await ctx.send("Searching for game on Steam...")
  game_details = steam.search_steam_game(game_name)
  if isinstance(game_details, str):
    await ctx.send(game_details)
  else:
    formatted_game_id = steam.reformat_game_id(game_details['name'])
    print(f"[ LOG ] Formatted SteamGame ID: {formatted_game_id}")
    game_url = f"https://store.steampowered.com/app/{game_details['steam_appid']}/{formatted_game_id}/"
    discount = game_details.get('price_overview', {}).get('discount_percent', 0)
    embed = discord.Embed(
      title=game_details['name'] + f' (ON SALE - {discount}% OFF)' if discount != 0 else game_details['name'],
      description=game_details.get('description', 'No description available.'),
      color=discord.Color.red() if discount != 0 else discord.Color.purple())
    embed.add_field(name="Price", value=f"{game_details['price_overview']['final_formatted']}" if 'price_overview' in game_details else "Free or Price Not Available")
    embed.add_field(name="Genres", value=', '.join([genre['description'] for genre in game_details['genres']]))
    embed.add_field(name="App ID", value=f"{game_details['steam_appid']}")
    embed.add_field(name="Steam Store", value=f"{game_url}", inline=False)
    embed.set_thumbnail(url=game_details['header_image'])
    await ctx.send(embed=embed)

# #####################
@bot.command(name="addwishlist", description="Add a Steam game to the server wishlist and set default wishlist channel")
async def add_wishlist(ctx, *, game_name: str):
  await steam.add_to_wishlist(ctx, game_name, server_wishlists, default_channel)
  save_wishlist()
  print(default_channel)
  save_default_channel()

@bot.command(name="removewishlist", description="Remove a Steam game from the servers wishlist.")
async def remove_wishlist(ctx, *, game_name: str):
  await steam.remove_from_wishlist(ctx, game_name, server_wishlists)
  save_wishlist()

@bot.command(name="wishlist", description="Display the servers communal wishlist, if it exists.")
async def show_wishlist(ctx):
  await steam.show_wishlist(ctx, server_wishlists)

# #####################
@bot.command(name="nfl_matchups", description="Displays information about an NFL league from Sleeper.")
async def nfl_league_info(ctx):
 embed = sport_details.fetch_matchup()
 await ctx.channel.send(embed=embed)

# #####################
@bot.command(name="nfl_week", description="Displays information about the current weeks NFL matchups from ESPN.")
async def nfl_weekly_matchup(ctx):
 embed = sport_details.get_weekly_games()
 await ctx.channel.send(embed=embed)

# #####################
@bot.command(name="convert", description="Converts the amount entered from currency A to currency B.")
async def current_converter(ctx, *, args: str):
  try:
    # Split the input into components
    components = args.split()
    if len(components) != 3:
      await ctx.send("Error: Please provide the correct format: `!convert <amount> <from_currency> <to_currency>`")
      return

    amount, from_currency, to_currency = components

    # Validate and convert the amount
    try:
      amount = float(amount)
    except ValueError:
      await ctx.send("Error: Amount must be a valid number.")
      return

    # Call the currency conversion function
    await currency.convert_currency(ctx, amount, from_currency, to_currency)

  except Exception as e:
    await ctx.send(f"An unexpected error occurred: {e}")

# #####################
@bot.command(name='p', description='Chat with the bot using HuggingFace models (trained up to 2022).')
async def ask_ai_command(ctx, *, query: str):
  await ctx.typing()  # Show typing while processing
  payload = {
    "messages": [
      {
        "role": "user",
        "content": query
      }
    ],
    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1"
  }

  response = requests.post(HUGGING_FACE_API_URL, headers=HF_HEADER, json=payload)

  if response.status_code != 200:
    await ctx.channel.send(f"⚠️ API Error {response.status_code}: {response.text}")
    return

  try:
    output = response.json()["choices"][0]["message"]["content"]
  except (KeyError, IndexError, TypeError) as e:
    await ctx.channel.send("⚠️ Error parsing response from Hugging Face.")
    print(f"Response parsing error: {e}")
    print(response.json())
    return

  # Handle discord character limit gracefully
  MAX_LENGTH = 1900  # Leave space for truncation note
  if len(output) > MAX_LENGTH:
    output = output[:MAX_LENGTH] + "\n...\n⚠️ Response truncated."

  await ctx.channel.send(output)

# ========================================
# SLASH COMMANDS
# ========================================
# #####################
@bot.tree.command(name="event", description="Create an event", guild=None)
@app_commands.describe(date="Date of the event (YYYY-MM-DD)", time="Event time (HH:MM, 24-hour format)", description="Description of event")
async def create_event(interaction: discord.Interaction, date: str, time: str, description: str):
  await events.create_event(interaction, date, time, description)


# ========================================
# PLAY MUSIC
# ========================================
# #####################
@bot.command(name="help-music", description="Displays the commands available related to music playing/queuing/skipping/etc.")
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

@bot.command(name="play", description="Allows user to play music using text or a YouTube link.")
async def play_command(ctx, *, message: str):
  print(ctx)
  embed = await playmusic.play_music(ctx, message, bot)
  await ctx.channel.send(embed=embed)

@bot.command(name="leave", description="Makes the bot leave the voice channel.")
async def leave_command(ctx):
  embed = await playmusic.leave_channel(ctx)
  await ctx.channel.send(embed=embed)

@bot.command(name="skip", description="Skips the current song that is playing and plays the next one in the queue.")
async def skip_command(ctx):
  await playmusic.skip_song(ctx, bot)


# ========================================
# CHAT RESPONSES
# ========================================
@bot.event
async def on_message(ctx):
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
