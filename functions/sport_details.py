import requests

API_KEY = "3"  # Free public API key
LEAGUE_NAME = "NFL"

def get_live_scores():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/livescore.php?l={LEAGUE_NAME}"
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

get_live_scores()
