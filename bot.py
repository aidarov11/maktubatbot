from aiogram.utils import executor
from create_bot import dp
from handlers import user, admin
from database import postgres_db


async def on_startup(_):
    print('Бот вышел в онлайн')
    postgres_db.sql_start()

user.register_handler(dp)
admin.register_handler(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
