import sqlite3
from datetime import datetime

# Создание соединения с базой данных и таблицы пользователей
def create_tables():
    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()
        # Создаем таблицу для хранения пользователей, если ее нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                date_joined TEXT
            )
        ''')

def add_user(user):
    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()
        # Проверяем, есть ли пользователь в базе
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
        if cursor.fetchone() is None:
            # Добавляем пользователя, если его нет в базе
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, last_name, date_joined) VALUES (?, ?, ?, ?, ?)',
                (user.id, user.username, user.first_name, user.last_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
