import requests
import discord   # pip install discord


def fetch_league_info():
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

# def fetch_matchup():
#   # Fetch matchups for the current week (e.g., week 1)
#   week = 1
#   matchups_url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
#   matchups_response = requests.get(matchups_url)
#   if matchups_response.status_code == 200:
#     matchups_data = matchups_response.json()
#     matchups_text = "Matchups for Week 1:\n"
#     for matchup in matchups_data:
#       matchups_text += f"Roster {matchup['roster_id']} vs Roster {matchup.get('opponent_id', 'TBD')}\n"
#     embed.add_field(name="Week 1 Matchups", value=matchups_text, inline=False)
#   else:
#     embed.add_field(name="Week 1 Matchups", value="Failed to retrieve matchups for Week 1.", inline=False)