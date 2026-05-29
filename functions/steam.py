import requests  # pip install requests
import discord   # pip install discord
import re

import functions.db as db

# Fetch Credentials from local .env variables
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')
STEAM_APPDETAILS_URL = "https://store.steampowered.com/api/appdetails?appids="


def fetch_game_price(game_id: str) -> dict:
  """Fetches the current price and discount for a Steam game."""
  response = requests.get(STEAM_APPDETAILS_URL + str(game_id)).json()[str(game_id)]['data']
  if 'price_overview' in response:
    return {
      "current_price": response['price_overview']['final_formatted'],
      "discount": int(response['price_overview']['discount_percent'])
    }
  return {"current_price": "Free or Unavailable", "discount": 0}


def add_game_fields(embed, game, price_info):
  """Adds a game's info fields to an existing embed."""
  title = game['name']
  if price_info['discount'] > 0:
    title += f' (ON SALE - {price_info["discount"]}% OFF) 🔥'
  formatted_game_id = reformat_game_id(game['name'])
  game_url = f"https://store.steampowered.com/app/{game['steam_appid']}/{formatted_game_id}/"
  embed.add_field(name="", value=f"🎮 **[{title}]({game_url})**", inline=False)
  embed.add_field(name="", value=f"Price: {price_info['current_price']}", inline=False)

# ========================================
# LOOP (24h): Steam Sale
# ========================================
async def check_sale(bot):
  """
  Checks every server's wishlist for games on sale and posts an announcement to that server's
  configured default channel. Reads both wishlists and default channels from the SQLite DB.
  """
  server_wishlists = db.get_all_wishlists()
  default_channel_ids = db.get_all_default_channels()

  for guild_id, wishlist in server_wishlists.items():
    channel_id = default_channel_ids.get(guild_id)
    if not channel_id:
      print(f"[ LOG ] No default channel set for guild {guild_id}, skipping.")
      continue
    channel = bot.get_channel(int(channel_id))
    print(f"[ LOG ] Found channel: {channel}")
    if not channel:
      print(f"Channel with ID {channel_id} not found.")
      continue

    embed = discord.Embed(
      title="🔥 Wishlist Games on Sale!",
      color=discord.Color.red()
    )

    for game in wishlist:
      game_id = str(game['steam_appid'])
      price_info = fetch_game_price(game_id)
      print(f"[ LOG ] Game: {game['name']} | Price: {price_info['current_price']} | Discount: {price_info['discount']}")

      if price_info['discount'] > 0:
        print(f"[ SUCCESS ] Discounted game found! GAME: {game['name']}")
        add_game_fields(embed, game, price_info)

    # Only send if at least one game is on sale
    if embed.fields:
      await channel.send(embed=embed)

# ========================================
# COMMAND: !addwishlist
# ========================================
async def add_to_wishlist(ctx, game_id):
  """
  Search for a game on Steam and add it to this guild's wishlist if not already present.
  Also sets the guild's default announcement channel to the current channel if not already set.
  """
  game_details = search_steam_game(game_id)
  if isinstance(game_details, str):
    await ctx.send(game_details)
    return

  guild_id = str(ctx.guild.id)

  # First time we see this guild: store channel + name. Otherwise just keep server_name fresh.
  existing = db.get_server(guild_id)
  if existing is None:
    db.upsert_server(guild_id, str(ctx.channel.id), ctx.guild.name)
  elif existing.get("server_name") != ctx.guild.name:
    db.update_server_name(guild_id, ctx.guild.name)

  inserted = db.add_wishlist_game(guild_id, str(game_details['steam_appid']), game_details)
  if not inserted:
    await ctx.send(f"❌ Whoops! {game_details['name']} is already in the wishlist!")
    return

  await ctx.send(f"✅ {game_details['name']} has been added to the wishlist!")

# ========================================
# COMMAND: !removewishlist
# ========================================
async def remove_from_wishlist(ctx, game_name):
  """Remove a game from this guild's wishlist by case-insensitive name match."""
  guild_id = str(ctx.guild.id)

  if not db.get_wishlist(guild_id):
    await ctx.send("The wishlist is currently empty. 😢 Use !addwishlist <game-name> to add games to your Server's wishlist")
    return

  removed = db.remove_wishlist_game_by_name(guild_id, game_name)
  if removed:
    await ctx.send(f"{removed} has been removed from the wishlist!")
  else:
    await ctx.send(f"Unable to find {game_name} in the wishlist.")

# ========================================
# COMMAND: !wishlist
# ========================================
async def show_wishlist(ctx):
  """Display the server's wishlist as an embed."""
  guild_id = str(ctx.guild.id)
  wishlist = db.get_wishlist(guild_id)

  if not wishlist:
    await ctx.send("The wishlist is currently empty. 😢 Use !addwishlist <game-name> to add games to your Server's wishlist")
    return

  embed = discord.Embed(
    title=f"🎁 {ctx.guild.name}'s Wishlist",
    color=discord.Color.blue()
  )

  # Add each game in the wishlist to the embed
  for game in wishlist:
    game_id = str(game['steam_appid'])
    price_info = fetch_game_price(game_id)
    add_game_fields(embed, game, price_info)

  await ctx.send(embed=embed)

# ========================================
# COMMAND: !steamgame
# ========================================
def search_steam_game(game_id: str):
  """
  Search for a game on Steam by ID and retrieves its details if found.

  Parameters
  ----------
  game_id: str
    The ID of the game to be searched for on Steam.

  Returns
  -------
  dict:
    A dictionary containing the game's details if the game is found and the details are successfully retrieved.
  str:
    A message indicating the error if the game is not found, or if there is a failure in fetching the game list or details.
  """
  url = f"https://store.steampowered.com/api/appdetails?appids={game_id}" # No API key required for this endpoint
  response = requests.get(url)
  if response.status_code == 200:
    game_details = response.json()[str(game_id)]['data']
    print(f"[ LOG ] Found game from search_steam_game(): {game_details}")
    # Retrieve only the data we need
    useful_info = {
      'name': game_details.get('name'),
      'steam_appid': game_id,
      'price_overview': game_details.get('price_overview', {}),
      'description': game_details.get('short_description', 'No description available'),
      'genres':game_details.get('genres', []),
      'header_image': game_details.get('header_image'),
    }
    return useful_info
  else:
    return "I was unable to find that game on Steam. Please check the game ID and try again."

def deprecated_search_steam_game(game_name: str):
  """
  Search for a game on Steam by name and retrieves its details if found.

  Parameters
  ----------
  game_name: str
    The name of the game to be searched for on Steam.

  Returns
  -------
  dict:
    A dictionary containing the game's details if the game is found and the details are successfully retrieved.
  str:
    A message indicating the error if the game is not found, or if there is a failure in fetching the game list or details.
  """
  url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/" # Deprecated
  url = f"https://store.steampowered.com/api/appdetails?appids=<APP_ID>"
  response = requests.get(url)
  if response.status_code == 200:
    apps = response.json()['applist']['apps']
    # Find the game by name
    game = next((app for app in apps if game_name.lower() == app['name'].lower()), None)
    print(f"[ LOG ] Search steam game: {game}")
    if game:
      # Fetch details for the found game
      details_url = f"http://store.steampowered.com/api/appdetails?appids={game['appid']}"
      details_response = requests.get(details_url)
      if details_response.status_code == 200:
        # Retrieve only the data we need
        game_details = details_response.json()[str(game['appid'])]['data']
        useful_info = {
          'name': game_details.get('name'),
          'steam_appid': game_details.get('steam_appid'),
          'price_overview': game_details.get('price_overview', {}),
          'description': game_details.get('short_description', 'No description available'),
          'genres':game_details.get('genres', []),
          'header_image': game_details.get('header_image'),
        }
        return useful_info
      else:
        return "Failed to fetch game details."
    else:
      return "Game not found."
  else:
    return "[API Failure] Failed to fetch game list from Steam API."


def reformat_game_id(input_string: str):
  """
  Reformat a game ID string by removing specific symbols and replacing spaces with underscores.

  Parameters
  ----------
  input_string: str
    The string to be reformatted, which may contain symbols and spaces.

  Returns
  -------
  str:
    The reformatted string with symbols removed, spaces replaced by underscores, and all characters converted to lowercase.
  """
  # Remove symbols
  cleaned_string = re.sub(r'[-$#&]', '', input_string)

  # Replace spaces with underscores
  result_string = re.sub(r'\s+', '_', cleaned_string)

  return result_string.lower()


# ========================================
# COMMAND: !cs2
# ========================================
def get_user_stats(ctx, message: str):
  """
  Retrieves and displays a user's Counter-Strike 2 statistics from Steam.

  Parameters
  ----------
  ctx: context
    The context of the command invocation, which includes details such as the server (guild) and channel information.
  message: str
    The message string containing the user's identifier (e.g., their name) to look up.

  Returns
  -------
  discord.Embed:
    An embedded message containing the user's Counter-Strike 2 stats if the user is found and the API request is successful.
  discord.Embed:
    An error message if the user is not found in the stored user list or if their game details are not public.
  None:
    If the user's stats are not found or the API request fails.
  """
  user = message.strip().split(" ")[-1].lower()
  steam_id = db.get_steam_id(user)
  if steam_id is None:
    embed = discord.Embed(
      title=":bangbang: E R R O R",
      description="User not found. Please send your SteamID to Gabe",
      color=discord.Color.red()
    )
    return embed

  app_id = 730 # Counter-Strike App ID
  url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={app_id}&key={STEAM_API_KEY}&steamid={steam_id}'
  response = requests.get(url)
  data = response.json()

  if 'playerstats' in data and 'stats' in data['playerstats']:
    user_stats = data['playerstats']['stats']
  # API Fetch Failure!!!
  else:
    embed = discord.Embed(
      title=":bangbang: E R R O R",
      description="Please make your game details public\nGo to Edit Profile > Privacy settings",
      color=discord.Color.red()
    )
    return embed

  if user_stats:
    embed = discord.Embed(
      title=":military_helmet: CS2 STATS: " + user.capitalize(),
      color=discord.Color.yellow()
    )
    # Add fields to the embed
    kills = user_stats[0]["value"]
    deaths = user_stats[1]["value"]
    embed.add_field(name='Overall KD', value=f"Total Kills: {kills}\nTotal Deaths: {deaths}\nKD: {round(kills/deaths, 2)}", inline=False)
    embed.add_field(name='Total Wins', value=user_stats[6]["value"], inline=False)
    return embed
  else:
    print("User stats not found or API request failed.")
    return
