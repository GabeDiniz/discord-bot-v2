import discord   # pip install discord

'''
DISCORD EMOJIS
✅ :white_check_mark:
❌ :x:
🤷‍♂️ :person_shrugging: 
'''
emojis = ["✅", "❌", "🤷‍♂️"]

async def create_poll(message, client):
  # PARSE THROUGH MESSAGE
  poll = message.content[6:]

  embed = discord.Embed(
    title=f"Poll: {poll}",
    description="React to vote",
    color=discord.Color.green()
  )

  print(f"[ LOG ] creating poll with message: {poll}\n")
  msg = await message.channel.send(embed=embed)
  for emoji in emojis:
    await msg.add_reaction(emoji)
  
  