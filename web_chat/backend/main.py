from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_WEB")

app = FastAPI()

# 🔹 Activăm CORS pentru a permite cereri din frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Poți specifica "http://localhost:3000" pentru securitate
    allow_credentials=True,
    allow_methods=["*"],  # Permitem toate metodele: GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Permitem toate headerele
)

# 🔹 Model pentru validarea datelor primite
class User(BaseModel):
    name: str
    phone: str
    email: str

async def connect_db():
    """ Creează conexiunea cu PostgreSQL """
    return await asyncpg.connect(DATABASE_URL)

@app.post("/register")
async def register_user(user: User):
    """ Endpoint pentru salvarea utilizatorilor în baza de date """
    conn = await connect_db()
    await conn.execute(
        "INSERT INTO users (name, phone, email) VALUES ($1, $2, $3)",
        user.name, user.phone, user.email
    )
    await conn.close()
    return {"message": "User registered successfully"}
