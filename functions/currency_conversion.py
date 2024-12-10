import discord
import requests  # pip install requests

# Fetch Credentials from local .env variables 
from decouple import config

EXCHANGE_RATE_API_KEY = config('EXCHANGE_RATE_API_KEY')

def get_rates(base_currency):
  """
  Search for the conversion rate off of the base currency using the Exchange Rate API.

  Parameters
  ----------
  base_currency: str
    The exchange rate token that the results will be based off of. 

  Returns
  -------
  dic:
    The conversion rate results based on the base currency.
  str:
    If no match is found that meets the cutoff criteria.
  """
  api_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{base_currency}"
  response = requests.get(api_url)

  if response.status_code == 200:
    rates = response.json()
    return rates['conversion_rates']
  else:
    print("[ API ERROR ] Response was not 200...")
    return f"{base_currency} not found (status code: {response.status_code})"

async def convert_currency(ctx, amount, from_currency, to_currency):
  """
  Description

  Parameters
  ----------
  ctx: discord.Bot
    The Discord bot instance used to interact with channels and send messages.
  amount: float
    The amount to be converted.
  from_currency: str
    The currency that the amount is based off of.
  to_currency: str
    The currency that the amount will be converted to.

  Returns
  -------
  None
    Sends a Discord embed message of the converted amount from from_currency to to_currency.
  """
  from_currency, to_currency = from_currency.upper(), to_currency.upper()
  rates = get_rates(from_currency)

  if isinstance(rates, dict):
    if to_currency in rates:
      rate = rates[to_currency]
      converted_amount = amount * rate

      # Send Discord Embed
      embed = discord.Embed(
        title=f"{amount} {from_currency} is approximately {converted_amount:.2f} {to_currency}.",
        color=discord.Color.blurple()
      )
    else:
      embed = discord.Embed(
        title=f"Error: {to_currency} not found in exchange rates.",
        color=discord.Color.red()
      )
  else:
    embed = discord.Embed(
      title=f"Error: {rates}",
      color=discord.Color.red()
    )
  
  # Send the message to the channel
  await ctx.send(embed=embed)