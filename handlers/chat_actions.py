from aiogram import types
from dispatcher import dp, bot
import config
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
from time import time
import os
import pymysql

connection = pymysql.connect(
	host=config.host,
	port=config.port,
	user=config.user,
	password=config.password,
	database=config.db_name,
	cursorclass = pymysql.cursors.DictCursor
)
print('Connected successfully!')

class Memory(StatesGroup):
	photo_from_id = State()

# getting commands
@dp.message_handler(is_admin = True, commands=['start'], commands_prefix = '!/')
async def start(message: types.Message):
	await message.answer('Привет!<b> Я чат-менеджер</b>. Назначь меня <u><b>администратором</b></u>, что бы я мог функционировать в чате.\
						\nСписок моих комманд(комманды можно вводить через !): \n<b>/admins</b> - список администраторов чата\
						\n<b>/top_user</b> - Самый активный пользователь чата(только если включен сбор активности)\
						\n<u><b>Для администраторов:</b></u> \n<b>/photo</b> - установить фото чата\
						\n<b>/delphoto</b> - удалить фото чата\
						\n<b>/url</b> - ссылка-приглашение в беседу\
						\n<b>/pin</b> - закрепить сообщение\
						\n<b>/mute</b> <i>{time}</i> - замутить участника (время в секундах)\
						\n<b>/permmute</b> - замутить участника навсегда\
						\n<b>/ban</b> <i>{time}</i> - забанить участника (время в секундах)\
						\n<b>/permban</b> - забанить участника навсегда\
						\n<u><b>Для создателя</b></u>:\n<b>/setadmin</b> - назначит администратором чата\
						\n<b>/setprefix</b> <i>{title}</i> - установить подпись админу(санскрит).\
						\n<b>/collectstats</b> - начать сбор активности\
						\n<b>/dbadd</b> - начать сбор активности пользователя')

# get all admins in chat
@dp.message_handler(commands = ['admins'], commands_prefix = '!/')
async def get_admins(message : types.Message):
	admins = await bot.get_chat_administrators(message.chat.id)
	for admin in admins:
		await message.answer(f'{admin["user"]["first_name"]}\n@{admin["user"]["username"]}\n{admin["status"]}')

# set group photo
@dp.message_handler(is_admin = True, commands = ['photo'], commands_prefix='!/')
async def get_chat_photo(message : types.Message):
	await message.answer('Пришли мне фото для беседы.')
	await Memory.photo_from_id.set()

@dp.message_handler(is_admin = True, content_types=['photo'], state = Memory.photo_from_id)
async def set_chat_photo(message : types.Message, state = FSMContext):
	await message.photo[-1].download(f'{message.from_user.id}.jpg')
	await bot.set_chat_photo(message.chat.id, InputFile(f'{message.from_user.id}.jpg'))
	os.remove(f'{message.from_user.id}.jpg')
	await message.delete()
	await state.finish()

# delete group photo
@dp.message_handler(is_admin = True, commands = ['delphoto'], commands_prefix ='!/')
async def del_photo(message : types.Message):
	try:
		await bot.delete_chat_photo(message.chat.id)
		await message.answer('Фото было удалено.')
	except Exception as ex:
		print(ex)
		await message.answer('Что-то пошло не так.')

# get invite url
@dp.message_handler(is_admin = True, commands=['url'], commands_prefix = '!/')
async def get_url(message : types.Message):
	url = await bot.export_chat_invite_link(message.chat.id)
	await message.reply(url)

# pin chat message
@dp.message_handler(is_admin = True, commands='pin', commands_prefix = '!/')
async def pin(message : types.Message):
	if not message.reply_to_message:
		await message.answer('Эта команда должна быть ответом на сообщение.')
		return

	await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
	await message.delete()

# auto mute
@dp.message_handler(text_contains='Плохое слово')
async def restrict_user(message : types.Message):
	await bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date = time()+60)
	await message.delete()

#permanent mute
@dp.message_handler(is_admin = True, commands=['permmute'], commands_prefix = '!/')
async def mute(message : types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение.')
		return

	await message.delete()

	try:
		await bot.restrict_chat_member(message.chat.id, user_id = message.reply_to_message.from_user.id)
		await message.answer('Пользователь принял обет молчания.')
	except:
		await message.answer('Бог не может быть наказан или вы неправильно прочитали заклинание.')

#time mute
@dp.message_handler(is_admin = True, commands=['mute'], commands_prefix = '!/')
async def mute(message : types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение.')
		return

	await message.delete()

	try:
		mute_time = int(message.text.split(' ')[1])
		await bot.restrict_chat_member(message.chat.id, user_id = message.reply_to_message.from_user.id, until_date = time() + mute_time)
		await message.answer('Пользователь был замьючен при помощи Каина.')
	except:
		await message.answer('Бог не может быть наказан или вы неправильно прочитали заклинание.')

# ban user
@dp.message_handler(is_admin = True, commands=['ban'], commands_prefix = '!/')
async def ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение.')
		return

	await message.delete()

	try:
		ban_time = int(message.text.split(' ')[1])
		await message.bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id, until_date = time() + ban_time)
		await message.answer('Пользователь попал в клетку к Люциферу. Пожелаем удачи!')
	except:
		await message.reply_to_message.reply('Бог не может быть наказан или вы не так прочитали заклинание.')

# permanent ban
@dp.message_handler(is_admin = True, commands=['permban'], commands_prefix = '!/')
async def ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение.')
		return

	await message.delete()

	try:
		await message.bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
		await message.answer('Пользователь попал в пустоту. Пожелаем удачи!')
	except:
		await message.reply_to_message.reply('Бог не может быть наказан или вы не так прочитали заклинание.')

# set administrator
@dp.message_handler(is_owner = True, commands = ['setadmin'], commands_prefix = '!/')
async def set_admin(message : types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение.')
		return

	try:
		await bot.promote_chat_member(chat_id = message.chat.id, user_id = message.reply_to_message.from_user.id, can_delete_messages = True, can_manage_voice_chats = True, can_restrict_members = True, can_invite_users = True)
		await message.answer('Пользователь возвысился и стал ангелом. Поздравляем!')
	except:
		await message.answer('Похоже, пользователь уже является ангелом. Или вы не так прочитали заклинание.')

# set administrator title
@dp.message_handler(commands=['setprefix'], commands_prefix='!/')
async def set_title(message : types.Message):
	if not message.reply_to_message:
		await message.reply('Эта команда должна быть ответом на сообщение')
		return

	try:
		title = str(message.text.split(' ')[1])
		await bot.set_chat_administrator_custom_title(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id, custom_title = title)
		await message.answer(f'Санскрит "{title}" установлен.')
	except:
		await message.answer('Что-то пошло не так. Попробуйте ещё раз или измените заклинание.')

# delete 'user_joined' notification and add user to db
@dp.message_handler(content_types=['new_chat_members'])
async def del_new_user_message(message : types.Message):
	await message.delete()
	with connection.cursor() as cursor:
		cursor.execute(f'INSERT INTO `{message.chat.id}`(user_id, words_number) VALUES ({message.new_chat_members[0].id}, 0);')
		connection.commit()

# start collecting stats
@dp.message_handler(is_owner = True, commands=['collectstats'], commands_prefix = '!/')
async def db(message : types.Message):
	with connection.cursor() as cursor:
		try:
			cursor.execute(f"CREATE TABLE `{message.chat.id}`(user_id varchar(50) Unique, words_number varchar(20));")
			await message.answer('Сбор статистики начался.')
		except pymysql.err.OperationalError:
			await message.answer('Что-то пошло не так. Возможно данные уже собираются.')
	
		cursor.execute(f'INSERT INTO `{message.chat.id}`(user_id, words_number) VALUES ({message.from_user.id}, 0);')
		connection.commit()

# add user to db
@dp.message_handler(is_admin = True, commands=['dbadd'], commands_prefix = '!/')
async def add_to_db(message : types.Message):
	if not message.reply_to_message:
		await message.answer('Эта команда должна быть ответом на сообщение')
		return

	with connection.cursor() as cursor:
		try:
			cursor.execute(f'INSERT INTO `{message.chat.id}`(user_id, words_number) VALUES ({message.reply_to_message.from_user.id}, 0);')
			connection.commit()
			await message.answer('Пользователь успешно добавлен в подсчёт статистики.')
		except:
			await message.answer('Что-то пошло не так или пользователь уже есть в бд.')

# get top activity user
@dp.message_handler(commands=['top_user'], commands_prefix = '!/')
async def get_user(message : types.Message):
	with connection.cursor() as cursor:
		try:
			cursor.execute(f'SELECT * FROM `{message.chat.id}` ORDER BY words_number DESC LIMIT 1')
			db_user = cursor.fetchall()[0]
			cur_user = await bot.get_chat_member(message.chat.id, db_user['user_id'])
			await message.answer(f'Самый активный пользователь чата:\
								\n<b>{cur_user["user"]["first_name"]}\
								\n@{cur_user["user"]["username"]}</b>\
								\n<em>Кол-во слов: </em>{db_user["words_number"]}')
		except pymysql.err.ProgrammingError:
			await message.answer('Включите сбор активности.')

# filling table
@dp.message_handler()
async def db_update(message : types.Message):
	words = message.text.split(' ')
	with connection.cursor() as cursor:
		cursor.execute(f'SELECT * from `{message.chat.id}` WHERE user_id = {message.from_user.id}')
		all_words = int(cursor.fetchall()[0]['words_number']) + len(words)
		cursor.execute(f'UPDATE `{message.chat.id}` SET words_number = {all_words} where user_id = {message.from_user.id}')
		connection.commit()