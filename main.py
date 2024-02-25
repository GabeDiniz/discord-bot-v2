from discord import Intents, Client
import discord   # pip install discord

# ========================================
# Response Features
# ========================================
import responses
import steam
import fortnite

# Fetch Credentials from local .env variables 
from decouple import config
# Constants
BOT_KEY = config('DISCORD_BOT_KEY')

def run_bot(BOT_KEY: str):
  # Basic setup
  # Gets message content
  intents = Intents.default()
  intents.message_content = True
  # Client makes the request
  client = Client(intents=intents)

  knowledge: dict = responses.load_knowledge('./knowledge/knowledge2.json')
  print(f"Knowledge: {knowledge}")

  @client.event
  # Perform the code as soon as the bot is started
  async def on_ready():
    print(f"{client.user} is now running!")
  
  @client.event
  # Every time a new message appears -> handle msg
  async def on_message(message):
    # Make sure the message being read is not from the bot
    if message.author == client.user:
      return
    
    # ========================================
    # Handle Responses
    # ========================================
    # Check for specific user
    # if str(message.author) == "username here":
    #   response: str = "Oh hello there... I've been expecting you"
    
    response = None   # Default Bot Response -> None
    # If Message is sent by a user
    if message.content:
      print(f'({message.channel}) {message.author}: "{message.content}"')
      
      # Handle !help command
      if message.content.startswith("!help"):
        embed = discord.Embed(
            title='Help',
            description='This is a help message!',
            color=discord.Color.blue()
        )
        # Add fields to the embed (optional)
        embed.add_field(name='!cs2 <name>', value='Displays cs2 stats', inline=False)
        embed.add_field(name='Command 2', value='Description 2', inline=False)
        
        # Send the embed message to the same channel where the command was issued
        await message.channel.send(embed=embed)
      elif message.content.startswith("!cs2"):
        embed = steam.get_user_stats(message.content)
        await message.channel.send(embed=embed)
      elif message.content.startswith("!fn shop"):
        embed = fortnite.get_shop_items()
        await message.channel.send(embed=embed)
      else:
        response: str = responses.get_response(message.content, knowledge=knowledge)
      if response:
        # Sending message
        print(response)
        await message.channel.send(response)
      
    # Potential error: i.e., missing permissions to access message.content
    else:
      print("[Error] Could not read the message. Make sure you have intents enabled!")

  client.run(token=BOT_KEY)

if __name__ == "__main__":
  run_bot(BOT_KEY=BOT_KEY)