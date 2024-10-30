import sqlite3
from datetime import datetime
from fuzzywuzzy import fuzz
from io import BytesIO
import matplotlib.pyplot as plt
from telebot import TeleBot, types  # Импортируем TeleBot и types

# Инициализация бота с вашим токеном
bot = TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')


# Функция для поиска товаров по артикулу
def articul_in_database(query, table_names):
    for table_name in table_names:
        with sqlite3.connect('test_baza.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE number = ?)", (query,))
            result = cursor.fetchone()[0]
            if bool(result):
                return True
    return False


# Функция для получения всех продуктов из таблиц
def fetch_all_products(cursor, table_names):
    all_products = []
    for table_name in table_names:
        cursor.execute(f"SELECT id, date_parsed, title, number, price, image, link FROM {table_name}")
        all_products.extend(cursor.fetchall())
    return all_products


# Функция для поиска продуктов по названию
def search_products_title(products, query):
    found_products = []
    query_lower = query.lower().strip()

    for product in products:
        title_score = fuzz.partial_ratio(query_lower, product[2].lower())
        if title_score >= 81:
            found_products.append(product)

    found_products.sort(key=lambda x: float(x[4]) if x[4].replace('.', '', 1).isdigit() else 0, reverse=True)
    return found_products


# Функция для поиска продуктов по артикулу
def search_products_articul(products, query):
    found_products = []
    for product in products:
        if query.strip() == product[3].strip():
            found_products.append(product)

    found_products.sort(key=lambda x: float(x[4]) if x[4].replace('.', '', 1).isdigit() else 999999999, reverse=True)
    return found_products


# Основная функция для поиска продуктов
def search_products(query, chat_id, bot):
    table_names = ['today_products', 'today_productsV2', 'today_productsV3']

    with sqlite3.connect('test_baza.db') as conn:
        cursor = conn.cursor()
        all_products = fetch_all_products(cursor, table_names)

    if articul_in_database(query, table_names):
        found_products = search_products_articul(all_products, query)
    else:
        found_products = search_products_title(all_products, query)

    if found_products:
        message = "Найденные товары (по убыванию цены):\n"
        i = 0
        for product in found_products:
            i += 1
            price = product[4] if product[4] and product[4].replace('.', '', 1).isdigit() and int(
                product[4]) < 999999999 else 'Необходимо уточнять'
            if product[6].startswith('https://avtobat36.ru'):
                site = 'Автобат36'
            elif product[6].startswith('https://vapkagro.ru'):
                site = 'Воронеж Комплект'
            else:
                site = 'Авто Альянс'

            message += (
                f"{i}. \n"
                f"Название сайта: {site}; \n"
                f"Название: {product[2]}; \n"
                f"Артикул: {product[3]}; \n"
                f"Цена: {price}; \n"
                f"Переход на сайт: [Переход на сайт]({product[6]})\n"
            )

            # Создаем кнопку для построения графика
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Построить график", callback_data=f"grapic_{product[3]}")
            markup.add(button)

            # Отправляем сообщение с кнопкой
            bot.send_message(chat_id, message, reply_markup=markup, parse_mode='Markdown')
            message = ""  # Очищаем сообщение для следующих товаров

        # Отправляем последнее сообщение, если оно осталось
        if message:
            bot.send_message(chat_id, message, parse_mode='Markdown')

    else:
        message = f"Товары по вашему запросу '{query}' не найдены."
        bot.send_message(chat_id, message)


# Функция для построения графика изменения цены
def plot_price_history_by_articul(bot, chat_id, product_id):
    conn = sqlite3.connect('test_baza.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date_parsed, price FROM products WHERE link LIKE ?", (f"%{product_id}",))
    data = cursor.fetchall()
    conn.close()

    if not data:
        bot.send_message(chat_id, "Данные для этого товара не найдены.")
        return

    dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in data]
    prices = [int(row[1]) for row in data]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker='o', linestyle='-', color='b')
    plt.title(f"Изменение цены для товара {product_id}")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.grid()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    bot.send_photo(chat_id=chat_id, photo=buffer)
    plt.close()
    buffer.close()


# Обработчик нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("grapic_"):
        product_id = call.data.split("_")[1]
        plot_price_history_by_articul(bot, call.message.chat.id, product_id)


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
