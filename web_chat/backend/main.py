from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
import json
from dotenv import load_dotenv
from ai import ask_openai
from bitrix import create_deal, add_comment_to_deal, notify_manager_to_join_chat, get_latest_messages_from_bitrix
import asyncio
from asyncio import Task
from db import create_tables

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_WEB")

app = FastAPI()

# Permitem conexiuni WebSocket și HTTP de la frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrânge la frontend-ul tău
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Elimină metodele nedorite
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await create_tables()

class User(BaseModel):
    name: str
    phone: str
    email: str

async def connect_db():
    return await asyncpg.connect(DATABASE_URL)

# Dicționar global pentru a păstra ID-urile mesajelor deja procesate
processed_messages = {}

async def fetch_bitrix_messages(deal_id):
    """ Verifică periodic mesajele noi din Bitrix24 și le trimite în WebSocket, excluzând notificările și AI """
    global processed_messages

    if deal_id not in processed_messages:
        processed_messages[deal_id] = set()

    while True:
        messages = get_latest_messages_from_bitrix(deal_id)

        if messages:
            for message in messages:
                message_id = message["ID"]
                message_text = message["COMMENT"].strip()  # Eliminăm spațiile goale

                # Excludem notificările și răspunsurile AI din Bitrix24
                if message_id not in processed_messages[deal_id] and not message_text.startswith(("🔔", "**Întrebare:**", "🤖 AI:")):
                    processed_messages[deal_id].add(message_id)  # Marcam mesajul ca procesat
                    
                    # Trimitem doar mesajele scrise de manager
                    await manager.send_message(deal_id, f"👔 Manager: {message_text}")

        await asyncio.sleep(5)  # Verificăm la fiecare 5 secunde

@app.post("/register")
async def register_user(user: User):
    """ Înregistrează un utilizator și creează un deal în Bitrix24 """
    conn = await connect_db()
    deal_id = create_deal(user.name, user.phone, user.email, "Web Chat")
    await conn.execute("INSERT INTO users (name, phone, email, deal_id) VALUES ($1, $2, $3, $4)", user.name, user.phone, user.email, deal_id)
    await conn.close()
    return {"message": "User registered successfully", "deal_id": deal_id}

class ConnectionManager:
    """ Gestionăm conexiunile WebSocket pentru utilizatori și manageri """
    def __init__(self):
        self.active_connections = {}
        self.managers = {}

    async def connect(self, websocket: WebSocket, user_type: str, deal_id: int):
        
        if user_type == "manager":
            self.managers[deal_id] = websocket
        else:
            self.active_connections[deal_id] = websocket

    async def disconnect(self, websocket: WebSocket, user_type: str, deal_id: int):
        if user_type == "manager":
            self.managers.pop(deal_id, None)
        else:
            self.active_connections.pop(deal_id, None)

    async def send_message(self, deal_id: int, message: str):
        if deal_id in self.active_connections:
            await self.active_connections[deal_id].send_text(message)
        if deal_id in self.managers:
            await self.managers[deal_id].send_text(message)

manager = ConnectionManager()

manager_tasks = {}  # Dicționar pentru a ține evidența task-urilor active

@app.websocket("/ws/chat/{user_type}/{deal_id}")
async def websocket_endpoint(websocket: WebSocket, user_type: str, deal_id: int):
    """ WebSocket pentru utilizatori și manageri """
    await websocket.accept()
    await manager.connect(websocket, user_type, deal_id)

    if user_type == "manager":
        if deal_id not in manager_tasks:
            task = asyncio.create_task(fetch_bitrix_messages(deal_id))
            manager_tasks[deal_id] = task

    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            message_text = data_json.get("message", "")

            if user_type == "manager":
                await manager.send_message(deal_id, f"👔 Manager: {message_text}")
                add_comment_to_deal(deal_id, message_text)  # Salvăm mesajul în Bitrix24
            else:
                response = await ask_openai(message_text)
                await manager.send_message(deal_id, f"🤖 AI: {response}")
                add_comment_to_deal(deal_id, f"**Întrebare:** {message_text}\n**Răspuns:** {response}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_type, deal_id)
        if user_type == "manager" and deal_id in manager_tasks:
            manager_tasks[deal_id].cancel()  # Oprire fetching mesaje din Bitrix24
            del manager_tasks[deal_id]

        
@app.post("/notify_manager/{deal_id}")
async def notify_manager(deal_id: int):
    """ Trimite notificare în Bitrix24 pentru manager când trebuie să se alăture chat-ului """
    notify_manager_to_join_chat(deal_id)
    return {"message": "Notificare trimisă managerului"}
