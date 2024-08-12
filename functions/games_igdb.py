from decouple import config   # pip install python-decouple
import requests
import json

def query_igdb():
  # IGDB API credentials
  clientID = config('IGDB_CLIENTID')
  accessToken = config('IGDB_ACCESS_TOKEN')

  # IGDB API endpoint
  url = 'https://api.igdb.com/v4/games'

  # Headers including the authorization and the Client ID
  headers = {
    'Client-ID': clientID,
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
  }

  # Query
  body = 'fields name; limit 10;'

  response = requests.post(url, headers=headers, data=body)

  if response.status_code == 200:
    # Print the response data
    games = response.json()
    print(json.dumps(games, indent=4))
  else:
    print('Failed to retrieve data:', response.status_code)
    print('If 401 ERROR, it is possible the access token has expired. Send a POST request here to get a new one:')
    print('https://id.twitch.tv/oauth2/token?client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>&grant_type=client_credentials')

# Run the function
query_igdb()