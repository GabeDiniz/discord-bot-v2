import requests

API_KEY = "3"  # Free public API key
LEAGUE_NAME = "NFL"

# Text to Discord Emoji Dictionary
weather_dictionary = {
    "Cloudy": ":cloud:",
    "Mostly cloudy": ":white_sun_cloud:",
    "Intermittent clouds": ":partly_sunny:",
    "Rain": ":cloud_rain:",
    "Sunny": ":sun:",
    "Mostly sunny": ":white_sun_small_cloud:",
    "Partly sunny": ":white_sun_small_cloud:",
    "Clear": ":sun:",
    "Done": ":white_check_mark:"
}

SPORTSDB = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/livescore.php?l={LEAGUE_NAME}"

def get_live_scores_sportsdb():
    url = SPORTSDB
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("events"):
            for event in data["events"]:
                print(f"Match: {event['strEvent']}")
                print(f"Score: {event['intHomeScore']} - {event['intAwayScore']}")
        else:
            print("No live games currently.")
    else:
        print("Error fetching live scores.")

ESPN = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

def get_weekly_games():
  """
  Search for the details of the current week's NFL games.

  Parameters
  ----------
  ctx: discord.Bot
    The Discord bot instance used to interact with channels and send messages.

  Returns
  -------
  None
    Sends a Discord embed message of the current week's game details.
  """
  url = ESPN
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    if data.get("events"):
      for event in data["events"]:
        time = event["status"]["type"]["detail"]
        matchName = event["name"]
        try:
          weather = event["weather"]["displayValue"]
        except KeyError:
          weather = "Done"
        print(f"Match: {matchName} ({time})")
        print(f"Weather: {weather}")
    else:
      print("No live games currently.")
  else:
    print("Error fetching live scores.")
