import asyncpg
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_db():
    """ Creează o conexiune cu PostgreSQL """
    return await asyncpg.connect(DATABASE_URL)

async def add_user(telegram_id: int, name: str, phone: str, email: str, user_type: str, deal_id: int):
    """ Adaugă un utilizator nou în baza de date, inclusiv deal_id """
    conn = await connect_db()

    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

    if user:
        print(f"⚠️ Utilizatorul {telegram_id} există deja, actualizăm deal_id.")
        await conn.execute(
            "UPDATE users SET deal_id = $1 WHERE telegram_id = $2",
            deal_id, telegram_id
        )
    else:
        await conn.execute(
            "INSERT INTO users (telegram_id, name, phone, email, user_type, deal_id) VALUES ($1, $2, $3, $4, $5, $6)",
            telegram_id, name, phone, email, user_type, deal_id
        )
        print(f"✅ Utilizatorul {telegram_id} a fost adăugat în baza de date.")

    await conn.close()

async def get_user(telegram_id: int):
    """ Returnează informațiile unui utilizator dacă există în baza de date """
    conn = await connect_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
    await conn.close()
    return user
