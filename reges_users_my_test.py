import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Создаем таблицы, если их нет
def create_tables():
    try:
        conn = mysql.connector.connect(
            host='krutskuy.beget.tech',  # Укажите ваш хост
            user='krutskuy_parc',       # Укажите вашего пользователя
            password='AnosVoldigod0',  # Укажите ваш пароль
            database='krutskuy_parc'  # Укажите вашу базу данных
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    date_joined DATETIME
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_product_list (
                    user_id BIGINT,
                    product_id INT,
                    PRIMARY KEY (user_id, product_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_products (
                    user_id BIGINT,
                    product_link VARCHAR(255),
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            conn.commit()
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Добавляем нового пользователя
def add_user(user):
    try:
        conn = mysql.connector.connect(
            host='krutskuy.beget.tech',
            user='krutskuy_parc',
            password='AnosVoldigod0',
            database='krutskuy_parc'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user.id,))
            if cursor.fetchone() is None:
                cursor.execute(
                    'INSERT INTO users (user_id, username, first_name, last_name, date_joined) VALUES (%s, %s, %s, %s, %s)',
                    (user.id, user.username, user.first_name, user.last_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
    except Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def add_product_to_user_list(user_id, product_id):
    create_tables()  # Убедитесь, что таблицы созданы

    try:
        conn = mysql.connector.connect(
            host='krutskuy.beget.tech',
            user='krutskuy_parc',
            password='AnosVoldigod0',
            database='krutskuy_parc'
        )
        if conn.is_connected():
            cursor = conn.cursor()

            # Проверяем, существует ли уже этот продукт в списке пользователя
            cursor.execute("SELECT * FROM user_products WHERE user_id = %s AND product_link = %s", (user_id, product_id))
            if cursor.fetchone() is not None:
                print(f"Продукт с ID {product_id} уже добавлен в список пользователя с ID {user_id}.")
                return

            # Добавляем продукт в список пользователя
            try:
                cursor.execute("INSERT INTO user_products (user_id, product_link) VALUES (%s, %s)", (user_id, product_id))
                conn.commit()
                print(f"Продукт с ID {product_id} добавлен в список пользователя с ID {user_id}.")
            except Error as e:
                print(f"Ошибка при добавлении продукта: {e}")
    except Error as e:
        print(f"Ошибка при добавлении продукта в список: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Регистрация нового пользователя
def register_user(message):
    create_tables()  # Убедитесь, что таблицы созданы
    add_user(message.from_user)  # Добавление пользователя в БД
    print(message.from_user)
