import requests  # pip install requests
import json
import discord   # pip install discord
import re

# Fetch Credentials from local .env variables 
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')

# ========================================
# COMMAND: !addwishlist
# ========================================
async def add_to_wishlist(ctx, game_name, server_wishlists):
  game_details = search_steam_game(game_name)
  # Check if returned is str -> Unable to find game
  if isinstance(game_details, str):
    await ctx.send(game_details)
    return

  # Get the server (guild) ID
  guild_id = ctx.guild.id

  # If the server doesn't have a wishlist yet, create one
  if guild_id not in server_wishlists:
    server_wishlists[guild_id] = []

  # Check if the game is already in the wishlist
  if any(game['steam_appid'] == game_details['steam_appid'] for game in server_wishlists[guild_id]):
    await ctx.send(f"{game_details['name']} is already in the wishlist!")
    return

  # Add the game to the server's wishlist
  server_wishlists[guild_id].append(game_details)
  await ctx.send(f"{game_details['name']} has been added to the wishlist!")

# ========================================
# COMMAND: !removewishlist
# ========================================
async def remove_from_wishlist(ctx, game_name, server_wishlists):
  """Removes a game from the server's wishlist."""
  # Get the server (guild) ID
  guild_id = ctx.guild.id

  # Check if the server has a wishlist
  if guild_id not in server_wishlists or not server_wishlists[guild_id]:
    await ctx.send("The wishlist is currently empty.")
    return

  # Search for the game in the wishlist
  game_details = search_steam_game(game_name)
  # Check if returned is str -> Unable to find game
  if isinstance(game_details, str):
    await ctx.send(game_details)
    return

  # Try to remove the game from the wishlist
  wishlist = server_wishlists[guild_id]
  for game in wishlist:
    if game['steam_appid'] == game_details['steam_appid']:
      wishlist.remove(game)
      await ctx.send(f"{game['name']} has been removed from the wishlist!")
      return

  await ctx.send(f"{game_name} is not in the wishlist.")

# ========================================
# COMMAND: !steamgame
# ========================================
def search_steam_game(game_name):
  """Search for a game on Steam by name and return its details."""
  url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
  response = requests.get(url)
  if response.status_code == 200:
    apps = response.json()['applist']['apps']
    # Find the game by name
    game = next((app for app in apps if game_name.lower() == app['name'].lower()), None)
    print(game)
    if game:
      # Fetch details for the found game
      details_url = f"http://store.steampowered.com/api/appdetails?appids={game['appid']}"
      details_response = requests.get(details_url)
      if details_response.status_code == 200:
        game_details = details_response.json()[str(game['appid'])]['data']
        print(f"Retrieved game from {details_url}")
        return game_details
      else:
        return "Failed to fetch game details."
    else:
      return "Game not found."
  else:
    return "Failed to fetch game list."
  

def reformat_game_id(input_string: str):
  # Remove symbols
  cleaned_string = re.sub(r'[-$#&]', '', input_string)

  # Replace spaces with underscores
  result_string = re.sub(r'\s+', '_', cleaned_string)
  
  return result_string.lower()


# ========================================
# COMMAND: !cs2
# ========================================
def load_users(file: str) -> dict:
  with open(file, "r") as f:
    return json.load(f)


def get_user_stats(ctx, message: str):
  # Find user
  file_path = "./knowledge/steam-info.json"
  users = load_users(file_path)
  user = message.strip().split(" ")[-1].lower()
  try:
    steam_id = users[user]
  except KeyError:
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