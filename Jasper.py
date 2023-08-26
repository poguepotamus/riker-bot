# Standard LIbraries
# from json import dumps as json_dumps
from dotenv import dotenv_values

# PyPi Libraries
from discord import Intents, utils, CategoryChannel, Embed
from discord.ext import commands


CLASSROOM_TEMPLATE = 'Class-Template'


# Using guide https://realpython.com/how-to-make-a-discord-bot-python/#welcoming-new-members
# Discord API docs https://discordpy.readthedocs.io/en/stable/api.html
# Context documentation https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context

# Using the bot commands method of creating a bot
# Relevant documentation https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#
# Registering the bot. This lets us use the @bot decorator instead of creating a whole new bot
bot = commands.Bot(command_prefix='/', intents=Intents().all())


def is_authorized():
	# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#parameter-metadata
	async def predicate(ctx):
		return any([
			ctx.author.id == ctx.guild.owner_id, # Checking if the user is guild owner
			ctx.author.guild_permissions.administrator, # Checking if the user has admin perms
			ctx.author.roles[-1].position > utils.get(ctx.guild.roles, name='Jasper').position, # Checking if user has a role above Jasper
		])
	return commands.check(predicate)


@bot.command()
@is_authorized()
async def jasperPing(ctx):
    await ctx.send(f'{bot.user.name} has connected to Discord!')

bot.run(dotenv_values('.env')['DISCORD_TOKEN'])