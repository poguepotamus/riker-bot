# PyPi Libraries
from dotenv import dotenv_values
from discord import Intents
from discord.ext import commands

# Local Libraries
# pylint: disable=relative-beyond-top-level
# from . import config, is_authorized, createStatusEmbed, createClassroom, deleteClassroom
from .Classes import Classes
# Creating some global bindings for easy access


# Using guide https://realpython.com/how-to-make-a-discord-bot-python/#welcoming-new-members
# Discord API docs https://discordpy.readthedocs.io/en/stable/api.html
# Context documentation https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context

# Using the bot commands method of creating a bot
# Relevant documentation https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#
# Registering the bot. This lets us use the @bot decorator instead of creating a whole new bot
bot = commands.Bot(
    command_prefix='!',
    intents=Intents().all(),
)

# Adding our classes commands to the bot
bot.add_cog(Classes(bot))

bot.run(dotenv_values('.env')['DISCORD_TOKEN'])