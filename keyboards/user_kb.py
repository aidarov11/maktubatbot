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


cancel_btn = KeyboardButton('↩️ Бас тарту')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_btn)


search_btn = KeyboardButton('Іздеуді тоқтату!')

search_kb = ReplyKeyboardMarkup(resize_keyboard=True)
search_kb.add(search_btn)


genre_btn1 = KeyboardButton('Ақида')
genre_btn2 = KeyboardButton('Құран')
genre_btn3 = KeyboardButton('Сүннет')
genre_btn4 = KeyboardButton('Хадис')
genre_btn5 = KeyboardButton('Фиқһ')
genre_btn6 = KeyboardButton('Намаз')
genre_btn7 = KeyboardButton('Ораза')
genre_btn8 = KeyboardButton('Зекет және садақа')
genre_btn9 = KeyboardButton('Қажылық')
genre_btn10 = KeyboardButton('Әйел және отбасы')
genre_btn11 = KeyboardButton('Әдеп және тасаууф')
genre_btn12 = KeyboardButton('Адасқан ағымдар')
genre_btn13 = KeyboardButton('Өмірбаян және тарих')
genre_btn14 = KeyboardButton('Ғылым')
genre_btn15 = KeyboardButton('Әртүрлі')
genre_btn16 = KeyboardButton('🔙 Артқа')


genre_kb = ReplyKeyboardMarkup(resize_keyboard=True)
genre_kb.add(genre_btn1, genre_btn2, genre_btn3, genre_btn4, genre_btn5, genre_btn6, genre_btn7, genre_btn8, genre_btn9, genre_btn10, genre_btn11, genre_btn2, genre_btn3, genre_btn4, genre_btn15).row(genre_btn16)



