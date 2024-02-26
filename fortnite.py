import requests
import json
import discord   # pip install discord
from datetime import date


def get_shop_items():
  # Format todays shop URL
  today_date = str(date.today())
  formatted_string = today_date.replace("-", "_") + "_en.png"
  url = 'https://shop.easyfnstats.com/' + formatted_string
  print(url)

  embed = discord.Embed(
    title=":shopping_cart: Todays Fortnite Shop ",
    color=discord.Color.red()
  )
  embed.set_image(url=url)
  return embed
