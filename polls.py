import discord


'''
DISCORD EMOJIS
✅ :white_check_mark:
❌ :x:
🤷‍♂️ :person_shrugging: 
'''


def create_poll(message, client):
  # PARSE THROUGH MESSAGE
  poll = message.content.strip("!poll ")

  # CHECK CASES
  if poll.startswith("online"):
    # Handle Who's online tonight? poll
    pass

  pass