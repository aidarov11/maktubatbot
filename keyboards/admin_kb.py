from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton

menu_btn1 = KeyboardButton('✅ Толықтырулар күтілуде')
menu_btn2 = KeyboardButton('📚 Кітап қосу')
menu_btn3 = KeyboardButton('📎 Кітап тіркеу')
menu_btn4 = KeyboardButton('🗑 Кітап жою')
menu_btn5 = KeyboardButton('📊 Статистика')
menu_btn6 = KeyboardButton('📝 Рассылка')
menu_btn7 = KeyboardButton('🔐 Рөл')
menu_btn8 = KeyboardButton('↩️ Бас мәзір')


menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add(menu_btn1).add(menu_btn2, menu_btn3).add(menu_btn4, menu_btn5).add(menu_btn6, menu_btn7).add(menu_btn8)


back_btn = KeyboardButton('↩️ Артқа')

back_kb = ReplyKeyboardMarkup(resize_keyboard=True)
back_kb.add(back_btn)


cancel_btn = KeyboardButton('Бас тарту')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_btn)


pass_btn = KeyboardButton('Өткізіп жіберу')

pass_cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
pass_cancel_kb.add(pass_btn).add(cancel_btn)


stat_btn1 = KeyboardButton('👫 Пайдаланушылар')
stat_btn2 = KeyboardButton('📚 Кітаптар')

stat_kb = ReplyKeyboardMarkup(resize_keyboard=True)
stat_kb.add(stat_btn1).add(stat_btn2).add(back_btn)


rights_btn1 = KeyboardButton('📝 Рөл иеленушілер')
rights_btn2 = KeyboardButton('✏️ Рөл беру')

rights_kb = ReplyKeyboardMarkup(resize_keyboard=True)
rights_kb.add(rights_btn1).add(rights_btn2).add(back_btn)

role_btn1 = KeyboardButton('Модератор')
role_btn2 = KeyboardButton('Администратор')

roles_kb = ReplyKeyboardMarkup(resize_keyboard=True)
roles_kb.add(role_btn1).add(role_btn2).add(cancel_btn)


mailing_btn = KeyboardButton('💌 Тарату')

mailing_kb = ReplyKeyboardMarkup(resize_keyboard=True)
mailing_kb.add(mailing_btn).add(cancel_btn)

