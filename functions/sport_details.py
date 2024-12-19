import requests

API_KEY = "3"  # Free public API key
LEAGUE_NAME = "NFL"

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
    url = ESPN
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("events"):
            for event in data["events"]:
                time = event["status"]["type"]["detail"]
                matchName = event["name"]
                weather = event["weather"]["displayValue"]
                print(f"Match: {matchName} ({time})")
                print(f"Weather: {weather}")
        else:
            print("No live games currently.")
    else:
        print("Error fetching live scores.")

