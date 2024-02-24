import requests
import json
import discord   # pip install discord

def get_user_stats(message: str):
  # Find user

  url = 'https://fortnite-api.com/v2/shop/br'
  response = requests.get(url)
  data = response.json()
  print("test")
  print(data)
  # for d in data:
  #   print(d)

get_user_stats("na")