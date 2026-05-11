import discord
import requests  # pip install requests
from datetime import date, timedelta

# Fetch Credentials from local .env variables
from decouple import config

FINNHUB_API_KEY = config('FINNHUB_API_KEY')
FINNHUB_IPO_URL = "https://finnhub.io/api/v1/calendar/ipo"

# Discord embed limits 25 fields per embed; cap below that for safety/readability.
MAX_IPO_FIELDS = 15


def fetch_upcoming_ipos(days_ahead: int = 7):
  """
  Fetch the upcoming IPO calendar from Finnhub.

  Parameters
  ----------
  days_ahead: int
    Number of days into the future (from today) to include in the window.

  Returns
  -------
  list:
    A list of IPO dicts as returned by Finnhub (keys include `date`, `exchange`,
    `name`, `numberOfShares`, `price`, `status`, `symbol`, `totalSharesValue`).
  str:
    An error message if the API call failed.
  """
  today = date.today()
  end = today + timedelta(days=days_ahead)
  params = {
    "from": today.isoformat(),
    "to": end.isoformat(),
    "token": FINNHUB_API_KEY,
  }
  response = requests.get(FINNHUB_IPO_URL, params=params)

  if response.status_code == 200:
    return response.json().get("ipoCalendar", [])
  else:
    print("[ API ERROR ] Finnhub IPO calendar response was not 200...")
    return f"Could not fetch IPO calendar (status code: {response.status_code})"


def _format_price_range(price: str) -> str:
  """Finnhub returns price as a string like '10-12' or '' — normalize for display."""
  if not price:
    return "TBD"
  return f"${price}"


async def show_upcoming_ipos(ctx, days_ahead: int = 7):
  """
  Send an embed listing upcoming IPOs in the next `days_ahead` days.

  Parameters
  ----------
  ctx: discord.ext.commands.Context
    The Discord command context used to send the reply.
  days_ahead: int
    How many days into the future to include.
  """
  result = fetch_upcoming_ipos(days_ahead)

  if isinstance(result, str):
    embed = discord.Embed(title=f"Error: {result}", color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  if not result:
    await ctx.send(f"No IPOs scheduled in the next {days_ahead} days.")
    return

  embed = discord.Embed(
    title=f"Upcoming IPOs (next {days_ahead} days)",
    color=discord.Color.green(),
  )
  for ipo_entry in result[:MAX_IPO_FIELDS]:
    name = ipo_entry.get("name") or "Unknown"
    symbol = ipo_entry.get("symbol") or "?"
    field_name = f"{name} ({symbol})"
    value = (
      f"📅 {ipo_entry.get('date', 'TBD')}\n"
      f"🏛️ {ipo_entry.get('exchange', 'Unknown exchange')}\n"
      f"💵 {_format_price_range(ipo_entry.get('price', ''))}"
    )
    embed.add_field(name=field_name, value=value, inline=False)

  if len(result) > MAX_IPO_FIELDS:
    embed.set_footer(text=f"Showing {MAX_IPO_FIELDS} of {len(result)} upcoming IPOs.")

  await ctx.send(embed=embed)


async def show_ipo_by_ticker(ctx, ticker: str):
  """
  Send an embed with details for a single upcoming IPO matching `ticker`.
  Searches a 90-day window so users can look ahead further than the default list.
  """
  ticker = ticker.upper()
  result = fetch_upcoming_ipos(days_ahead=90)

  if isinstance(result, str):
    embed = discord.Embed(title=f"Error: {result}", color=discord.Color.red())
    await ctx.send(embed=embed)
    return

  match = next((i for i in result if (i.get("symbol") or "").upper() == ticker), None)

  if not match:
    await ctx.send(f"`{ticker}` not found in the upcoming IPO calendar (next 90 days).")
    return

  embed = discord.Embed(
    title=f"{match.get('name', 'Unknown')} ({match.get('symbol', '?')})",
    color=discord.Color.green(),
  )
  embed.add_field(name="IPO Date", value=match.get("date", "TBD"), inline=True)
  embed.add_field(name="Exchange", value=match.get("exchange", "Unknown"), inline=True)
  embed.add_field(name="Status", value=match.get("status", "Unknown"), inline=True)
  embed.add_field(name="Price Range", value=_format_price_range(match.get("price", "")), inline=True)

  shares = match.get("numberOfShares")
  if shares:
    embed.add_field(name="Shares Offered", value=f"{shares:,}", inline=True)

  total_value = match.get("totalSharesValue")
  if total_value:
    embed.add_field(name="Total Offering Value", value=f"${total_value:,}", inline=True)

  await ctx.send(embed=embed)
