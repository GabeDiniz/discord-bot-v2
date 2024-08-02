import discord   # pip install discord


async def create_poll(ctx, message):
  # CATCH EMPTY POLL
  if message.strip() == "":
    embed = discord.Embed(
      title=":bangbang: E R R O R",
      description="Your poll message is empty. Please add your poll question after !poll",
      color=discord.Color.red()
    )
    await message.channel.send(embed=embed)
    return

  embed = discord.Embed(
    title=f"Poll: {message}",
    description="React to vote",
    color=discord.Color.green()
  )

  # If ctx is an interaction, respond to it
  # This sends the confirmation message to the user
  if isinstance(ctx, discord.Interaction):
    await ctx.response.send_message("Poll created!", ephemeral=True)

  # print(f"[ LOG ] creating poll with message: {message}\n")
  await ctx.channel.send(embed=embed)
  # for emoji in emojis:
  #   await msg.add_reaction(emoji)
  
  