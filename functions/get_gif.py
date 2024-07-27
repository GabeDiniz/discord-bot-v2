import requests

# Fetch Credentials from local .env variables 
from decouple import config
GIPHY_API_KEY = config('GIPHY_API_KEY')


def random_gif():
  url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&tag=&rating=g"
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      data = data["data"]["embed_url"]
      if data:
        return data
  return None