import asyncpg
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_db():
    """ Creează o conexiune cu PostgreSQL """
    return await asyncpg.connect(DATABASE_URL)

async def add_user(telegram_id: int, name: str, phone: str, email: str, user_type: str):
    """ Adaugă un utilizator nou în baza de date """
    conn = await connect_db()
    await conn.execute(
        "INSERT INTO users (telegram_id, name, phone, email, user_type) VALUES ($1, $2, $3, $4, $5)",
        telegram_id, name, phone, email, user_type
    )
    await conn.close()

async def get_user(telegram_id: int):
    """ Verifică dacă utilizatorul există deja în baza de date """
    conn = await connect_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
    await conn.close()
    return user
