from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
import json
from dotenv import load_dotenv
from ai import ask_openai
from bitrix import create_deal, add_comment_to_deal, notify_manager

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_WEB")

app = FastAPI()

# 🔹 Permitem conexiuni WebSocket și HTTP de la frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrânge la frontend-ul tău
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Elimină metodele nedorite
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    phone: str
    email: str

async def connect_db():
    return await asyncpg.connect(DATABASE_URL)

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

@app.websocket("/ws/chat/{user_type}/{deal_id}")
async def websocket_endpoint(websocket: WebSocket, user_type: str, deal_id: int):
    """ WebSocket pentru utilizatori și manageri """
    print(f"🌐 Încercare de conexiune WebSocket: {user_type} pentru Deal {deal_id}")

    try:
        await websocket.accept()  # 🔹 Acceptăm conexiunea manual
        print(f"✅ WebSocket Acceptat: {user_type} - Deal {deal_id}")

        await manager.connect(websocket, user_type, deal_id)
    except Exception as e:
        print(f"❌ Eroare la acceptarea conexiunii WebSocket: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            message_text = data_json.get("message", "")

            print(f"📩 Mesaj primit ({user_type} - Deal {deal_id}): {message_text}")  # Debugging

            if user_type == "manager":
                await manager.send_message(deal_id, f"👔 Manager: {message_text}")
            else:
                response = await ask_openai(message_text)
                await manager.send_message(deal_id, f"🤖 AI: {response}")
                add_comment_to_deal(deal_id, f"**Întrebare:** {message_text}\n**Răspuns:** {response}")

    except WebSocketDisconnect:
        print(f"❌ {user_type} deconectat de la chat-ul Deal ID {deal_id}")
        await manager.disconnect(websocket, user_type, deal_id)
