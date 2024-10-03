import requests
import discord   # pip install discord


def fetch_league_info():
  """
  Retrieve NFL Sleeper League information based on League ID via Sleeper API.

  Returns
  -------
  discord.Embed: with League information (League ID, Name, Roster size)
  discord.Embed Error: if error occurs
  """
   # Sleeper API League details
  league_id = '1125842110265032704'
  api_url = f'https://api.sleeper.app/v1/league/{league_id}'

  response = requests.get(api_url)

  if response.status_code == 200:
    league_data = response.json()
    embed = discord.Embed(title=f"{league_data['name']} (2024)", color=discord.Color.red())
    embed.add_field(name="League ID", value=league_id, inline=True)
    embed.add_field(name="Total Rosters", value=league_data['total_rosters'], inline=False)

    return embed
  else:
    return discord.Embed(title="Failed to retrieve league information. Please check the league ID and try again.", color=discord.Color.red())

def fetch_matchup():
  """
  Retrive NFL league matchup for the current week.

  Returns
  -------
  discord.Embed: with matchup information
  """
  # Retrieve current NFL week
  api_url = 'https://api.sleeper.app/v1/state/nfl'
  week = requests.get(api_url).json()["week"]

  # Setup embed
  embed = discord.Embed(title=f"PSFF (2024)", description=f'Matchups for week {week}', color=discord.Color.red())

  users_url = 'https://api.sleeper.app/v1/league/1125842110265032704/users'
  rosters_url = 'https://api.sleeper.app/v1/league/1125842110265032704/rosters'
  matchups_url = f'https://api.sleeper.app/v1/league/1125842110265032704/matchups/{week}'

  users_response = requests.get(users_url)
  roster_response = requests.get(rosters_url)
  matchups_response = requests.get(matchups_url)

  # Fetch data
  if users_response.status_code == 200 and roster_response.status_code == 200 and matchups_response.status_code == 200:
    user_data = users_response.json()
    roster_data = roster_response.json()
    matchup_data = matchups_response.json()

  # Organize roster data
  roster_info = {}
  for roster in roster_data:
    roster_id = roster['roster_id']
    roster_info[roster_id] = roster

  # Organize user data
  user_info = {}
  for user in user_data:
    user_id = user['user_id']
    user_info[user_id] = user

  # Get Matchup info
  matchup_info = {}
  for matchup in matchup_data:
    roster_id, matchup_id = matchup['roster_id'], matchup['matchup_id']
    print(f"[TESTING - Roster ID and Matchup ID] {roster_id}, {matchup_id}")

    # Grab userId
    user_id = roster_info[roster_id]['owner_id'] # Ex: 997305988602544128

    if matchup_id not in matchup_info:
      # Create new Matchup
      matchup_info[matchup_id] = {'user1': user_info[user_id]['display_name'], 'team1': user_info[user_id]['metadata']['team_name']}
    else: 
      # Add user2 and team2 to existing Matchup
      matchup_info[matchup_id]['user2'] = user_info[user_id]['display_name']
      matchup_info[matchup_id]['team2'] = user_info[user_id]['metadata']['team_name']
  
  # Add a field for each matchup
  for i in range(1, len(matchup_info) + 1):
    current_matchup = matchup_info[i]
    print(f"MATCHUP {i}: {current_matchup['user1']} vs {current_matchup['user2']}")
    embed.add_field(name=f"Matchup {i}", value=f"{current_matchup['user1']} ({current_matchup['team1']}) vs {current_matchup['user2']} ({current_matchup['team2']})", inline=False)

  return embed
  
  