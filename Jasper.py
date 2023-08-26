# Standard LIbraries
# from json import dumps as json_dumps
from dotenv import dotenv_values

# PyPi Libraries
from discord import Intents, utils, CategoryChannel, Embed, PermissionOverwrite
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
async def newClass(ctx, class_name:str):
	message = ''

	# Creating a new role for the class
	try:
		class_role = await ctx.guild.create_role(name=class_name, reason='New class created with name {name}')
	except Exception:
		message += f':triangular_flag_on_post: Couln\'t create `{class_name}` role.\n'
	else:
		message += f':white_check_mark: Successfully created `{class_name}` role.\n'

	# Creating the new classroom for the class
	# @TODO Add error handling for if the classroom already exists
	# @TODO Add error handling for if the classroom can't be created
	# @TODO Add error handling for if the template doesn't exist
	try:
		await createClassroom(ctx, class_name, class_role)
	except Exception:
		message += f':triangular_flag_on_post: Couln\'t create `{class_name}` classroom.\n'
	else:
		message += f':white_check_mark: Successfully created `{class_name}` classroom.\n'

	# Sending our status message
	await ctx.send(embed=createStatusEmbed(message, title='Classroom Creation Status'))


@bot.command()
@is_authorized()
async def deleteClass(ctx, class_name:str):
	# Attempting to delete the role for this class
	role = utils.get(ctx.guild.roles, name=class_name)
	message = ''
	if role is None:
		message += f':triangular_flag_on_post: Couln\'t find `{class_name}` role to delete.\n'
	else:
		message += f':white_check_mark: Successfully deleted `{class_name}` role.\n'
		await role.delete(reason='Classroom no longer needed')

	# Attempting to remove the classroom for this class
	if await deleteClassroom(ctx, utils.get(ctx.guild.categories, name=class_name)):
		message += f':white_check_mark: Successfully deleted `{class_name}` classroom.\n'
	else:
		message += f':triangular_flag_on_post: Couln\'t find `{class_name}` classroom to delete.\n'

	await ctx.send(embed=createStatusEmbed(message, title='Classroom Deletion Status'))


async def createClassroom(ctx, class_name, class_role):
	# Getting the template that we'll be basing our new classroom on
	template = utils.get(ctx.guild.categories, name=CLASSROOM_TEMPLATE)

	# Creating the new classroom
	role_permissions = template.overwrites
	role_permissions[class_role] = PermissionOverwrite(view_channel=True)
	classroom = await ctx.guild.create_category(class_name,
		overwrites=role_permissions,
		reason='New class created with name {name}',
		position=template.position - 1, # Putting our new category right above the template
	)

	# Creating all the other channels from our template dynamically
	for channel in template.channels:
		new_channel = await channel.clone(reason=f'New class created with name {class_name}', name=channel.name.replace('_name_', class_name))
		await new_channel.edit(category=classroom, sync_permissions=True)

	# Returning the new class category
	return classroom


async def deleteClassroom(_, classroom:CategoryChannel):
	# If our search turned up nothing, we return without question
	if classroom is None:
		return False

	# Iterating through the channels in the classroom and deleting them
	for channel in classroom.channels:
		await channel.delete(reason='Classroom no longer needed')

	# Delete the classroom itself
	await classroom.delete(reason='Classroom no longer needed')

	return True


def createStatusEmbed(message=None, valid=':white_check_mark:', invalid=':triangular_flag_on_post:', **kwargs):
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


@bot.command()
@is_authorized()
async def jasperPing(ctx):
    await ctx.send(f'{bot.user.name} has connected to Discord!')

bot.run(dotenv_values('.env')['DISCORD_TOKEN'])