from typing import Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from schemas.agent import supported_models, supported_roles


class MessageCreate(BaseModel):
    content: str
    agent_name: str
    agent_role: supported_roles
    agent_model: supported_models
    agent_params: dict[str, Any] | None = None
    timestamp: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    agent_name: str
    agent_role: supported_roles
    agent_model: supported_models
    agent_params: dict[str, Any] | None = None
    timestamp: datetime


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    agent_name: str
    agent_role: supported_roles
    agent_model: supported_models
    agent_params: dict[str, Any] | None = None
    timestamp: datetime
