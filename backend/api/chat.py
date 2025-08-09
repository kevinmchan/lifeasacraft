import json
import datetime
import httpx
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from schemas.message import MessageCreate, MessageRead
from schemas.project import ProjectRead
from crud.project import read_project, create_message
from db.session import get_db
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/chat", tags=["chat"])
llm_client = OpenAI()

# Define the containeragent endpoint base URL (adjust host/port as needed)
CONTAINERAGENT_BASE_URL = "http://localhost"  # e.g., if running on port 80


# Async helper to call the containeragent execute endpoint
async def call_containeragent_execute(command: str) -> dict[str, Any]:
    url = f"{CONTAINERAGENT_BASE_URL}/api/execute/"
    payload = {"command": command}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    def remove_connection(self, project_id: str, websocket: WebSocket):
        if project_id in self.active_connections:
            try:
                self.active_connections[project_id].remove(websocket)
            except ValueError:
                print(
                    f"WebSocket not found in active connections for project {project_id}"
                )
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        else:
            print(f"Project ID {project_id} not found in active connections.")

    async def disconnect(self, project_id: str, websocket: WebSocket, code: int = 1000):
        try:
            await websocket.close(code=code)
        except RuntimeError as e:
            print(f"Error closing websocket: {e}")

        self.remove_connection(project_id, websocket)

    async def broadcast(self, project_id: str, message: str):
        for connection in self.active_connections.get(project_id, []):
            try:
                await connection.send_text(message)
            except RuntimeError as e:
                print(
                    f"Error: In project {project_id} attempting to send message: {message}\nFailed with error: {e}"
                )
                if "close message has been sent" in str(e):
                    self.remove_connection(project_id, connection)


manager = ConnectionManager()


@router.websocket("/{project_id}/ws")
async def websocket_endpoint(
    *, websocket: WebSocket, project_id: str, db: Session = Depends(get_db)
):
    await manager.connect(project_id, websocket)

    # Load project data
    db_project = read_project(db, project_id)

    if not db_project:
        # Send error message
        error_message = {
            "type": "error",
            "code": "not_found",
            "message": f"Project with ID {project_id} not found",
        }
        try:
            await websocket.send_json(error_message)
        except RuntimeError as e:
            print(
                f"Error: In project {project_id} attempting to send message: {error_message}\nFailed with error: {e}"
            )
            if "close message has been sent" in str(e):
                manager.remove_connection(project_id, websocket)
                return

        # Close connection
        await manager.disconnect(project_id, websocket)
        return

    project = ProjectRead.model_validate(db_project)

    # TODO: Eventually consider using a shared cache like Redis
    messages = project.messages

    try:
        while True:
            data = await websocket.receive_text()
            message_data = MessageCreate.model_validate(json.loads(data))

            # Add received message to conversation
            db_message = create_message(db, project_id, message_data)
            message = MessageRead.model_validate(db_message)
            messages.append(message)

            # Send acknowledgment
            receipt_message = {
                "type": "receipt",
                "status": "received",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            try:
                await websocket.send_json(receipt_message)
            except RuntimeError as e:
                print(
                    f"Error: In project {project_id} attempting to send message: {receipt_message}\nFailed with error: {e}"
                )
                if "close message has been sent" in str(e):
                    manager.remove_connection(project_id, websocket)
                    return

            # Get response from OpenAI
            # TODO: extract completions logic from endpoint logic
            completion = llm_client.chat.completions.create(
                model="o3-mini",  # TODO: dynamically assign agent model
                # TODO: figure out typing for openai chat messages
                messages=[  # type: ignore
                    {
                        "role": message.agent_role,
                        "content": message.content_assistant_view,
                    }
                    for message in messages
                ],
            )
            response = completion.choices[0].message.content
            if response is None:
                response = "No response"

            # Send the assistant's response back to the client
            message_data = MessageCreate(
                content=response,
                # TODO: dynamically assign agent
                agent_name="chiefofstaff",
                agent_role="assistant",
                agent_model="o3-mini",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            db_message = create_message(db, project_id, message_data)
            message = MessageRead.model_validate(db_message)
            messages.append(message)

            # Broadcast the assistant message to all clients
            await manager.broadcast(project_id, message.model_dump_json())

            # If the response instructs to execute a command, call containeragent
            if response.strip().startswith("execute:"):
                command = response.strip()[len("execute:") :].strip()
                try:
                    execution_result = await call_containeragent_execute(command)
                    # Modify response to include the execution result
                    response = "Execution result: " + json.dumps(execution_result)
                except httpx.HTTPStatusError as e:
                    # Grab additional details from the response, such as its content.
                    detailed_error = e.response.text
                    response = f"Error executing command: {e.response.status_code} - {detailed_error}"

                # Send the execution result back to the client
                message_data = MessageCreate(
                    content=response,
                    # TODO: change agent details to reflect the execution agent
                    agent_name="chiefofstaff",
                    agent_role="assistant",
                    agent_model="o3-mini",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                db_message = create_message(db, project_id, message_data)
                message = MessageRead.model_validate(db_message)
                messages.append(message)

                # Broadcast the assistant message to all clients
                await manager.broadcast(project_id, message.model_dump_json())

    except WebSocketDisconnect:
        manager.remove_connection(project_id, websocket)
