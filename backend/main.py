from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from schemas.convo import Convo, Message
from typing import List
import json
from datetime import datetime

app = FastAPI()

conv_data = {
    "title": "Our conversation",
    "messages": [
        {
            "role": "assistant",
            "agent": "chiefofstaff",
            "content": "Hello! How can I help you today?", 
            "timestamp": "2021-10-01T12:00:00Z"
        },
        {
            "role": "user",
            "agent": "kevin",
            "content": "I need help with my order.", 
            "timestamp": "2021-10-01T12:01:00Z"
        },
        {
            "role": "assistant",
            "agent": "chiefofstaff",
            "content": "Sure! What is your order number?", 
            "timestamp": "2021-10-01T12:02:00Z"
        },
        {
            "role": "user",
            "agent": "kevin",
            "content": "123456", 
            "timestamp": "2021-10-01T12:03:00Z"
        },
        {
            "role": "assistant",
            "agent": "chiefofstaff",
            "content": "Thank you! Let me check on that for you.", 
            "timestamp": "2021-10-01T12:04:00Z"
        }
    ]
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.get("/convo")
def read_convo_endpoint() -> Convo:
    convo = Convo(**conv_data)
    return convo

@app.post("/convo/message")
def add_message_endpoint(message: Message) -> Convo:
    conv_data["messages"].append(message.dict())
    convo = Convo(**conv_data)
    return convo

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add received message to conversation
            conv_data["messages"].append(message_data)
            
            # Send acknowledgment
            await manager.send_personal_message(
                {
                    "type": "receipt", 
                    "status": "received", 
                    "timestamp": datetime.now().isoformat()
                },
                websocket,
            )
            
            # You could simulate a bot response here
            if message_data["role"] == "user":
                assistant_message = {
                    "role": "assistant",
                    "agent": "chatbot",
                    "content": f"Echo: {message_data['content']}",
                    "timestamp": datetime.now().isoformat()
                }
                conv_data["messages"].append(assistant_message)
                
                # Broadcast the assistant message to all clients
                await manager.broadcast(assistant_message)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)