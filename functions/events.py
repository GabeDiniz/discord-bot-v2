import discord

async def create_event(ctx: discord.Interaction, date: str, time: str, description: str):
  # Create an embed for the event
  embed = discord.Embed(
    title="New Event Created",
    description=description,
    color=discord.Color.blue()
  )
  embed.add_field(name="Date", value=date, inline=True)
  embed.add_field(name="Time", value=time, inline=True)
  embed.set_footer(text="React with ✅ to RSVP")

  # Send the embed message
  await ctx.response.send_message(embed=embed)
  # Fetch the sent message to add a reaction
  message = await ctx.original_response()
  await message.add_reaction("✅")

# Handle reactions for RSVP
async def on_reaction_add(reaction, user):
  # Check if the reaction is on an event message and is a checkmark
  if reaction.emoji == "✅" and not user.bot:
    message = reaction.message
    if message.embeds and "New Event Created" in message.embeds[0].title:
      # Extract information from the embed
      embed = message.embeds[0]
      description = embed.description
      date = embed.fields[0].value
      time = embed.fields[1].value

      # Update the embed to show the user's RSVP
      if "RSVPs" not in embed.fields:
        embed.add_field(name="RSVPs", value=user.display_name, inline=False)
      else:
        rsvp_field_index = 2
        current_rsvps = embed.fields[rsvp_field_index].value
        if user.display_name not in current_rsvps:
          current_rsvps += f", {user.display_name}"
          embed.set_field_at(rsvp_field_index, name="RSVPs", value=current_rsvps, inline=False)

      await message.edit(embed=embed)
