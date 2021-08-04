from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config

class IsAdminFilter(BoundFilter):
	key = 'is_admin'

	def __init__(self, is_admin):
		self.is_admin = is_admin

	async def check(self, message : types.Message):
		member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
		return member.is_chat_admin() == self.is_admin

class IsOwnerFilter(BoundFilter):
	key = 'is_owner'

	def __init__(self, is_owner):
		self.is_owner = is_owner

	async def check(self, message : types.Message):
		return message.from_user.id == config.BOT_OWNER