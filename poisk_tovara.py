import sqlite3
from fuzzywuzzy import fuzz


def articul_in_database(query, table_names):
    for table_name in table_names:
        with sqlite3.connect('test_baza.db') as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE number = ?)", (query,))
            result = cursor.fetchone()[0]
            if bool(result):
                return bool(result)

    return False


def fetch_all_products(cursor, table_names):
    all_products = []
    for table_name in table_names:
        cursor.execute(f"SELECT id, date_parsed, title, number, price, image, link FROM {table_name}")
        all_products.extend(cursor.fetchall())
    return all_products


def search_products_title(products, query):
    found_products = []
    query_lower = query.lower().strip()

    for product in products:
        title_score = fuzz.partial_ratio(query_lower, product[2].lower())
        if title_score >= 81:
            found_products.append(product)

    # Преобразуем цену в float для сортировки
    found_products.sort(key=lambda x: float(x[4]) if x[4].replace('.', '', 1).isdigit() else 0, reverse=True)
    return found_products


def search_products_articul(products, query):
    found_products = []

    for product in products:
        number_exact_match = query.strip() == product[3].strip()
        if number_exact_match:
            found_products.append(product)

    # Преобразуем цену в float для сортировки
    found_products.sort(key=lambda x: float(x[4]) if x[4].replace('.', '', 1).isdigit() else 999999999, reverse=True)
    return found_products


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
            price = product[4] if int(product[4]) < 999999999 else 'Необходимо уточнять'
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
                f"Ссылка: {product[6]}\n"
            )

        while len(message) > 4096:
            split_index = message.rfind('\n', 0, 4096)
            if split_index == -1:
                split_index = 4096
            bot.send_message(chat_id, message[:split_index])
            message = message[split_index:]

        bot.send_message(chat_id, message)
    else:
        message = f"Товары по вашему запросу '{query}' не найдены."
        bot.send_message(chat_id, message)