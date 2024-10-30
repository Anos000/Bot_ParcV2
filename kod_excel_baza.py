import pandas as pd
import re
import sqlite3

# Путь к файлу Excel
excel_file = "../Parcing/downloads/parsed_data.xlsx"

# Чтение данных из Excel
df = pd.read_excel(excel_file, engine='openpyxl')

# Обработка столбца "Цена" для удаления всех символов, кроме цифр
df['Цена'] = df['Цена'].astype(str).apply(lambda x: re.sub(r'\D', '', x))

# Подключение к базе данных
conn = sqlite3.connect('test_baza.db')
cursor = conn.cursor()

# Создаем таблицу, если ее нет
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_parsed TEXT,
    title TEXT,
    number TEXT,
    price TEXT,
    image TEXT,
    link TEXT
)
''')

# Подготовка данных для вставки в базу данных
data_to_insert = []

for index, row in df.iterrows():
    data_to_insert.append((
        row['Дата парсинга'],  # Дата парсинга из Excel
        row['Название'],
        row['Артикул'],
        row['Цена'],
        '',  # Пустое поле для изображения
        row['Ссылка']
    ))

# Вставляем данные из Excel
cursor.executemany('''
    INSERT INTO products (date_parsed, title, number, price, image, link)
    VALUES (?, ?, ?, ?, ?, ?)
''', data_to_insert)

# Сохранение и закрытие соединения
conn.commit()
conn.close()
