import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import bot, dp
from aiogram.utils.exceptions import BotBlocked

# DB
from database import postgres_db

# Keyboards
from keyboards import admin_kb, user_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# FSM
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup



async def admin_panel_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Админ панель:', parse_mode='html', reply_markup=admin_kb.menu_kb)


async def awaiting_verification_command(message: types.Message):
    files = await postgres_db.get_unverified_files()

    if files:
        for file in files:
            await bot.send_document(message.chat.id, file[1], reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Толықтыру', callback_data=f'complement {file[3]}')).add(InlineKeyboardButton('Жою', callback_data=f'delete {file[0]} {file[3]}')))
    else:
        await bot.send_message(message.chat.id, 'Тізім бос')


async def add_book_command(message: types.Message):
    await UploadBook.title.set()
    UploadBook.gear = 1

    await bot.send_message(message.chat.id, 'Кітаптың атын енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def pin_book_command(message: types.Message):
    await PinOrDeleteBook.book_id.set()
    PinOrDeleteBook.gear = 1

    await bot.send_message(message.chat.id, 'Кітаптың ID енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def delete_book_command(message: types.Message):
    await PinOrDeleteBook.book_id.set()
    PinOrDeleteBook.gear = 2

    await bot.send_message(message.chat.id, 'Жойғыңыз келетін кітаптың ID енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def statistics_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Бұл бөлім жасалу сатысында...')


async def mailing_command(message: types.Message):
    await Mailing.text.set()
    await bot.send_message(message.chat.id, 'Тарату мәтінін енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def back_command(message: types.message):
    await bot.send_message(message.chat.id, 'Бас мізір', parse_mode='html', reply_markup=user_kb.menu_with_admin_panel_kb)


async def complement_callback(callback_query: types.CallbackQuery):
    book_id = callback_query.data.replace('complement ', '')

    await callback_query.answer(text='Кітапты толықтыру', show_alert=False)

    await UploadBook.title.set()
    UploadBook.book_id = book_id
    UploadBook.gear = 2

    await bot.send_message(callback_query.message.chat.id, 'Кітаптың атын енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def delete_callback(callback_query: types.CallbackQuery):
    file_id, book_id = callback_query.data.replace('delete ', '').split(' ')

    await postgres_db.delete_book(book_id)
    await callback_query.answer(text='Жойылды', show_alert=False)
    await callback_query.message.delete()


class UploadBook(StatesGroup):
    book_id = None
    gear = None

    title = State()
    description = State()
    author = State()
    genre = State()
    book = State()


class PinOrDeleteBook(StatesGroup):
    gear = None

    book_id = State()
    book_file = State()


class Mailing(StatesGroup):
    text = State()
    type = State()


async def cancel_upload_book_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == None:
        return

    await state.finish()

    await bot.send_message(message.chat.id, 'Функция жойылды', parse_mode='html', reply_markup=admin_kb.menu_kb)


async def set_title(message: types.Message, state: FSMContext):
    gear = UploadBook.gear

    if gear == 1:
        print("Gear 1")
        async with state.proxy() as data:
            data['title'] = message.text

        await UploadBook.next()
        await bot.send_message(message.chat.id, 'Кітаптың берілгенің енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        print("Gear 2")
        async with state.proxy() as data:
            data['book_id'] = UploadBook.book_id
            data['title'] = message.text

        await UploadBook.next()
        await bot.send_message(message.chat.id, 'Кітаптың берілгенің енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)



async def set_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    await UploadBook.next()
    await bot.send_message(message.chat.id, 'Кітаптың авторын енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def set_author(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['author'] = message.text

    await UploadBook.next()
    await bot.send_message(message.chat.id, 'Кітаптің жанрын таңдаңыз:', parse_mode='html', reply_markup=admin_kb.genre_kb)


async def set_genre(message: types.Message, state: FSMContext):
    gear = UploadBook.gear
    genres = await postgres_db.get_genres()

    if message.text in genres:
        async with state.proxy() as data:
            genre_id = await postgres_db.get_genre_id(message.text)
            data['genre'] = genre_id

        if gear == 2:
            data = list(data.values())
            await postgres_db.update_book(data)

            # Gear = 2
            await state.finish()
            await bot.send_message(message.chat.id, 'Кітап сәтті толықтырылды.', parse_mode='html', reply_markup=admin_kb.menu_kb)
        else:
            # Gear = 3
            await UploadBook.next()
            await bot.send_message(message.chat.id, 'Төменге жіберетін кітапты енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        await bot.send_message(message.chat.id, 'Кітаптің жанрын таңдаңыз:', parse_mode='html', reply_markup=admin_kb.genre_kb)


async def set_book(message: types.Message, state: FSMContext):
    gear = UploadBook.gear

    tg_id = message.chat.id
    user_id = await postgres_db.get_user_id(tg_id)
    file_id = message.document.file_id
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx']:
        async with state.proxy() as data:
            data['user_id'] = user_id
            data = list(data.values())
            book_id = await postgres_db.add_book(data)

        await postgres_db.add_file(file_id, file_type, book_id)

        await state.finish()
        await bot.send_message(message.chat.id, 'Кітап сәтті қосылды.', parse_mode='html', reply_markup=admin_kb.menu_kb)
    else:
        await bot.send_message(message.chat.id, 'Кайта жберініз')


# Pin Or Delete book FSM
async def set_book_id(message: types.Message, state=FSMContext):
    if PinOrDeleteBook.gear == 1:
        async with state.proxy() as data:
            data['book_id'] = int(message.text)

        await PinOrDeleteBook.next()
        await bot.send_message(message.chat.id, 'Кітапты тіркеңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        book_id = int(message.text)
        await postgres_db.delete_book(book_id)

        await state.finish()
        await bot.send_message(message.chat.id, 'Кітап сәтті жойылды!', parse_mode='html', reply_markup=admin_kb.menu_kb)


async def set_book_file(message: types.Message, state=FSMContext):
    file_id = message.document.file_id
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx']:
        async with state.proxy() as data:
            book_id = data['book_id']

        await postgres_db.add_file(file_id, file_type, book_id)


        await state.finish()
        await bot.send_message(message.chat.id, 'Кітап сәтті қосылды!', parse_mode='html', reply_markup=admin_kb.menu_kb)
    else:
        await bot.send_message(message.chat.id, 'Кітапты қайта жберініз')


async def mailing_text(message: types.message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    await Mailing.next()
    await bot.send_message(message.chat.id, 'Тарату түрін таңдаңыз:', parse_mode='html', reply_markup=admin_kb.mailing_kb)



async def mailing_type(message: types.message, state: FSMContext):
    async with state.proxy() as data:
        mailing_text = data['text']

    if message.text == '📩 Өзіме жберу':
        await state.finish()
        await bot.send_message(message.chat.id, mailing_text, parse_mode='html', reply_markup=admin_kb.menu_kb)
    elif message.text == '💌 Тарату':
        users_id = await postgres_db.get_users_id()
        number_of_users = len(users_id)
        number_of_failed_attempts = 0

        for user_id in users_id:
            try:
                await bot.send_message(user_id[0], mailing_text, parse_mode='html')
            except BotBlocked:
                number_of_failed_attempts += 1
                await asyncio.sleep(1)

        await state.finish()
        await bot.send_message(message.chat.id, f'Тарату сәтті аяқталды 🙌 ({number_of_users}/{number_of_users-number_of_failed_attempts})', parse_mode='html', reply_markup=admin_kb.menu_kb)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(admin_panel_command, Text(equals='👨‍💻 Админ панель'))
    dp.register_message_handler(awaiting_verification_command, Text(equals='✅ Толықтырулар күтілуде'))
    dp.register_message_handler(add_book_command, Text(equals='📚 Кітап қосу'))
    dp.register_message_handler(pin_book_command, Text(equals='📎 Кітап тіркеу'))
    dp.register_message_handler(delete_book_command, Text(equals='🗑 Кітап жою'))
    dp.register_message_handler(statistics_command, Text(equals='📊 Статистика'))
    dp.register_message_handler(mailing_command, Text(equals='📝 Рассылка'))
    dp.register_message_handler(back_command, Text(equals='↩️ Бас мәзір'))

    # FSM
    dp.register_message_handler(cancel_upload_book_command, Text(equals='Бас тарту', ignore_case=True), state='*')

    # Mailing
    dp.register_message_handler(mailing_text, state=Mailing.text)
    dp.register_message_handler(mailing_type, state=Mailing.type)

    # Pin or delete book
    dp.register_message_handler(set_book_id, state=PinOrDeleteBook.book_id)
    dp.register_message_handler(set_book_file, content_types=types.ContentTypes.DOCUMENT, state=PinOrDeleteBook.book_file)

    # Add book
    dp.register_message_handler(set_title, state=UploadBook.title)
    dp.register_message_handler(set_description, state=UploadBook.description)
    dp.register_message_handler(set_author, state=UploadBook.author)
    dp.register_message_handler(set_genre, state=UploadBook.genre)
    dp.register_message_handler(set_book, content_types=types.ContentTypes.DOCUMENT, state=UploadBook.book)


    # Callback
    dp.register_callback_query_handler(complement_callback, lambda x: x.data and x.data.startswith('complement '))
    dp.register_callback_query_handler(delete_callback, lambda x: x.data and x.data.startswith('delete '))