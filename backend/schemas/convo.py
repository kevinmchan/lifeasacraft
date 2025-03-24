from pydantic import BaseModel


class Message(BaseModel):
    role: str
    agent: str
    content: str
    timestamp: str

class Convo(BaseModel):
    title: str
    messages: list[Message]