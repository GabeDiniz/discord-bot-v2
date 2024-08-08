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