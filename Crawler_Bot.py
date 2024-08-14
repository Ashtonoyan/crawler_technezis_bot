from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import pandas as pd
import sqlite3
from telegram.constants import ParseMode
from io import BytesIO
import my_parser



def init_db():
    conn = sqlite3.connect('information.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect('information.db')
    cursor = conn.cursor()
    try:
        cursor.executemany('''
            INSERT INTO products (title, url, xpath) VALUES (?, ?, ?)
        ''', data)
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()




async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Нажмите на кнопку и загрузите Excel-файл с данными о товарах.")


async def handle_file(update: Update, context: CallbackContext) -> None:

    if update.message.document:
        document = update.message.document
        mime_type = document.mime_type


        if mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            file = await document.get_file()


            file_bytes = await file.download_as_bytearray()


            with open('user_data.xlsx', 'wb') as f:
                f.write(file_bytes)


            df = pd.read_excel('user_data.xlsx')


            df_str = df.to_string(index=False)
            await update.message.reply_text(f"Содержимое файла:\n{df_str}")


            data = list(df[['title', 'url', 'xpath']].itertuples(index=False, name=None))


            save_to_db(data)
            await update.message.reply_text("Данные успешно сохранены в базу данных.")

            table_str = df.to_string(index=False)
            markdown_table = f"```\n{table_str}\n```"
            await update.message.reply_text(f"Содержимое файла в другом виде:\n{markdown_table}", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text("Пожалуйста, загрузите файл в формате Excel (.xlsx).")
    else:
        await update.message.reply_text("Пожалуйста, загрузите файл Excel.")


    result_message = my_parser.handle_parsing()


    with open('average_prices.csv', 'r', encoding='utf-8') as f:
        average_prices_content = f.read()
    await update.message.reply_text(f"Содержимое файла 'average_prices.csv':\n\n{average_prices_content}")
    with open('detailed_results.csv', 'rb') as f:
        await update.message.reply_document(document=f, filename='detailed_results.csv')

def main() -> None:

    TOKEN = '7528570553:AAEb529FR6NqpM6Xfc4ulfEA2IBaCHgLUZY'
    init_db()


    application = Application.builder().token(TOKEN).build()


    application.add_handler(CommandHandler("start", start))


    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))


    application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())