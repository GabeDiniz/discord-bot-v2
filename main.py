import json
from discord import Intents, Client, app_commands
from discord.ext import commands, tasks    # pip install discord-ext-bot
import discord   # pip install discord
import openai  # pip install openai
import os

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
import functions.nfl_sleeper as nfl_sleeper 
import functions.sport_details as sport_details
import functions.currency_conversion as currency 

# Fetch Credentials from local .env variables 
# Constants
BOT_KEY = config('BOT_KEY')
# OPENAI_API_KEY = config('OPENAI_API_KEY')
knowledge: dict = responses.load_knowledge('./knowledge/knowledge.json')

# Bot Constants
intents = Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None) # Initialize bot
# gptClient = openai.OpenAI(api_key=OPENAI_API_KEY)

# Start bot
@bot.event
async def on_ready():
  load_wishlist()
  await steam_sale.start()
  await bot.tree.sync()
  print(f"{bot.user} is now running!")

# ========================================
# FUNCTIONS
# ========================================
def save_wishlist():
  global server_wishlists
  with open('wishlist.json', 'w') as f:
    json.dump(server_wishlists, f)
  print("[ SAVED ] Wishlist saved successfully")

def save_default_channel():
  global default_wishlist_channel
  with open('default_channel.json', 'w') as f:
    json.dump(default_wishlist_channel, f)
    print("[ SAVED ] Default wishlist channel saved successfully")

def load_wishlist():
  '''Load wishlist if existing, create a new one if none available'''
  global server_wishlists
  global default_wishlist_channel
  try:
    print("[ LOG ] Loading Server Wishlist...")
    with open('wishlist.json', 'r') as f:
      server_wishlists = json.load(f)
    print("[ LOG ] LOADED existing Wishlist")

    print("[ LOG ] Loading Default Wishlist channel data...")
    with open('default_channel.json', 'r') as f:
      default_wishlist_channel = json.load(f)
    print("[ LOG ] LOADED Default Wishlist channel")
  except FileNotFoundError:
    print("[ LOG ] wishlist.json or default_channel.json not found, starting with an empty wishlist.")
    server_wishlists = {}
    default_wishlist_channel = {}


@tasks.loop(hours=12)
async def steam_sale():
  print("[ LOG ] Loop-task: checking for server steam wishlist sale")
  await steam.check_sale(bot, server_wishlists, default_wishlist_channel)

@steam_sale.before_loop
async def before_check_sales():
  '''Ensure the bot is ready before starting the steam_sale loop'''
  await bot.wait_until_ready()

# ========================================
# ! COMMANDS
# ========================================
# Simple example command
@bot.command(name='hello')
async def hello_command(ctx):
  await ctx.send(f'Hello, {ctx.author.name}!')

# #####################
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
  embed.add_field(name='Search for a Game', value='`!steamgame <name>`', inline=True)
  embed.add_field(name='Steam Server Wishlist', value='`!wishlist` `!addwishlist <game-name>` `!removewishlist <game-name>`', inline=False)
  embed.add_field(name='CS2 Stats', value='`!cs2 <name>`', inline=True)
  embed.add_field(name='Today\'s Fortnite Shop', value='`!fn-shop`', inline=True)
  embed.add_field(name='Create a QR', value='Color-code should be in Hex format (#FFFFFF)\n`!qr <link> <optional: fg-color> <optional: bg-color>`', inline=False)
  embed.add_field(name='Random GIF', value='`!gif`', inline=True)
  embed.add_field(name='Currency Converter', value='`!convert <amount> <from-currency> <to-currency>`', inline=False)
  embed.add_field(name='Create events!', value='`/event`', inline=True)
        
  # Send the embed message to the same channel where the command was issued
  await ctx.channel.send(embed=embed)

# #####################
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

# #####################
@bot.command(name='cs2')
async def steam_command(ctx, *, message: str):
  embed = steam.get_user_stats(ctx, message)
  await ctx.channel.send(embed=embed)
  
# #####################
@bot.command(name='fn-shop')
async def play_command(ctx):
  embed = fortnite.get_shop_items()
  await ctx.channel.send(embed=embed)

# #####################
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

# #####################
@bot.command(name='gif')
async def play_command(ctx):
  gif = gifs.random_gif()
  await ctx.channel.send(gif)

# #####################
@bot.command(name="steamgame")
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
@bot.command(name="addwishlist")
async def add_wishlist(ctx, *, game_name: str):
  await steam.add_to_wishlist(ctx, game_name, server_wishlists, default_wishlist_channel)
  save_wishlist()
  print(default_wishlist_channel)
  save_default_channel()
  
@bot.command(name="removewishlist")
async def remove_wishlist(ctx, *, game_name: str):
  await steam.remove_from_wishlist(ctx, game_name, server_wishlists)
  save_wishlist()

@bot.command(name="wishlist", description="Display the servers communal wishlist, if it exists.")
async def show_wishlist(ctx):
  await steam.show_wishlist(ctx, server_wishlists)
  
# #####################
@bot.command(name="nfl_matchups", description="Displays information about an NFL league from Sleeper.")
async def nfl_league_info(ctx):
 embed = nfl_sleeper.fetch_matchup()
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
# WIP: NOT FUNCTIONING AS IT COSTS MONEY
# @bot.command(name='gpt')
# async def chatgpt(ctx, *, query: str):
#   await ctx.typing()  # Show typing indicator while processing

#   try:
#     response = gptClient.chat.completions.create(
#       model="gpt-3.5-turbo",
#       messages=[
#         {"role": "user", "content": query}
#       ]
#     )
#     print(response)
#     answer = response.choices[0].message
#     await ctx.send(answer)
#   except Exception as e:
#     await ctx.send(f"An error occurred: {e}")


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