from typing import List
import json
import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from schemas.message import MessageCreate, MessageRead
from schemas.project import ProjectRead
from crud.project import read_project, add_message
from db.session import get_db
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/chat", tags=["chat"])
llm_client = OpenAI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket, code: int = 1000):
        await websocket.close(code=code)
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # Keep track of connections to remove
        closed_connections: list[WebSocket] = []

        # Try sending to each connection
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError as e:
                if "close message has been sent" in str(e):
                    # Connection is already closed
                    closed_connections.append(connection)
                else:
                    # Some other RuntimeError
                    print(f"Error sending message: {e}")

        # Remove closed connections
        for connection in closed_connections:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/{project_id}/ws")
async def websocket_endpoint(
    *, websocket: WebSocket, project_id: str, db: Session = Depends(get_db)
):
    await manager.connect(websocket)

    # Load project data
    db_project = read_project(db, project_id)

    if not db_project:
        # Send error message
        error_message = {
            "type": "error",
            "code": "not_found",
            "message": f"Project with ID {project_id} not found",
        }
        await websocket.send_json(error_message)
        # Close connection
        await manager.disconnect(websocket)
        return

    project = ProjectRead.model_validate(db_project)

    # TODO: Eventually consider using a shared cache like Redis
    messages = project.messages

    try:
        while True:
            data = await websocket.receive_text()
            message_data = MessageCreate.model_validate(json.loads(data))

            # Add received message to conversation
            db_message = add_message(db, project_id, message_data)
            message = MessageRead.model_validate(db_message)
            messages.append(message)

            # Send acknowledgment
            await websocket.send_json(
                {
                    "type": "receipt",
                    "status": "received",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            # Get response from OpenAI
            # TODO: extract completions logic from endpoint logic
            completion = llm_client.chat.completions.create(
                model="o3-mini",  # TODO: dynamically assign agent model
                # TODO: figure out typing for openai chat messages
                messages=[  # type: ignore
                    {
                        "role": message.agent_role,
                        "content": message.content,
                    }
                    for message in messages
                ],
            )
            response = completion.choices[0].message.content
            if response is None:
                response = "No response"

            # Add generated message to conversation
            message_data = MessageCreate(
                content=response,
                # TODO: dynamically assign agent
                agent_name="chiefofstaff",
                agent_role="assistant",
                agent_model="o3-mini",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            db_message = add_message(db, project_id, message_data)
            message = MessageRead.model_validate(db_message)
            messages.append(message)

            # Broadcast the assistant message to all clients
            await manager.broadcast(message.model_dump_json())

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
