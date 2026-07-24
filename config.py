import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в файле .env!")
if not DB_PATH:
    raise ValueError("DB_PATH не задан в файле .env!")