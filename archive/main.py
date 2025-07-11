# This file holds functions main.py functions (commands) that are deprecated
#   or no longer useful.

# ========================================
# SLASH COMMANDS
# ========================================


# #####################
# [DEPRECATED]
# @bot.tree.command(name="poll", description="Create a poll", guild=None)
# async def poll_slash_command(interaction: discord.Interaction, question: str):
#   await polls.create_poll(interaction, question)

# #####################
# WIP: NOT FUNCTIONING AS IT COSTS MONEY
# @bot.command(name='gpt')
# async def chatgpt(ctx, *, query: str):
#   await ctx.typing()  # Show typing indicator while processing

#   try:
#     response = gptClient.chat.completions.create(
#       model="gpt-3.5-turbo",
#       messages=[
#         {"role": "user", "content": query}
#       ]
#     )
#     print(response)
#     answer = response.choices[0].message
#     await ctx.send(answer)
#   except Exception as e:
#     await ctx.send(f"An error occurred: {e}")
