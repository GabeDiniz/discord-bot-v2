import requests
import json
import discord   # pip install discord

def get_shop_items():
  # Find user

  url = 'https://fortnite-api.com/v2/shop/br'
  response = requests.get(url)
  data = response.json()


  # print("test")
  # print(data)
  # for d in data:
  #   print(d)

get_shop_items()