import requests
import json

# Fetch Credentials from local .env variables 
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')


def load_users(file: str) -> dict:
  with open(file, "r") as f:
    return json.load(f)


def get_user_stats(steam_id, app_id):
    url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={app_id}&key={STEAM_API_KEY}&steamid={steam_id}'
    response = requests.get(url)
    data = response.json()
    
    if 'playerstats' in data and 'stats' in data['playerstats']:
        return data['playerstats']['stats']
    else:
        return None


def format_embed():
    pass

# STEAM ID - Obtained from: https://www.steamidfinder.com/
steam_id = '76561198099677359' 
app_id = 730  # Counter-Strike App ID
user_stats = get_user_stats(steam_id, app_id)

if user_stats:
    for stat in user_stats:
        print(f"{stat['name']}: {stat['value']}")
else:
    print("User stats not found or API request failed.")
