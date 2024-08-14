import requests
from lxml import html
import pandas as pd
import re
import sqlite3


def extract_price(price_str: str) -> float:
    price_str = re.sub(r'[^\d.,]', '', price_str)
    price_str = price_str.replace(',', '.')
    try:
        return float(price_str)
    except ValueError:
        return 0.0


def parse_price(url: str, xpath: str) -> list:

    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        prices = tree.xpath(xpath)

        return [extract_price(price.strip()) for price in prices]

    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return []
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []


def calculate_average_price(prices: list) -> float:
    if prices:
        return sum(prices) / len(prices)
    return 0.0


def load_from_db() -> pd.DataFrame:
    try:
        conn = sqlite3.connect('information.db')
        df = pd.read_sql_query('SELECT * FROM products', conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def save_results_to_file(results: pd.DataFrame, filename: str, encoding='utf-8-sig'):
    results.to_csv(filename, index=False, encoding=encoding)
    print(f"Результаты сохранены в {filename}")


def handle_parsing() -> str:
    df = load_from_db()
    if df is None:
        return "Ошибка: Не удалось загрузить данные из базы данных."

    site_prices = {}
    all_prices = []

    for _, row in df.iterrows():
        title = row['title']
        url = row['url']
        xpath = row['xpath']
        prices = parse_price(url, xpath)

        for price in prices:
            all_prices.append({'Store': url, 'Item': title, 'Price': price})

        if url in site_prices:
            site_prices[url].extend(prices)
        else:
            site_prices[url] = prices

    if all_prices:
        results_df = pd.DataFrame(all_prices)
        results_df['Price'] = results_df['Price'].map(lambda x: f"{x:.2f} ₽")  # Форматируем цену
    else:
        results_df = pd.DataFrame(columns=['Store', 'Item', 'Price'])


    average_prices = {
        'Store': [],
        'Average Price': []
    }
    for url, prices in site_prices.items():
        average_price = calculate_average_price(prices)
        average_prices['Store'].append(url)
        average_prices['Average Price'].append(f"{average_price:.2f} ₽")

    average_prices_df = pd.DataFrame(average_prices)

    save_results_to_file(results_df, 'detailed_results.csv')
    save_results_to_file(average_prices_df, 'average_prices.csv')

    return "Результаты сохранены в файлы 'detailed_results.csv' и 'average_prices.csv'."


if __name__ == "__main__":
    result_message = handle_parsing()
    print(result_message)
