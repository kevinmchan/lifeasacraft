from pydantic import BaseModel
from typing import Literal, Any

supported_models = Literal["user", "o3-mini"]
supported_roles = Literal["user", "assistant"]


class Agent(BaseModel):
    id: str
    role: supported_roles
    model: supported_models
    name: str
    params: dict[str, Any]
