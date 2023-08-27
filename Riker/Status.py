# PyPi Libraries
from discord import Embed

# Local Libraries
from . import config

class Status:
	def __init__(self):
		self._messages = []
		self.errored = False

	def reset(self):
		self._messages = []
		self.errored = False

	def error(self, message:str):
		self.errored = True
		self._messages.append(f'{config.INVALID_EMOJI} {message}')

	def success(self, message:str):
		self._messages.append(f'{config.VALID_EMOJI} {message}')

	def embed(self, task, **kwargs):
		# First, we color our embed depending on if we have an error
		if self.errored:
			kwargs['color'] = 0x992222
		else:
			kwargs['color'] = 0x229922

		# Construct our description from our messages
		kwargs['description'] = '\n'.join(self._messages)
		# Give a title depending on if we have an error
		kwargs['title'] = f'{task} {"Failed" if self.errored else "Succeeded"}'
		# Next, we'll construct our embed and add our messages
		return Embed(**kwargs)
