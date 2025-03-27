from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from schemas.message import Message, MessageRead
from schemas.agent import Agent


class ProjectCreate(BaseModel):
    title: str
    intention: str
    parent_project_id: str | None = None


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    intention: str
    parent_project_id: str | None = None
    child_projects: list[Project] | None = None
    messages: list[Message]
    current_agent: Agent | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    intention: str
    parent_project_id: str | None = None
    child_projects: list[Project] | None = None
    messages: list[MessageRead]
    current_agent: Agent | None = None
