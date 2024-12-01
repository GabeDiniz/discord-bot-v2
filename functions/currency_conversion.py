import requests  # pip install requests

# Fetch Credentials from local .env variables 
from decouple import config

EXCHANGE_RATE_API_KEY = config('EXCHANGE_RATE_API_KEY')

def get_rates(base_currency):
  api_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{base_currency}"
  response = requests.get(api_url)
  
  if response.status_code == 200:
    rates = response.json()
    return rates['conversion_rates']
  else:
    return f"Error: Unable to fetch rates (status code: {response.status_code})"

def convert_currency(bot, amount, from_currency, to_currency):
  rates = get_rates(from_currency.upper())
  if isinstance(rates, dict):
    if to_currency in rates:
      rate = rates[to_currency]
      converted_amount = amount * rate
      return f"{amount} {from_currency} is approximately {converted_amount:.2f} {to_currency}."
    else:
      return f"Error: {to_currency} not found in exchange rates."
  else:
    return rates  # Return the error message

# Example usage:
print(convert_currency('none', 10, "cad", "USD"))