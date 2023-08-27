# PyPi Libraries
from discord import ButtonStyle, Interaction, Message, utils
from discord.ui import Button, View
from discord.ui.view import _walk_all_components, _component_to_item


class ClassJoinView(View):
	def __init__(self):
		super().__init__(timeout=None)

	def add_class(self, class_name:str) -> 'ClassJoinView':
		self.add_item(ClassButton(style=ButtonStyle.secondary, label=class_name, custom_id=f'join_{class_name}'))
		return self

	def remove_class(self, class_name:str) -> 'ClassJoinView':
		self.remove_item(f'join_{class_name}')
		return self

	@classmethod
	def from_message(cls, message:Message, /, *, timeout:float|None = 180.0) -> 'ClassJoinView':
		""" Converts a message's components into a :class:`ClassJoinView`.

			The :attr:`.Message.components` of a message are read-only
			and separate types from those in the ``discord.ui`` namespace.
			In order to modify and edit message components they must be
			converted into a :class:`View` first.

			Parameters
			----------
			message: :class:`.Message`
				The message with components to convert into a view.
			timeout: Optional[:class:`float`]
				The timeout of the converted view.

			Returns
			-------
			:class:`ClassJoinView`
				The converted view. This always returns a :class:`ClassJoinView` and not
				one of its subclasses.
		"""
		view = ClassJoinView()
		for component in _walk_all_components(message.components):
			view.add_item(_component_to_item(component))
		return view


class ClassButton(Button):
	async def callback(self, interaction:Interaction):
		# Trying to get the name of the class to join
		class_role = utils.get(interaction.guild.roles, name=self.label)
		# If we're not able to get the role, we let the user know
		if class_role is None:
			await interaction.response.send_message(f'Unable to find role `{self.label}`', ephemeral=True)
		# Assigning the role to the user
		else:
			# Checking to see if the user has this role already
			user_role = utils.get(interaction.user.roles, name=self.label)
			# If they do, we remove it
			if user_role is not None:
				await interaction.user.remove_roles(user_role)
				await interaction.response.send_message(f'You\'ve been removed from the `{self.label}` class!', ephemeral=True)

			# If they don't we add it
			else:
				await interaction.user.add_roles(class_role)
				await interaction.response.send_message(f'You\'ve joined the `{self.label}` class!', ephemeral=True)