# PyPi Libraries
from discord import utils, Embed
from discord.ext import commands

# Local Libraries
from . import config


def is_authorized():
	# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#parameter-metadata
	async def predicate(ctx:commands.Context):
		return any([
			ctx.author.id == ctx.guild.owner_id, # Checking if the user is guild owner
			ctx.author.guild_permissions.administrator, # Checking if the user has admin perms
			ctx.author.roles[-1].position > utils.get(ctx.guild.roles, name='Jasper').position, # Checking if user has a role above Jasper
		])
	return commands.check(predicate)


def create_status_embed(message=None, valid=config.VALID_EMOJI, invalid=config.INVALID_EMOJI, **kwargs):
	# Message is our description if we don't have one
	if 'description' not in kwargs.keys() and message is not None:
		kwargs['description'] = message

	# Determining what color we use for the embed
	if 'color' not in kwargs.keys():
		# If we have all valid lines, we use green
		if kwargs['description'].count(valid) == len(kwargs['description'].strip().split('\n')):
			kwargs['color'] = 0x229922
		# If we have all invalid lines, we use red
		elif kwargs['description'].count(invalid) == len(kwargs['description'].strip().split('\n')):
			kwargs['color'] = 0x992222
		# If we have a mix, we use orange
		else:
			kwargs['color'] = 0xdd8822

	# Sending a message to the user about what happened
	return Embed(
		**kwargs,
	)