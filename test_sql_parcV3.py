from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pytz
import re


# Настройка для работы с Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Запуск браузера в фоновом режиме
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Устанавливаем драйвер для Chrome с использованием webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Основной URL страницы
base_url = "https://www.autoopt.ru/catalog/otechestvennye_gruzoviki?pageSize=100&PAGEN_1="

# Подключение к базе данных
conn = sqlite3.connect('test_baza.db')
cursor = conn.cursor()

# Извлекаем общее количество товаров
def get_total_products():
    driver.get(base_url + "1")  # Загружаем первую страницу
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'lxml')

    total_products_element = soup.find('div', class_='row mt-4 mb-4')
    if total_products_element:
        span_element = total_products_element.find('span', class_='bold')
        if span_element:
            total_products = int(span_element.text.strip())
            print(f"Всего товаров: {total_products}")
            return total_products
        else:
            print("Не удалось найти элемент 'span' с классом 'bold'.")
            return 0
    else:
        print("Не удалось найти элемент 'div' с классом 'row mt-4 mb-4'.")
        return 0

total_products = get_total_products()

# Рассчитываем количество страниц
products_per_page = 100
total_pages = (total_products // products_per_page) + (1 if total_products % products_per_page > 0 else 0)
print(f"Страниц для парсинга: {total_pages}")

# Создаем таблицу, если она не существует
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS productsV3 (
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
CREATE TABLE IF NOT EXISTS today_productsV3 (
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

# Извлечение всех ссылок и последних цен из базы данных
cursor.execute(''' 
    SELECT link, price FROM productsV3
''')
existing_data = cursor.fetchall()

# Преобразуем данные в словарь для быстрой проверки (link -> price)
existing_data_dict = {item[0]: item[1] for item in existing_data}


# Функция для парсинга одной страницы
def parse_page(page_number):
    url = f"{base_url}{page_number}"
    print(f"Парсим страницу {page_number}: {url}")

    # Открываем страницу
    driver.get(url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'lxml')

    # Находим все товары на странице
    products = soup.find_all('div', class_='n-catalog-item relative grid-item n-catalog-item__product')

    if not products:
        print(f"Товары на странице {page_number} не найдены.")
        return []  # Если товаров нет, возвращаем пустой список

    # Извлекаем информацию о каждом товаре
    parsed_data_page = []
    for product in products:
        try:
            # Название товара
            title_elem = product.find('a', class_='n-catalog-item__name-link')
            title = title_elem.text.strip() if title_elem else 'Название не найдено'

            # Поиск цены товара
            price_elements = product.find_all('span', class_=re.compile(r'bold price-item.*'))
            price = price_elements[0].text.strip() if price_elements else 'Необходимо уточнять'
            price = re.sub(r'\D', '', price)

            # Артикул товара
            articule = product.find('div', class_='n-catalog-item__article')
            number_elem = articule.find('span', class_='string bold nowrap n-catalog-item__click-copy n-catalog-item__ellipsis') if articule else None
            number = number_elem.text.strip() if number_elem else 'Артикул не найден'

            # Ссылка на товар
            link_elem = product.find('a', class_='n-catalog-item__name-link')
            link = f"https://www.autoopt.ru{link_elem['href']}" if link_elem else 'Ссылка не найдена'

            # Извлекаем URL изображения
            thumbnail_div = product.find('div', class_='lightbox__thumbnail-img')
            style = thumbnail_div['style'] if thumbnail_div else ''
            start_index = style.find('url(') + len('url(')
            end_index = style.find(')', start_index)
            image_url = style[start_index:end_index].strip(' &quot;') if start_index >= 0 and end_index >= 0 else None

            # Проверка наличия изображения
            if image_url:
                image_url = f"https://www.autoopt.ru{image_url.strip('\"')}"  # Убираем кавычки и добавляем префикс
            else:
                image_url = 'Нет изображения'  # Устанавливаем сообщение при отсутствии изображения

            # Сохранение данных с изменением порядка колонок
            parsed_data_page.append((current_date, title, number, price, image_url, link))
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")

    return parsed_data_page

# Удаляем все записи из таблицы актуальных данных, чтобы сохранить только данные текущего дня
cursor.execute('DELETE FROM today_productsV3')

# Список для хранения данных о товарах
parsed_data = []

# Парсим страницы
for page_number in range(1, total_pages + 1):
    try:
        data = parse_page(page_number)
        parsed_data.extend(data)
        # Обновляем таблицу актуальных данных новыми данными текущего дня
    except Exception as e:
        print(f"Ошибка при обработке страницы {page_number}: {e}")
        break  # Прекращаем при ошибке
cursor.executemany('''
            INSERT INTO today_productsV3 (date_parsed, title, number, price, image, link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', parsed_data)


# Переменная для отслеживания изменений
new_entries = []

# Проверка данных после парсинга
for current_date, title, number, price, image_url, link in parsed_data:
    # Если товара нет в базе данных (по ссылке), он новый и добавляется
    if link not in existing_data_dict:
        new_entries.append((current_date, title, number, price, image_url, link))
    # Если товар есть, но цена изменилась, обновляем запись
    elif price != existing_data_dict[link]:
        new_entries.append((current_date, title, number, price, image_url, link))

# Если изменения найдены, добавляем новые данные в базу
if new_entries:
    print("Найдены изменения, добавляем новые данные.")
    cursor.executemany(''' 
        INSERT INTO productsV3 (date_parsed, title, number, price, image, link) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', new_entries)
else:
    print("Изменений нет, данные не будут добавлены.")

# Сохранение и закрытие соединения
conn.commit()
conn.close()
driver.quit()
