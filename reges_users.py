import sqlite3
from datetime import datetime

# Создаем таблицы, если их нет
def create_tables():
    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                date_joined TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_product_list (
                user_id INTEGER,
                product_id INTEGER,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_products (
                user_id INTEGER,
                product_link TEXT,
                added_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        conn.commit()

# Добавляем нового пользователя
def add_user(user):
    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
        if cursor.fetchone() is None:
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, last_name, date_joined) VALUES (?, ?, ?, ?, ?)',
                (user.id, user.username, user.first_name, user.last_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()


def add_product_to_user_list(user_id, product_id):

    create_tables()  # Убедитесь, что таблицы созданы

    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()

        # Проверяем, существует ли уже этот продукт в списке пользователя
        cursor.execute("SELECT * FROM user_products WHERE user_id = ? AND product_link = ?", (user_id, product_id))
        if cursor.fetchone() is not None:
            print(f"Продукт с ID {product_id} уже добавлен в список пользователя с ID {user_id}.")
            return

        # Добавляем продукт в список пользователя
        try:
            cursor.execute("INSERT INTO user_products (user_id, product_link) VALUES (?, ?)", (user_id, product_id))
            conn.commit()
            print(f"Продукт с ID {product_id} добавлен в список пользователя с ID {user_id}.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении продукта: {e}")

# Регистрация нового пользователя
def register_user(message):
    create_tables()  # Убедитесь, что таблицы созданы
    add_user(message.from_user)  # Добавление пользователя в БД