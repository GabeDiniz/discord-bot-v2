from discord import Intents, Client
import discord   # pip install discord

# ========================================
# Response Features
# ========================================
import responses
import steam
import fortnite
import playmusic

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
          # title='Cpt. Bot Commands',
          color=discord.Color.red()
        )
        # Add fields to the embed (optional)
        embed.set_author(name="King Bob's Commands", url="https://github.com/GabeDiniz", icon_url="https://i.imgur.com/sRmJYmJ.jpeg")
        embed.set_thumbnail(url="https://imgur.com/IvB8ln5.jpeg")
        embed.add_field(name='CS2 Stats', value='`!cs2 <name>`', inline=True)
        embed.add_field(name='Today\'s Fortnite Shop', value='`!fn shop`', inline=True)
        
        # Send the embed message to the same channel where the command was issued
        await message.channel.send(embed=embed)
      
      # COMMAND: CS2 Statistics 
      elif message.content.startswith("!cs2"):
        embed = steam.get_user_stats(message.content)
        await message.channel.send(embed=embed)
      # COMMAND: Fortnite Shop
      elif message.content.startswith("!fn shop"):
        embed = fortnite.get_shop_items()
        await message.channel.send(embed=embed)
      elif message.content.startswith("!play"):
        embed = await playmusic.playmusic(message, client)
        await message.channel.send(embed=embed)
      elif message.content.startswith("!leave"):
        embed = await playmusic.stopmusic(message)
        await message.channel.send(embed=embed)
      # COMMAND: Basic text responses
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