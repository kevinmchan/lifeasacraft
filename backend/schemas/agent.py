from pydantic import BaseModel, ConfigDict
from typing import Literal, Any

supported_models = Literal["user", "o3-mini"]
supported_roles = Literal["user", "assistant"]


class Agent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: supported_roles
    model: supported_models
    name: str
    params: dict[str, Any]


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: supported_roles
    model: supported_models
    name: str
    params: dict[str, Any]


class AgentCreate(BaseModel):
    id: str
    role: supported_roles
    model: supported_models
    name: str
    params: dict[str, Any]
