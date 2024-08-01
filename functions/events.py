import discord
from datetime import datetime, timedelta, timezone


async def create_event(ctx: discord.Interaction, date: str, time: str, description: str):
  # Parse date and time into a datetime object
  event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
  # Manually set the timezone to EST
  est = timezone(timedelta(hours=-5))
  event_datetime = event_datetime.replace(tzinfo=est)

  # Create event
  event = await ctx.guild.create_scheduled_event(
    name="New Event",
    description=description,
    start_time=event_datetime,
    end_time=event_datetime + timedelta(hours=2),  # Optional: set an appropriate end time
    entity_type=discord.EntityType.external,
    location="Discord",  # Change this to the actual location if needed
    privacy_level=discord.PrivacyLevel.guild_only  # Set the privacy level to guild only
  )
  await ctx.response.send_message(f"Event created! Check it out [here]({event.url})")


# Handle reactions for RSVP
# Catch reactions and update RSVP list
# async def on_reaction_add(reaction, user):
#   # Check if the reaction is on an event message and is a checkmark
#   if reaction.emoji == "✅" and not user.bot:
#     message = reaction.message
#     if message.embeds and "New Event Created" in message.embeds[0].title:
#       # Pull embed info
#       embed = message.embeds[0]
#       description = embed.description
#       date = embed.fields[0].value
#       time = embed.fields[1].value

#       # Update the embed to show the user's RSVP
#       if "RSVPs" not in embed.fields:
#         embed.add_field(name="RSVPs", value=user.display_name, inline=False)
#       else:
#         rsvp_field_index = 2
#         current_rsvps = embed.fields[rsvp_field_index].value
#         # Make sure the user is not already RSVP'd
#         if user.display_name not in current_rsvps:
#           current_rsvps += f", {user.display_name}"
#           embed.set_field_at(rsvp_field_index, name="RSVPs", value=current_rsvps, inline=False)

#       await message.edit(embed=embed)
