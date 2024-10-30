from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pytz
import re
import os

# Настройка для работы с Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL страницы интернет-магазина
url = "https://avtobat36.ru/catalog/avtomobili_gruzovye/"
driver.get(url)
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'lxml')

# Находим номер последней страницы
pages = soup.find('div', class_='bx_pagination_page').find_all('li')
last_page = int(pages[-2].text.strip())

# Путь к базе данных
db_file = 'test_baza.db'

# Подключение к базе данных (создание, если файл не существует)
try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Проверяем существование файла базы данных
    if not os.path.isfile(db_file):
        print(f"Database file {db_file} does not exist, creating a new one.")
    else:
        # Try executing a simple query to verify the database
        cursor.execute("SELECT 1")
except sqlite3.DatabaseError as e:
    print(f"Error accessing database: {e}. Deleting corrupted database file and creating a new one.")
    os.remove(db_file)  # Delete the corrupted database file
    conn = sqlite3.connect(db_file)  # Create a new database
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

# Создаем таблицу для актуальных данных, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS today_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_parsed TEXT,
    title TEXT,
    number TEXT,
    price TEXT,
    image TEXT,
    link TEXT
)
''')



# Получаем текущую дату в часовом поясе UTC+3
tz = pytz.timezone("Europe/Moscow")
current_date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

# Получаем ссылки и цены для всех товаров из базы данных
cursor.execute('''
    SELECT link, price FROM products
''')
existing_products = cursor.fetchall()
existing_links = {item[0]: item[1] for item in existing_products}  # link -> price

# Переменная для хранения данных сегодняшнего дня
today_data = []

# Проходим по всем страницам
for page in range(1, last_page + 1):
    page_url = f"https://avtobat36.ru/catalog/avtomobili_gruzovye/?PAGEN_2={page}"
    driver.get(page_url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'lxml')

    products = soup.find_all('div', class_=re.compile(r'catalog-section-item sec_item itm_'))
    print(f"Страница {page}: найдено товаров {len(products)}")

    for product in products:
        try:
            title_element = product.find('a', class_='d-lnk-txt')
            title = title_element.text.strip() if title_element else "Нет названия"

            price_element = product.find('span', class_='js-price')
            price = price_element.text.strip() if price_element else 'Необходимо уточнять'
            price = re.sub(r'\D', '', price)

            number_element = product.find('div', class_='sec_params d-note')
            if number_element:
                details = number_element.text.strip()
                number = details[details.find(':') + 1:details.find('П') - 1].strip()
            else:
                number = 'Артикул отсутствует'

            link_element = product.find('a', class_='d-lnk-txt')
            link = link_element['href'] if link_element else "Нет ссылки"
            link_full = f"https://avtobat36.ru{link}"

            # Проверка на наличие изображения
            image_element = product.find('img')
            image = f"https://avtobat36.ru{image_element['src']}" if image_element and 'src' in image_element.attrs else "Нет изображения"

            # Добавляем данные для последующей обработки
            today_data.append((current_date, title, number, price, image, link_full))

        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")

# Проверка на новые товары или изменение цены
new_entries = []

for current_date, title, number, price, image, link in today_data:
    # Проверка на наличие ссылки среди записей в базе данных
    if link in existing_links:
        # Если ссылка уже есть, проверяем изменение цены
        last_price = existing_links[link]
        if price != last_price:  # Цена изменилась
            new_entries.append((current_date, title, number, price, image, link))
    else:
        # Новый товар, если ссылка не найдена в базе
        new_entries.append((current_date, title, number, price, image, link))

# Добавление новых товаров и товаров с измененной ценой в базу данных
if new_entries:
    print("Найдены новые товары или изменения в цене, добавляем в базу данных.")
    cursor.executemany('''
        INSERT INTO products (date_parsed, title, number, price, image, link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', new_entries)
else:
    print("Изменений нет, данные не будут добавлены.")

# Удаляем все записи из таблицы актуальных данных, чтобы сохранить только данные текущего дня
cursor.execute('DELETE FROM today_products')
# Обновляем таблицу актуальных данных новыми данными текущего дня
cursor.executemany('''
    INSERT INTO today_products (date_parsed, title, number, price, image, link)
    VALUES (?, ?, ?, ?, ?, ?)
''', today_data)

# Сохранение и закрытие соединения
conn.commit()
conn.close()
driver.quit()
