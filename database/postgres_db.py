import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def sql_start():
    global conn, cur
    conn = psycopg2.connect(dbname=os.getenv('DB_NAME'), host='localhost', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'))
    cur = conn.cursor()

    if conn:
        print('DB connected successfully')


# User
async def add_user(message):
    cur.execute('insert into users (first_name, last_name, username, telegram_id) values (%s, %s, %s, %s)', (str(message.from_user.first_name), str(message.from_user.last_name), str(message.from_user.username), str(message.from_user.id)))
    conn.commit()

    print('[INFO] New user has been added!')


async def check_user(tg_id):
    cur.execute('select exists(select 1 from users where telegram_id = %s)', (str(tg_id),))
    record = cur.fetchone()

    return record[0]


async def get_user_id(tg_id):
    cur.execute('select id from users where telegram_id = %s', (str(tg_id),))
    record = cur.fetchone()

    return record[0]


async def get_users_id():
    cur.execute('select telegram_id from users')
    records = cur.fetchall()

    return records


async def get_user_status(tg_id):
    cur.execute('select status from users where telegram_id = %s', (str(tg_id),))
    record = cur.fetchone()

    return record[0]


async def get_telegram_users_id():
    cur.execute('select telegram_id from users')
    record = cur.fetchall()

    return record


async def get_user_data(tg_user_id):
    cur.execute('select first_name, last_name, username from users where telegram_id = %s', (str(tg_user_id),))
    record = cur.fetchone()

    return record


async def get_numbet_of_users():
    cur.execute('select count(id) from users')
    record = cur.fetchone()

    return record[0]


async def update_user_data(user):
    cur.execute('update users set first_name = %s, last_name = %s, username = %s where telegram_id = %s', (str(user.first_name), str(user.last_name), str(user.username), str(user.id)))
    conn.commit()

    print('[INFO] User data updated')


# User statistics
async def add_user_statistics(active_users, inactive_users):
    cur.execute('insert into user_statistics(active_users, inactive_users) values (%s, %s)', (active_users, inactive_users))
    conn.commit()

    print('[INFO] User statistics added')


async def get_user_statistics():
    cur.execute('select active_users, inactive_users, created_at from user_statistics order by created_at desc limit 1')
    record = cur.fetchone()

    return record


# Genre
async def get_genres():
    cur.execute('select name from genres')
    records = [record[0] for record in cur.fetchall()]

    return records


async def get_genre_id(genre_name):
    cur.execute('select id from genres where name = %s', (str(genre_name),))
    record = cur.fetchone()

    return record[0]


# Books
async def add_empty_book(user_id):
    cur.execute('insert into books (user_id) values (%s) returning id', (user_id,))
    conn.commit()

    book_id = cur.fetchone()[0]

    print('[INFO] Empty book has been added!')
    return book_id


async def add_book(data):
    cur.execute('insert into books (title, description, author, genre_id, user_id) values (%s, %s, %s, %s, %s) returning id', (data[0], data[1], data[2], data[3], data[4]))
    conn.commit()

    book_id = cur.fetchone()[0]
    # Говно код
    cur.execute('update books set is_verified = true where id = %s', (book_id,))
    conn.commit()

    print('[INFO] Book has been added!')
    return book_id


async def update_book(data):
    cur.execute('update books set title = %s, description = %s, author = %s, genre_id = %s, is_verified = true where id = %s', (data[1], data[2], data[3], data[4], data[0]))
    conn.commit()

    print('[INFO] Book has been updated')


async def get_new_books():
    cur.execute('select books.id, books.title, books.description, books.author, genres.name from books inner join genres on books.genre_id = genres.id where is_verified = true  order by books.created_at desc limit 5')
    records = cur.fetchall()

    return records


async def get_popular_books():
    cur.execute('select books.id, books.title, books.description, books.author, genres.name from books inner join genres on books.genre_id = genres.id where is_verified = true  order by books.downloads desc limit 5')
    records = cur.fetchall()

    return records


async def get_books(text):
    cur.execute(f"SELECT books.id, books.title, books.description, books.author, genres.name FROM books INNER JOIN genres ON books.genre_id = genres.id where is_verified = true AND LOWER(books.title) LIKE '%{text}%' OR LOWER(books.description) LIKE '%{text}%' OR LOWER(books.author) LIKE '%{text}%' OR LOWER(genres.name) LIKE '%{text}%'")
    records = cur.fetchall()

    return records


async def get_books_by_genre_id(genre_id):
    cur.execute('SELECT books.id, books.title, books.description, books.author, genres.name FROM books INNER JOIN genres ON books.genre_id = genres.id where is_verified = true AND books.genre_id = %s', (genre_id,))
    records = cur.fetchall()

    return records

async def get_number_of_books():
    cur.execute('select count(id) from books where is_verified=true')
    record = cur.fetchone()

    return  record[0]


async def get_genre_statistics():
    cur.execute('select genres.name, count(books.id), sum(books.downloads) from books inner join genres on books.genre_id = genres.id where is_verified = true group by genres.name')
    records = cur.fetchall()

    return records


async def delete_book(book_id):
    cur.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()

    cur.execute('DELETE FROM files WHERE book_id = %s', (book_id,))
    conn.commit()

    print('[INFO] Book and his File has been deleted')


async def increase_downloads_book(book_id):
    cur.execute('update books set downloads = downloads + 1 where id = %s', (book_id,))
    conn.commit()


# Files
async def add_file(file_id, file_type, book_id):
    cur.execute('insert into files (file_id, type, book_id) values (%s, %s, %s)', (file_id, file_type, book_id))
    conn.commit()

    print('[INFO] New file has been added!')


async def get_file_id(id):
    cur.execute('select file_id from files where id = %s', (id,))
    record = cur.fetchone()

    return record[0]


async def get_files(book_id):
    cur.execute('select id, type from files where book_id = %s', (book_id,))
    records = cur.fetchall()

    return records

async def get_unverified_files():
    cur.execute('select files.id, files.file_id, files.type, books.id from files inner join books on files.book_id = books.id where is_verified = false')
    records = cur.fetchall()

    return records

