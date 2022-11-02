from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton

menu_btn1 = KeyboardButton('✅ Толықтырулар күтілуде')
menu_btn2 = KeyboardButton('📚 Кітап қосу')
menu_btn3 = KeyboardButton('📎 Кітап тіркеу')
menu_btn4 = KeyboardButton('🗑 Кітап жою')
menu_btn5 = KeyboardButton('📊 Статистика')
menu_btn6 = KeyboardButton('↩️ Бас мәзір')

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add(menu_btn1).add(menu_btn2, menu_btn3).add(menu_btn4, menu_btn5).add(menu_btn6)


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
cancel_btn = KeyboardButton('Бас тарту')

genre_kb = ReplyKeyboardMarkup(resize_keyboard=True)
genre_kb.add(genre_btn1, genre_btn2, genre_btn3, genre_btn4, genre_btn5, genre_btn6, genre_btn7, genre_btn8, genre_btn9, genre_btn10, genre_btn11, genre_btn2, genre_btn3, genre_btn4, genre_btn15).row(cancel_btn)

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_btn)
