from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu_btn1 = KeyboardButton('🔍 Іздеу')
menu_btn2 = KeyboardButton('📚 Кітаптар сөресі')
menu_btn3 = KeyboardButton('🆕 Жаңа кітаптар')
menu_btn4 = KeyboardButton('🔝 Ең көп жүктелгендер')
menu_btn5 = KeyboardButton('ℹ️ Біз туралы')
menu_btn6 = KeyboardButton('♥️ Жобаны қолдау')
menu_btn7 = KeyboardButton('📥 Кітап жіберу')

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.row(menu_btn1).row(menu_btn2).add(menu_btn3, menu_btn4).add(menu_btn5, menu_btn6).row(menu_btn7)


admin_panel_btn = KeyboardButton('👨‍💻 Админ панель')

menu_with_admin_panel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_with_admin_panel_kb.row(menu_btn1).row(menu_btn2).add(menu_btn3, menu_btn4).add(menu_btn5, menu_btn6).row(menu_btn7).row(admin_panel_btn)


cancel_btn = KeyboardButton('↩️ Бас тарту')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_btn)

