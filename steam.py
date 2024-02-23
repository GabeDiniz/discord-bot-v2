import requests
import json
import discord   # pip install discord

# Fetch Credentials from local .env variables 
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')


def load_users(file: str) -> dict:
  with open(file, "r") as f:
    return json.load(f)


def get_user_stats(message: str):
  # Find user
  users = load_users("steam-info.json")
  user = message.strip().split(" ")[-1].lower()
  steam_id = users[user]

  app_id = 730 # Counter-Strike App ID
  url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={app_id}&key={STEAM_API_KEY}&steamid={steam_id}'
  response = requests.get(url)
  data = response.json()
  
  if 'playerstats' in data and 'stats' in data['playerstats']:
    user_stats = data['playerstats']['stats']
  else:
    return None
  
  if user_stats:
    # print(user_stats)
    embed = discord.Embed(
      title="CS2 STATS: " + user.capitalize(),
      color=discord.Color.red()
    )
    # Add fields to the embed (optional)
    kills = user_stats[0]["value"]
    deaths = user_stats[1]["value"]
    embed.add_field(name='Overall KD', value=f"Total Kills: {kills}\nTotal Deaths: {deaths}\nKD: {round(kills/deaths, 2)}", inline=False)
    embed.add_field(name='Total Wins', value=user_stats[6]["value"], inline=False)
    return embed
    # for stat in user_stats:
    #   print(f"{stat['name']}: {stat['value']}")
  else:
    print("User stats not found or API request failed.")
    return


# get_user_stats("!cs2 gabe")

def format_embed():
  pass

# STEAM ID - Obtained from: https://www.steamidfinder.com/
# steam_id = '76561198099677359' 
# user_stats = get_user_stats(steam_id, app_id)

# print(load_users("steam-info.json")["Gabe"])


if __name__ == "__main__":
  pass