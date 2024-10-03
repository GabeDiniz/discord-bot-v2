import json
import discord   # pip install discord
from datetime import date, datetime, timedelta


def get_shop_items():
  """
  Search for the current Fortnite shop based on the date.

  Returns
  -------
  discord.Embed: with the image of the shop
  """
  # Format todays shop URL
  current_time = datetime.now()

  # Check if its after 7pm EST
  #   > At 7pm the Shop updates to the next day (update day accordingly)
  if int(str(current_time).split()[1][:2]) >= 19:
    shop_date = date.today() + timedelta(days=1)  
  else:
    shop_date = str(date.today())

  formatted_string = str(shop_date).replace("-", "_") + "_en.png"
  url = 'https://shop.easyfnstats.com/1092593399997136987/' + formatted_string
  print(url)

  embed = discord.Embed(
    title=":shopping_cart: Todays Fortnite Shop ",
    color=discord.Color.blurple()
  )
  embed.set_image(url=url)
  # embed.set_image(url="https://imgur.com/XpYfvqM.jpg")
  
  return embed
