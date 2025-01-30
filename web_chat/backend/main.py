from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv
from ai import ask_openai  # Importă funcția AI

# Încărcăm variabilele de mediu
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# 🔹 Activăm CORS pentru a permite accesul din frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Poți restricționa la "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 WebSocket pentru chat live
class ConnectionManager:
    """ Gestionăm conexiunile WebSocket pentru chat în timp real """
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """ WebSocket care primește mesaje de la client și trimite răspunsuri AI """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📩 Mesaj primit: {data}")  # Debugging

            # Generăm răspunsul AI
            response = await ask_openai(data)

            print(f"✅ Răspuns AI generat: {response}")  # Debugging

            # Trimitem răspunsul înapoi clientului
            await manager.send_message(response)

    except WebSocketDisconnect:
        print("❌ Utilizator deconectat")
        await manager.disconnect(websocket)