# PyPi Libraries
from discord import utils, Role, CategoryChannel, Embed, PermissionOverwrite
from discord.ext.commands import Context, Cog
from discord.commands import SlashCommandGroup

# Local Libraries
# pylint: disable=relative-beyond-top-level
from .utils import is_authorized, create_status_embed
from .Status import Status
from .ClassJoinView import ClassJoinView
# Collecting our config information and providing some with shorter names
from . import config
NOPE = config.INVALID_EMOJI
YEP = config.VALID_EMOJI


class Classes(Cog):
	# Creates a group of commands for the bot named class
	group = SlashCommandGroup('class', 'Commands for managing classes.')

	def __init__(self, bot):
		self.bot = bot
		self._status = Status()
		self._status_messages = []
		self._status_error = False

	@group.command()
	@is_authorized()
	async def new(self, ctx:Context, class_name:str, classroom_template:CategoryChannel=None):
		# Resetting our status for a new command
		self._status.reset()

		# Getting our default classroom template if we didn't get one. Doesn't matter if it's valid as we'll check later
		if classroom_template is None:
			classroom_template = utils.get(ctx.guild.categories, name=config.CLASSROOM_TEMPLATE)

		# Checking to see if we can create our classroom
		await self._classroom_creation_check(ctx, class_name, classroom_template)

		# If we don't have errors, we continue to create our classroom
		if self._status.errored == False:
			# Create our role first
			class_role = await ctx.guild.create_role(name=class_name, reason='New class created with name {name}')
			# Then we create our classroom
			await self._create_classroom(ctx, class_name, class_role)
			# Then we add our class to the join menu
			await self._manage_join_menu(ctx, class_name, remove=False)

		# Give status message to user
		await ctx.respond(
			embed=self._status.embed('Classroom Creation'),
			ephemeral=True,
			# ephemeral=self._status.errored,
		)
		return

	async def _classroom_creation_check(self, ctx:Context, class_name:str, classroom_template:CategoryChannel):
		# Role check
		# If role exists, we error
		if utils.get(ctx.guild.roles, name=class_name) is not None:
			self._status.error(f'Role `{class_name}` already exists. Delete role and try again.')

		# Classroom check
		# If classroom exists, we error
		if utils.get(ctx.guild.categories, name=class_name) is not None:
			self._status.error(f'Category `{class_name}` already exists. Delete classroom and try again.')
		# If template doesn't exist, we error
		if classroom_template is None:
			self._status.error(f'Category `{classroom_template}` doesn\'t exist. Create template and try again.')

		# Join menu check
		# If assignments channel doesn't exist, we error
		assignments_channel = utils.get(ctx.guild.channels, name=config.CLASSROOM_ASSIGNMENTS_CHANNEL)
		if assignments_channel is None:
			self._status.error(f'Channel `{config.CLASSROOM_ASSIGNMENTS_CHANNEL}` doesn\'t exist. Create channel and try again.')
		else:
			# If the first message in the assignments channel isn't ours, we error
			channel_history = [_ async for _ in assignments_channel.history(limit=1, oldest_first=True)]
			if len(channel_history) > 0 and channel_history[0].author != self.bot.user:
				self._status.error(f'Channel `{config.CLASSROOM_ASSIGNMENTS_CHANNEL}`\'s first message isn\'t mine. Please clear the channel to allow my message to be first, and I\'ll create the role selection.')

	async def _create_classroom(self, ctx:Context, class_name:str, class_role:Role):
		# Getting the template that we'll be basing our new classroom on
		template = utils.get(ctx.guild.categories, name=config.CLASSROOM_TEMPLATE)

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

	async def _manage_join_menu(self, ctx:Context, class_name:str, remove:bool=False):
		# We've already checked to see if the assignments channel exists, so we can just get it
		assignments_channel = utils.get(ctx.guild.channels, name=config.CLASSROOM_ASSIGNMENTS_CHANNEL)

		# If there is no first message, we create one
		assignments_message = [_ async for _ in assignments_channel.history(limit=1, oldest_first=True)]
		if not assignments_message:
			assignments_message = await assignments_channel.send(
				embed=Embed(
					title='Class Join Menu',
					description='Click the buttons below to join or leave a class.',
				),
				view=ClassJoinView(),
			)
		else :
			assignments_message = assignments_message[0]

		# Now that we have a message, we'll manage our join menu
		if remove:
			new_view = ClassJoinView.from_message(assignments_message).remove_class(class_name)
		else:
			new_view = ClassJoinView.from_message(assignments_message).add_class(class_name)
		# Updating the message with our new view
		await assignments_message.edit(view=new_view)


	@group.command()
	@is_authorized()
	async def delete(self, ctx:Context, class_name:str):
		# Attempting to delete the role for this class
		role = utils.get(ctx.guild.roles, name=class_name)
		message = ''
		if role is None:
			message += f'{NOPE} Couln\'t find `{class_name}` role to delete.\n'
		else:
			message += f'{YEP} Successfully deleted `{class_name}` role.\n'
			await role.delete(reason='Classroom no longer needed')

		# Attempting to remove the classroom for this class
		if await self.deleteClassroom(utils.get(ctx.guild.categories, name=class_name)):
			message += f'{YEP} Successfully deleted `{class_name}` classroom.\n'
		else:
			message += f'{NOPE} Couln\'t find `{class_name}` classroom to delete.\n'

		await ctx.respond(
			embed=create_status_embed(message, title='Classroom Deletion Status'),
			ephemeral=True,
		)


	async def deleteClassroom(self, classroom:CategoryChannel):
		# If our search turned up nothing, we return without question
		if classroom is None:
			return False

		# Iterating through the channels in the classroom and deleting them
		for channel in classroom.channels:
			await channel.delete(reason='Classroom no longer needed')

		# Delete the classroom itself
		await classroom.delete(reason='Classroom no longer needed')

		return True
