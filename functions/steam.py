import requests  # pip install requests
import json
import discord   # pip install discord
import re

# Fetch Credentials from local .env variables 
from decouple import config

# Constants
STEAM_API_KEY = config('STEAM_API_KEY')

# ========================================
# LOOP (24h): Steam Sale
# ========================================
async def check_sale(bot, server_wishlists, default_channel_id):
  """
  This asynchronous function continuously checks if any games in the server wishlists are on sale and announces the sale 
  in the respective server's default channel.

  Parameters
  ----------
  bot: discord.Bot
    The Discord bot instance used to interact with channels and send messages.
  server_wishlists: dict
    A dictionary where each server (guild) ID maps to its respective wishlist of games.
  default_channel_id: dict
    A dictionary where each server (guild) ID maps to the channel ID where sale announcements should be posted.

  Returns
  -------
  None
    Sends an embedded message to the default channel of each server announcing any discounts found on the wishlist games.
    Logs if a channel is not found or if no discounts are available.
  """
  url = f"http://store.steampowered.com/api/appdetails?appids="

  for guild_id, wishlist in server_wishlists.items():
    channel_id = default_channel_id[guild_id]  # Get the channel where to post the announcement
    # print(f"[ LOG ] Channel ID: {channel_id}") # Debug
    channel = bot.get_channel(int(channel_id))
    print(f"[ LOG ] Found channel: {channel}")
    if not channel_id:
      print(f"Channel with ID {guild_id} not found.")
      continue

    for game in wishlist:
      # Check if the game has a discount
      game_id = str(game['steam_appid'])
      response = requests.get(url + game_id).json()[game_id]['data']
      
      # Retrieve current discount and price
      if 'price_overview' in response:
        current_price = f"{response['price_overview']['final_formatted']}" 
        discount = int(response['price_overview']['discount_percent'])
      else:
        current_price = "Free or Unavailable"
        discount = 0
      print(f"[ LOG ] Game: {game['name']} | Price: {current_price} | Discount: {discount}")
      
      if discount > 0:
        print(f"[ SUCCESS ] Discounted game found! GAME: {game['name']}")
        embed = discord.Embed(
          title=f"🔥 {game['name']} is on sale! ({discount}% OFF)",
          description=game.get('short_description', 'No description available.'),
          color=discord.Color.red()
        )
        embed.add_field(
          name="Discounted Price", 
          value=current_price
        )
        embed.add_field(name="Steam Store", value=f"https://store.steampowered.com/app/{game['steam_appid']}/", inline=False)
        embed.set_thumbnail(url=game['header_image'])

        # Send the announcement to the channel
        await channel.send(embed=embed)

# ========================================
# COMMAND: !addwishlist
# ========================================
async def add_to_wishlist(ctx, game_name, server_wishlists, default_channel_data):
  """
  Search for a game on Steam, checks if it's already in the server's wishlist, 
  and adds it if not present.

  Parameters
  ----------
  ctx: discord context
    The context of the command invocation, which includes details such as the server (guild) and channel information.
  game_name: str
    The name of the game to be searched and added to the wishlist.
  server_wishlists: dict
    A dictionary storing wishlists for multiple servers, with each server (guild) ID as the primary key.

  Returns
  -------
  None
    Sends a message to the context based on the outcome: whether the game is added, already exists, 
    or cannot be found on Steam.
  """
  game_details = search_steam_game(game_name)
  # Check if returned is str -> Unable to find game
  if isinstance(game_details, str):
    await ctx.send(game_details)
    return

  # Get the server (guild) ID
  guild_id = str(ctx.guild.id)

  # If the server doesn't have a wishlist yet, create one
  #   and add default text channel
  if guild_id not in server_wishlists:
    server_wishlists[guild_id] = []
    channel_id = str(ctx.channel.id)
    print(channel_id)
    default_channel_data[guild_id] = channel_id

  # Check if the game is already in the wishlist
  if any(game['steam_appid'] == game_details['steam_appid'] for game in server_wishlists[guild_id]):
    await ctx.send(f"❌ Whoops! {game_details['name']} is already in the wishlist!")
    return

  # Add the game to the server's wishlist
  server_wishlists[guild_id].append(game_details)
  await ctx.send(f"✅ {game_details['name']} has been added to the wishlist!")

# ========================================
# COMMAND: !removewishlist
# ========================================
async def remove_from_wishlist(ctx, game_name, server_wishlists):
  """
  Removes a specified game from the server's wishlist if it exists.

  Parameters
  ----------
  ctx: discord context
    The context of the command invocation, which includes details such as the server (guild) and channel information.
  game_name: str
    The name of the game to be removed from the wishlist.
  server_wishlists: dict
    A dictionary storing wishlists for multiple servers, with each server (guild) ID as the primary key.

  Returns
  -------
  None
    Sends a message to the context based on the outcome:whether the game is removed, doesn't exist in the wishlist,
    or if the wishlist is empty.
  """
  # Get the server (guild) ID
  guild_id = str(ctx.guild.id)

  # Check if the server has a wishlist
  if guild_id not in server_wishlists or not server_wishlists[guild_id]:
    await ctx.send("The wishlist is currently empty. 😢 Use !addwishlist <game-name> to add games to your Server's wishlist")
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
    if int(game['steam_appid']) == int(game_details['steam_appid']):
      wishlist.remove(game)
      await ctx.send(f"{game['name']} has been removed from the wishlist!")
      return

  await ctx.send(f"{game_name} is not in the wishlist.")

# ========================================
# COMMAND: !wishlist
# ========================================
async def show_wishlist(ctx, server_wishlists):
  """
  Displays the server's wishlist by sending a formatted embeded message to the server.
  
  Parameters
  ----------
  ctx: context
    The context of the command invocation, which includes details such as the server (guild) and channel information.
  server_wishlists: dict
    A dictionary storing wishlists for multiple servers, with each server (guild) ID as the primary key.

  Returns
  -------
  None
    Sends a Discord embed message containing the wishlist, or a message stating that the wishlist is empty 
    if no games are found.
  """
  guild_id = str(ctx.guild.id)

  # Check if the server has a wishlist
  if guild_id not in server_wishlists or not server_wishlists[guild_id]:
    await ctx.send("The wishlist is currently empty. 😢 Use !addwishlist <game-name> to add games to your Server's wishlist")
    return

  wishlist = server_wishlists[guild_id]
  embed = discord.Embed(
    title=f"{ctx.guild.name}'s Wishlist", 
    color=discord.Color.blue()
  )
  
  url = f"http://store.steampowered.com/api/appdetails?appids="
  # Add each game in the wishlist to the embed
  for game in wishlist:
    # Check if the game has a discount
    game_id = str(game['steam_appid'])
    response = requests.get(url + game_id).json()[game_id]['data']

    # Retrieve current discount and price
    if 'price_overview' in response:
      current_price = f"{response['price_overview']['final_formatted']}" 
      discount = int(response['price_overview']['discount_percent'])
    else:
      current_price = "Free or Unavailable"
      discount = 0
    title = game['name'] + f' (ON SALE - {discount}% OFF) 🔥' if discount != 0 else game['name']
    formatted_game_id = reformat_game_id(game['name'])
    game_url = f"https://store.steampowered.com/app/{game['steam_appid']}/{formatted_game_id}/"
    embed.add_field(name="", value=f"**[{title}]({game_url})**", inline=False)
    embed.add_field(name="", value=f"Price: {current_price}", inline=False)

  await ctx.send(embed=embed)


# ========================================
# COMMAND: !steamgame
# ========================================
def search_steam_game(game_name):
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
  url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
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
    return "Failed to fetch game list."
  

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
def load_users(file: str) -> dict:
  """
  Loads a JSON file and returns its contents as a dictionary.

  Parameters
  ----------
  file: str
    The file path of the JSON file to be loaded.

  Returns
  -------
  dict:
    A dictionary representing the contents of the loaded JSON file.
  """
  with open(file, "r") as f:
    return json.load(f)


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