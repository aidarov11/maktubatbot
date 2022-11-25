from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text, Filter
from create_bot import bot, dp

# DB
from database import postgres_db

# Keyboards
from keyboards import user_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# FSM
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Config
import config

import os
from dotenv import load_dotenv

load_dotenv()

# Filter
class isGenre(Filter):
    async def check(self, message: types.Message) -> bool:
        genres = await postgres_db.get_genres()
        genre = message.text

        if genre in genres:
            return True

        return False


class isQuery(Filter):
    async def check(self, message: types.Message) -> bool:
        if len(message.text) > 3:
            books = await postgres_db.get_books(message.text.lower())

            if books:
                return True
            else:
                await bot.send_message(message.chat.id, 'Өкінішке орай, сіз іздеген кітап табылмады', parse_mode='html')
        else:
            await bot.send_message(message.chat.id, '3 әріптен көп сөзді енгізіңіз', parse_mode='html')

        return False


async def start_command(message: types.Message):
    if not await postgres_db.check_user(message.chat.id):
        await postgres_db.add_user(message)
    else:
        user_data = await postgres_db.get_user_data(message.chat.id)

        if f'{message.from_user.first_name}' != user_data[0] or f'{message.from_user.last_name}' != user_data[1] or f'{message.from_user.username}' != user_data[2]:
            await postgres_db.update_user_data(message.from_user)


    if await user_is_chat_member(message.chat.id):
        await menu_keyboard_by_user_status(message.chat.id, config.welcome_text)
    else:
        await check_user_subscribe(message.chat.id)


async def search_book_command(message: types.Message):
    await bot.send_message(message.chat.id, config.search_text, parse_mode='html', reply_markup=user_kb.search_kb)


async def books_by_query(message: types.Message):
    books = await postgres_db.get_books(message.text.lower())
    await normalize_books(message.chat.id, books)


async def show_genres_of_books_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Жанрлар:', parse_mode='html', reply_markup=user_kb.genre_kb)


async def books_by_genre(message: types.Message):
    genre = message.text
    genre_id = await postgres_db.get_genre_id(genre)
    books = await postgres_db.get_books_by_genre_id(genre_id)

    if books:
        await normalize_books(message.chat.id, books)
    else:
        await bot.send_message(message.chat.id, 'Жанрдын іші бос', parse_mode='html')


async def show_new_books_command(message: types.Message):
    new_books = await postgres_db.get_new_books()
    await normalize_books(message.chat.id, new_books)


async def show_popular_books_command(message: types.Message):
    popular_books = await postgres_db.get_popular_books()
    await normalize_books(message.chat.id, popular_books)


async def about_us_command(message: types.Message):
    await bot.send_message(message.chat.id, config.about_us_text, parse_mode='html')


async def project_support_command(message: types.Message):
    await bot.send_message(message.chat.id, config.project_support_text, parse_mode='html')


async def upload_book_command(message: types.Message):
    await UploadBookFSM.upload_book.set()
    await bot.send_message(message.chat.id, config.upload_book_text, parse_mode='html', reply_markup=user_kb.cancel_kb)


# Log out
async def log_out_command(message: types.Message):
    result = await bot.log_out()
    print("Log out result: " + str(result))


class UploadBookFSM(StatesGroup):
    upload_book = State()


# Cancel FSM
async def cancel_fsm_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == None:
        return

    await state.finish()

    await menu_keyboard_by_user_status(message.chat.id, 'Бас мәзір')


# go back to the menu
async def menu_command(message: types.Message):
    chat_id = message.chat.id
    user_status = await postgres_db.get_user_status(chat_id)

    if user_status == 1:
        await bot.send_message(chat_id, 'Бас мәзір', reply_markup=user_kb.menu_with_admin_panel_kb)
    else:
        await bot.send_message(chat_id, 'Бас мәзір', reply_markup=user_kb.menu_kb)


# Upload book FSM
async def upload_book(message: types.ContentTypes.DOCUMENT, state: FSMContext):
    tg_id = message.chat.id
    user_id = await postgres_db.get_user_id(tg_id)
    file_id = message.document.file_id
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx', 'txt', 'rtf', 'azw']:
        book_id = await postgres_db.add_empty_book(user_id)
        await postgres_db.add_file(file_id, file_type, book_id)

        await state.finish()
        await menu_keyboard_by_user_status(message.chat.id, config.uploaded_book_text)
    else:
        await bot.send_message(message.chat.id, config.upload_book_text, parse_mode='html', reply_markup=user_kb.cancel_kb)


# Callback
async def download_file_callback(callback_query: types.CallbackQuery):
    file_id, book_id = callback_query.data.replace('download ', '').split(' ')
    tg_file_id = await postgres_db.get_file_id(int(file_id))
    chat_id = callback_query.message.chat.id

    # downloads count
    await postgres_db.increase_downloads_book(book_id)

    await callback_query.answer(text='Күте тұрыңыз, кітап жүктелу үстінде...', show_alert=False)
    await bot.send_document(chat_id, tg_file_id)


async def check_user_subscribe_callback(callback_query: types.CallbackQuery):
    tg_user_id = callback_query.data.replace('check ', '')

    if await user_is_chat_member(tg_user_id):
        await menu_keyboard_by_user_status(tg_user_id, config.welcome_text)
    else:
        await check_user_subscribe(tg_user_id)



# Additional functions
async def user_is_chat_member(tg_user_id):
    chat_member_status = await bot.get_chat_member(os.getenv('CHANNEL_ID'), tg_user_id)

    if chat_member_status.status != 'left':
        return True

    return False


async def check_user_subscribe(tg_user_id):
    subscribe_btn = InlineKeyboardButton('📢 Тіркелу', url='https://t.me/maktubatkz')
    check_btn = InlineKeyboardButton('✅ Тексеру', callback_data=f'check {tg_user_id}')

    subscribe_kb = InlineKeyboardMarkup()
    subscribe_kb.add(subscribe_btn).add(check_btn)

    message = await bot.send_message(tg_user_id, 'Ботты қолдану үшін алдымен біздің каналға тіркеліңіз.', reply_markup=subscribe_kb)


async def menu_keyboard_by_user_status(chat_id, message):
    user_status = await postgres_db.get_user_status(chat_id)

    if user_status == 0:
        await bot.send_message(chat_id, message, parse_mode='html', reply_markup=user_kb.menu_kb)
    else:
        await bot.send_message(chat_id, message, parse_mode='html', reply_markup=user_kb.menu_with_admin_panel_kb)


async def normalize_books(chat_id, books):
    await bot.send_message(chat_id, f'<i>Табылған кітап саны:</i> {len(books)}', parse_mode='html')
    user_status = await postgres_db.get_user_status(chat_id)

    for book in books:
        book_id = book[0]
        genre = str(book[4]).replace(' ', '_')

        files = await postgres_db.get_files(book_id)

        file_btns = (InlineKeyboardButton(text, callback_data=f'download {file_id} {book_id}') for file_id, text in files)
        file_kb = InlineKeyboardMarkup()
        file_kb.row(*file_btns)

        if user_status == 0:
            await bot.send_message(chat_id, f'#{genre}\n<b>{book[1]}</b>\n\n<i>{book[3]}</i>\n\n{book[2]}', parse_mode='html', reply_markup=file_kb)
        else:
            await bot.send_message(chat_id, f'ID: {book_id}\n\n#{genre}\n<b>{book[1]}</b>\n\n<i>{book[3]}</i>\n\n{book[2]}', parse_mode='html', reply_markup=file_kb)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])

    dp.register_message_handler(search_book_command, Text(equals='🔍 Іздеу'))
    dp.register_message_handler(menu_command, Text(equals='Іздеуді тоқтату', ignore_case=True))

    dp.register_message_handler(show_genres_of_books_command, Text(equals='📚 Кітаптар сөресі'))
    dp.register_message_handler(menu_command, Text(equals='🔙 Артқа', ignore_case=True))

    dp.register_message_handler(show_new_books_command, Text(equals='🆕 Жаңа кітаптар'))
    dp.register_message_handler(show_popular_books_command, Text(equals='🔝 Ең көп жүктелгендер'))
    dp.register_message_handler(about_us_command, Text(equals='ℹ️ Біз туралы'))
    dp.register_message_handler(project_support_command, Text(equals='♥️ Жобаны қолдау'))
    dp.register_message_handler(upload_book_command, Text(equals='📥 Кітап жіберу'))
    dp.register_message_handler(log_out_command, commands=['tgLogOut'])
    dp.register_message_handler(books_by_genre, isGenre())
    dp.register_message_handler(books_by_query, isQuery())

    # FSM
    dp.register_message_handler(cancel_fsm_command, Text(equals='↩️ Бас тарту', ignore_case=True), state='*')


    # Upload book FSM
    dp.register_message_handler(upload_book, content_types=types.ContentTypes.DOCUMENT, state=UploadBookFSM.upload_book)

    # Callback
    dp.register_callback_query_handler(download_file_callback, lambda x: x.data and x.data.startswith('download '))
    dp.register_callback_query_handler(check_user_subscribe_callback, lambda x: x.data and x.data.startswith('check '))