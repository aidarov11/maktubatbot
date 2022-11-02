from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
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


async def start_command(message: types.Message):
    if not await postgres_db.check_user(message.chat.id):
        await postgres_db.add_user(message)

    if message.from_user.id not in [5091636122, 380448197, 515485172]:
        await bot.send_message(message.chat.id, 'Техникалық жұмыстарға байланысты бот уақытша өз жұмысын тоқтата тұруда.\n\nТүсіністікпен қарап күте тұруларынызды сұраймыз!')
    else:
        await menu_keyboard_by_user_status(message.chat.id, config.welcome_text)


class SearchBookFSM(StatesGroup):
    search = State()


async def search_book_command(message: types.Message):
    await SearchBookFSM.search.set()
    await bot.send_message(message.chat.id, config.search_text, parse_mode='html', reply_markup=user_kb.search_kb)


async def cancel_search_book_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == None:
        return

    await state.finish()
    await menu_keyboard_by_user_status(message.chat.id, 'Бас мәзір')


async def search_book(message: types.Message, state: FSMContext):
    if len(message.text) > 1:
        books = await postgres_db.get_books(message.text.lower())
        await normalize_books(message.chat.id, books)
    else:
        await bot.send_message(message.chat.id, '1 символдан коп енгызыныз')


# Books by genre FSM
class BooksByGenreFSM(StatesGroup):
    genre = State()


async def show_genres_of_books_command(message: types.Message):
    await BooksByGenreFSM.genre.set()
    await bot.send_message(message.chat.id, 'Жанрлар:', parse_mode='html', reply_markup=user_kb.genre_kb)


async def cancel_books_by_genre_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == None:
        return

    await state.finish()
    await menu_keyboard_by_user_status(message.chat.id, 'Бас мәзір')


async def books_by_genre(message: types.Message, state: FSMContext):
    genres = await postgres_db.get_genres()
    genre = message.text

    if genre in genres:
        genre_id = await postgres_db.get_genre_id(genre)
        books = await postgres_db.get_books_by_genre_id(genre_id)

        if books:
            await normalize_books(message.chat.id, books)
        else:
            await bot.send_message(message.chat.id, 'Жанрдын ышы бос!')



async def show_new_books_command(message: types.Message):
    new_books = await postgres_db.get_new_books()
    await normalize_books(message.chat.id, new_books)


async def download_file_callback(callback_query: types.CallbackQuery):
    file_id, book_id = callback_query.data.replace('download ', '').split(' ')
    tg_file_id = await postgres_db.get_file_id(int(file_id))
    chat_id = callback_query.message.chat.id

    # downloads count
    await postgres_db.increase_downloads_book(book_id)


    await callback_query.answer(text='Күте тұрыңыз, кітап жүктелу үстінде...', show_alert=False)
    await bot.send_document(chat_id, tg_file_id)


async def show_popular_books_command(message: types.Message):
    popular_books = await postgres_db.get_popular_books()
    await normalize_books(message.chat.id, popular_books)


async def about_us_command(message: types.Message):
    await bot.send_message(message.chat.id, config.about_us_text, parse_mode='html')


async def project_support_command(message: types.Message):
    await bot.send_message(message.chat.id, config.project_support_text, parse_mode='html')

# Upload book FSM
class UploadBookFSM(StatesGroup):
    upload_book = State()


async def upload_book_command(message: types.Message):
    await UploadBookFSM.upload_book.set()
    await bot.send_message(message.chat.id, config.upload_book_text, parse_mode='html', reply_markup=user_kb.cancel_kb)


async def cancel_upload_book_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == None:
        return

    await state.finish()
    await menu_keyboard_by_user_status(message.chat.id, 'Бас мәзір')


async def upload_book(message: types.ContentTypes.DOCUMENT, state: FSMContext):
    tg_id = message.chat.id
    user_id = await postgres_db.get_user_id(tg_id)
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx', 'txt']:
        book_id = await postgres_db.add_empty_book(user_id)
        file_id, file_path = await download_file(message.document)
        await postgres_db.add_file(file_type, file_id, file_path, book_id)

        await state.finish()
        await menu_keyboard_by_user_status(message.chat.id, config.upload_book_text)
    else:
        await bot.send_message(message.chat.id, config.upload_book_text, parse_mode='html', reply_markup=user_kb.cancel_kb)

# Additional functions
async def menu_keyboard_by_user_status(chat_id, message):
    user_status = await postgres_db.get_user_status(chat_id)

    if user_status == 0:
        await bot.send_message(chat_id, message, parse_mode='html', reply_markup=user_kb.menu_kb)
    else:
        await bot.send_message(chat_id, message, parse_mode='html', reply_markup=user_kb.menu_with_admin_panel_kb)


async def download_file(document):
    file_id = document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    destination = '/Users/aidarov/PycharmProjects/MaktubatkzBot/'
    destination_file = await bot.download_file(file_path=file_path, destination_dir=destination)

    return file_id, destination_file.name


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
            await bot.send_message(chat_id, f'#{genre}\n<b>{book[1]}</b>\n\n<i>{book[3]}</i>\n\n<code>{book[2]}</code>', parse_mode='html', reply_markup=file_kb)
        else:
            await bot.send_message(chat_id, f'ID: {book_id}\n\n#{genre}\n<b>{book[1]}</b>\n\n<i>{book[3]}</i>\n\n<code>{book[2]}</code>', parse_mode='html', reply_markup=file_kb)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(search_book_command, Text(equals='🔍 Іздеу'))
    dp.register_message_handler(show_genres_of_books_command, Text(equals='📚 Кітаптар сөресі'))
    dp.register_message_handler(show_new_books_command, Text(equals='🆕 Жаңа кітаптар'))
    dp.register_message_handler(show_popular_books_command, Text(equals='🔝 Ең көп жүктелгендер'))
    dp.register_message_handler(about_us_command, Text(equals='ℹ️ Біз туралы'))
    dp.register_message_handler(project_support_command, Text(equals='♥️ Жобаны қолдау'))
    dp.register_message_handler(upload_book_command, Text(equals='📥 Кітап жіберу'))

    # Search FSM
    dp.register_message_handler(cancel_search_book_command, Text(equals='Іздеуді тоқтату!', ignore_case=True), state='*')
    dp.register_message_handler(search_book, state=SearchBookFSM.search)

    # Books by genre FSM
    dp.register_message_handler(cancel_books_by_genre_command, Text(equals='🔙 Артқа', ignore_case=True), state='*')
    dp.register_message_handler(books_by_genre, state=BooksByGenreFSM.genre)

    # Upload book FSM
    dp.register_message_handler(cancel_upload_book_command, Text(equals='↩️ Бас тарту', ignore_case=True), state='*')
    dp.register_message_handler(upload_book, content_types=types.ContentTypes.DOCUMENT, state=UploadBookFSM.upload_book)

    # callback
    dp.register_callback_query_handler(download_file_callback, lambda x: x.data and x.data.startswith('download '))



