# Standard LIbraries
# from json import dumps as json_dumps
from dotenv import dotenv_values

# PyPi Libraries
from discord import Intents
from discord.ext import commands


CLASSROOM_TEMPLATE = 'Class-Template'


# Using guide https://realpython.com/how-to-make-a-discord-bot-python/#welcoming-new-members
# Discord API docs https://discordpy.readthedocs.io/en/stable/api.html
# Context documentation https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context

# Using the bot commands method of creating a bot
# Relevant documentation https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#
# Registering the bot. This lets us use the @bot decorator instead of creating a whole new bot
bot = commands.Bot(command_prefix='/', intents=Intents().all())


@bot.command()
async def jasperPing(ctx):
    await ctx.send(f'{bot.user.name} has connected to Discord!')

bot.run(dotenv_values('.env')['DISCORD_TOKEN'])