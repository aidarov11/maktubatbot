import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import bot, dp
from database import postgres_db
from keyboards import admin_kb, user_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


async def admin_panel_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        await bot.send_message(message.chat.id, 'Админ панель:', parse_mode='html', reply_markup=admin_kb.menu_kb)


async def awaiting_verification_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        files = await postgres_db.get_unverified_files()

        if files:
            for file in files:
                await bot.send_document(message.chat.id, file[1], reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Толықтыру', callback_data=f'complement {file[3]}')).add(InlineKeyboardButton('Өшіру', callback_data=f'delete {file[0]} {file[3]}')))
        else:
            await bot.send_message(message.chat.id, 'Тізімнің іші бос')
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def add_book_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        await UploadBook.title.set()
        UploadBook.gear = 1

        await bot.send_message(message.chat.id, 'Кітаптың атын енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def pin_book_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        await PinOrDeleteBook.book_id.set()
        PinOrDeleteBook.gear = 1

        await bot.send_message(message.chat.id, 'Кітаптың ID енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def delete_book_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 1:
        await PinOrDeleteBook.book_id.set()
        PinOrDeleteBook.gear = 2

        await bot.send_message(message.chat.id, 'Өшіргіңіз келетін кітаптің ID енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def statistics_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        await bot.send_message(message.chat.id, 'Статистика бөлімі:', parse_mode='html', reply_markup=admin_kb.stat_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)

# Статистика пользователей
async def user_statistics(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 2:
        number_of_users = await postgres_db.get_number_of_users()
        statistics = await postgres_db.get_user_statistics()
        active_users = 0
        inactive_users = 0
        date = ['0']

        if statistics:
            active_users = statistics[0]
            inactive_users = statistics[1]
            date = str(statistics[2]).split(' ')


        await bot.send_message(message.chat.id, f'Пайдаланушылар саны: <i>{number_of_users}</i>\n\n<b>{date[0]}</b>\nБелсенділер саны: <i>{active_users}</i>\nБелсенділер емес саны: <i>{inactive_users}</i>', parse_mode='html')
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def book_statistics(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        statistics = await postgres_db.get_genre_statistics()
        number_of_books = await postgres_db.get_number_of_books()
        genre_statistics = ''

        for statistic in statistics:
            genre_statistics += f'#{statistic[0]}\nКітап саны: <i>{statistic[1]}</i>\nЖүктелген кітап саны: <i>{statistic[2]}\n\n</i>'

        await bot.send_message(message.chat.id, f'Кітаптардың жалпы саны: <i>{number_of_books}</i>\n\n{genre_statistics}', parse_mode='html')
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def mailing_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 2:
        await Mailing.text.set()
        await bot.send_message(message.chat.id, 'Тарату мәтінін енгізіңіз:', parse_mode='html', reply_markup=admin_kb.pass_cancel_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def rights_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        await bot.send_message(message.chat.id, 'Рөл бөлімі:', parse_mode='html', reply_markup=admin_kb.rights_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def right_owners_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
        right_owners = await postgres_db.get_right_owners()

        if right_owners:
            for right_ownwer in right_owners:
                if user_status > 2 and right_ownwer[0] != await postgres_db.get_user_id(message.chat.id):
                    await bot.send_message(message.chat.id, f'Аты: <b>{right_ownwer[1]}</b>\nЖөні: <b>{right_ownwer[2]}</b>\nusername: <b>{right_ownwer[3]}</b>\nСтатус: <b>{await get_status(right_ownwer[4])}</b>', parse_mode='html', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Өшіру', callback_data=f'turn_off {right_ownwer[0]}')))
                else:
                    await bot.send_message(message.chat.id, f'Аты: <b>{right_ownwer[1]}</b>\nЖөні: <b>{right_ownwer[2]}</b>\nusername: <b>{right_ownwer[3]}</b>\nСтатус: <b>{await get_status(right_ownwer[4])}</b>', parse_mode='html')

            await bot.send_message(message.chat.id, '🔙', reply_markup=admin_kb.back_kb)
        else:
            await bot.send_message(message.chat.id, 'Тізімнің іші бос', reply_markup=admin_kb.back_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)



async def give_rights_command(message: types.Message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 2:
        await Rights.username.set()
        await bot.send_message(message.chat.id, 'Қолданушының username-ың енгізіңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)
    else:
        await bot.send_message(message.chat.id, '🚫', reply_markup=admin_kb.menu_kb)


async def back_command(message: types.message):
    user_status = await postgres_db.get_user_status(message.chat.id)
    if user_status > 0:
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
    await callback_query.answer(text='Өшірілді', show_alert=False)
    await callback_query.message.delete()


async def turnoff_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.replace('turn_off ', '')

    await postgres_db.reset_user_status(user_id)

    await callback_query.answer(text='Қолданушы рөлі өшірілді', show_alert=False)
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
    file = State()
    type = State()


class Rights(StatesGroup):
    username = State()
    user_rights = State()


async def cancel_fsm_command(message: types.Message, state: FSMContext):
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
    await bot.send_message(message.chat.id, 'Кітаптің жанрын таңдаңыз:', parse_mode='html', reply_markup=await get_genres_kb())


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
        await bot.send_message(message.chat.id, 'Кітаптің жанрын таңдаңыз:', parse_mode='html', reply_markup=await get_genres_kb())


async def set_book(message: types.Message, state: FSMContext):
    gear = UploadBook.gear

    tg_id = message.chat.id
    user_id = await postgres_db.get_user_id(tg_id)
    file_id = message.document.file_id
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx', 'txt', 'rtf', 'azw']:
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
        await bot.send_message(message.chat.id, 'Кітап сәтті жойылды', parse_mode='html', reply_markup=admin_kb.menu_kb)


async def set_book_file(message: types.Message, state=FSMContext):
    file_id = message.document.file_id
    file_type = message.document.mime_type.split('/')[1]

    if file_type in ['pdf', 'epub', 'mobi', 'doc', 'docx', 'txt', 'rtf', 'azw']:
        async with state.proxy() as data:
            book_id = data['book_id']

        await postgres_db.add_file(file_id, file_type, book_id)


        await state.finish()
        await bot.send_message(message.chat.id, 'Кітап сәтті қосылды', parse_mode='html', reply_markup=admin_kb.menu_kb)
    else:
        await bot.send_message(message.chat.id, 'Кітапты қайта жберініз')


async def mailing_text(message: types.message, state: FSMContext):
    text = message.text

    async with state.proxy() as data:
        if text != 'Өткізіп жіберу':
            data['text'] = message.text
            await Mailing.next()
        else:
            data['text'] = None
            await Mailing.next()

    await bot.send_message(message.chat.id, 'Таратуға арналған сурет немесе видеоны жберініз:', parse_mode='html', reply_markup=admin_kb.pass_cancel_kb)


async def mailing_file(message: types.ContentTypes.TEXT | types.ContentTypes.PHOTO | types.ContentTypes.VIDEO, state: FSMContext):
    async with state.proxy() as data:
        if message['text']:
            if message['text'] == 'Өткізіп жіберу':
                if data['text'] == None:
                    await cancel_fsm_command(message, state)
                    return
                else:
                    data['file_type'] = None
                    data['file_id'] = None

                    await Mailing.next()
        else:
            if message['video']:
                data['file_type'] = 'video'
                data['file_id'] = message['video'].file_id

                await Mailing.next()
            elif message['photo']:
                data['file_type'] = 'photo'
                data['file_id'] = message['photo'][-1].file_id

                await Mailing.next()
            else:
                await bot.send_message(message.chat.id, 'Таратуға арналған сурет немесе видеоны жберініз:', parse_mode='html', reply_markup=admin_kb.pass_cancel_kb)

    await bot.send_message(message.chat.id, 'Таратылуға арналған тарату:', parse_mode='html', reply_markup=admin_kb.mailing_kb)
    await completed_mailing(message, state)



async def completed_mailing(message, state):
    async with state.proxy() as data:
        text = data['text']
        file_type = data['file_type']
        file_id = data['file_id']

        if text and file_type:
            if file_type == 'photo':
                await bot.send_photo(message.chat.id, photo=file_id, caption=text, parse_mode='html')
            elif file_type == 'video':
                await bot.send_video(message.chat.id, video=file_id, caption=text, parse_mode='html')
        elif text:
            await bot.send_message(message.chat.id, text, parse_mode='html')
        elif file_type:
            if file_type == 'photo':
                await bot.send_photo(message.chat.id, photo=file_id)
            elif file_type == 'video':
                await bot.send_video(message.chat.id, video=file_id)



async def mailing_type(message: types.message, state: FSMContext):
    await bot.send_message(message.chat.id, '<b>Таратылу басталды!</b>\nТаратылу толық біткенше күте тұруыңызды сұраймыз', parse_mode='html')

    if message.text == '💌 Тарату':
        users_id = await postgres_db.get_users_id()
        number_of_users = len(users_id)
        number_of_failed_attempts = 0

        async with state.proxy() as data:
            text = data['text']
            file_type = data['file_type']
            file_id = data['file_id']

            for user_id in users_id:
                try:
                    if text and file_type:
                        if file_type == 'photo':
                            await bot.send_photo(user_id[0], photo=file_id, caption=text, parse_mode='html')
                        elif file_type == 'video':
                            await bot.send_video(user_id[0], video=file_id, caption=text, parse_mode='html')
                    elif text:
                        await bot.send_message(user_id[0], text, parse_mode='html')
                    elif file_type:
                        if file_type == 'photo':
                            await bot.send_photo(user_id[0], photo=file_id)
                        elif file_type == 'video':
                            await bot.send_video(user_id[0], video=file_id)
                except:
                    number_of_failed_attempts += 1
                    await asyncio.sleep(1)

        active_users = number_of_users - number_of_failed_attempts
        await postgres_db.add_user_statistics(active_users, number_of_failed_attempts)

        await state.finish()
        await bot.send_message(message.chat.id, f'Тарату сәтті аяқталды 🙌 ({number_of_users}/{active_users})', parse_mode='html', reply_markup=admin_kb.menu_kb)
    else:
        await bot.send_message(message.chat.id, 'Рассылканы бастау үшін "💌 Тарату" батырмасын басыныз')


async def username_state(message: types.message, state: FSMContext):
    current_username = str(message.text).replace('@', '')

    if await check_username(current_username):
        tg_id = await postgres_db.get_tg_id(current_username)

        async with state.proxy() as data:
            data['tg_id'] = tg_id

        await Rights.next()
        await bot.send_message(message.chat.id, 'Пайдаланушы рөлін таңдаңыз:', parse_mode='html', reply_markup=admin_kb.roles_kb)
    else:
        await bot.send_message(message.chat.id, 'Пайдаланушының username-мі табылмады, қайта енгізіп көріңіз:', parse_mode='html', reply_markup=admin_kb.cancel_kb)


async def user_rights_state(message: types.message, state: FSMContext):
    role = message.text
    roles = ['Модератор', 'Администратор']
    async with state.proxy() as data:
        tg_id = data['tg_id']

    if role in roles:
        index = roles.index(role)
        await postgres_db.set_user_status(index+1, tg_id)

        await state.finish()
        await bot.send_message(message.chat.id, 'Пайдаланушыға рөл сәтті берілді', parse_mode='html', reply_markup=admin_kb.menu_kb)
    else:
        await bot.send_message(message.chat.id, 'Пайдаланушы рөлін тандаңыз:', parse_mode='html', reply_markup=admin_kb.roles_kb)


async def get_genres_kb():
    genres = await postgres_db.get_genres()

    genres_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    other_btn = KeyboardButton('Әртүрлі')
    cancel_btn = KeyboardButton('Бас тарту')
    genre_btns = []

    for genre in genres:
        if genre != 'Әртүрлі':
            genre_btns.append(KeyboardButton(genre))

    genres_kb.add(*genre_btns).add(other_btn).add(cancel_btn)

    return genres_kb


async def check_username(current_username):
    users_username = await postgres_db.get_users_username()

    for username in users_username:
        if username[0] == current_username and username[0] != 'None':
            return True

    return False


async def get_status(status):
    if status == 1:
        return 'Модератор'
    elif status == 2:
        return 'Администратор'


def register_handler(dp: Dispatcher):
    dp.register_message_handler(admin_panel_command, Text(equals='👨‍💻 Админ панель'))
    dp.register_message_handler(awaiting_verification_command, Text(equals='✅ Толықтырулар күтілуде'))
    dp.register_message_handler(add_book_command, Text(equals='📚 Кітап қосу'))
    dp.register_message_handler(pin_book_command, Text(equals='📎 Кітап тіркеу'))
    dp.register_message_handler(delete_book_command, Text(equals='🗑 Кітап жою'))
    dp.register_message_handler(statistics_command, Text(equals='📊 Статистика'))
    dp.register_message_handler(user_statistics, Text(equals='👫 Пайдаланушылар'))
    dp.register_message_handler(book_statistics, Text(equals='📚 Кітаптар'))
    dp.register_message_handler(rights_command, Text(equals='🔐 Рөл'))
    dp.register_message_handler(right_owners_command, Text(equals='📝 Рөл иеленушілер'))
    dp.register_message_handler(give_rights_command, Text(equals='✏️ Рөл беру'))
    dp.register_message_handler(admin_panel_command, Text(equals='↩️ Артқа'))
    dp.register_message_handler(mailing_command, Text(equals='📝 Рассылка'))
    dp.register_message_handler(back_command, Text(equals='↩️ Бас мәзір'))

    # FSM
    dp.register_message_handler(cancel_fsm_command, Text(equals='Бас тарту', ignore_case=True), state='*')

    # Rights
    dp.register_message_handler(username_state, state=Rights.username)
    dp.register_message_handler(user_rights_state, state=Rights.user_rights)

    # Mailing
    dp.register_message_handler(mailing_text, state=Mailing.text)
    dp.register_message_handler(mailing_file, content_types=types.ContentTypes.TEXT | types.ContentTypes.PHOTO | types.ContentTypes.VIDEO, state=Mailing.file)
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
    dp.register_callback_query_handler(turnoff_callback, lambda x: x.data and x.data.startswith('turn_off '))