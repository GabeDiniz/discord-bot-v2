import requests  # pip install requests
import json
import discord   # pip install discord

# Fetch Credentials from local .env variables 
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')

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
    # Add fields to the embed (optional)
    kills = user_stats[0]["value"]
    deaths = user_stats[1]["value"]
    embed.add_field(name='Overall KD', value=f"Total Kills: {kills}\nTotal Deaths: {deaths}\nKD: {round(kills/deaths, 2)}", inline=False)
    embed.add_field(name='Total Wins', value=user_stats[6]["value"], inline=False)
    return embed
  else:
    print("User stats not found or API request failed.")
    return

# For testing:
# get_user_stats("!cs2 gabe")

# STEAM ID - Obtained from: https://www.steamidfinder.com/