import uuid
from typing import Optional, Any
import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Project(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    title: str
    intention: str

    parent_project_id: Optional[str] = Field(default=None, foreign_key="projects.id")
    current_agent_id: Optional[str] = Field(default=None, foreign_key="agents.id")

    parent_project: Optional["Project"] = Relationship(
        back_populates="child_projects",
        sa_relationship_kwargs={
            "remote_side": "Project.id",
        },
    )

    child_projects: list["Project"] = Relationship(back_populates="parent_project")

    messages: list["Message"] = Relationship(back_populates="project")

    current_agent: Optional["Agent"] = Relationship(
        back_populates="projects", sa_relationship_kwargs={"uselist": False}
    )


# TODO: Figure out circular dependencies issues and move to a separate file
class Message(SQLModel, table=True):
    __tablename__ = "messages"  # type: ignore

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    content: str
    agent_role: str
    agent_name: str
    agent_model: str
    agent_params: dict[str, Any] | None = Field(None, sa_column=Column(JSON))
    project_id: str = Field(foreign_key="projects.id")
    timestamp: datetime.datetime = Field(default_factory=now)

    project: "Project" = Relationship(
        back_populates="messages", sa_relationship_kwargs={"uselist": False}
    )


# TODO: Figure out circular dependencies issues and move to a separate file
class Agent(SQLModel, table=True):
    __tablename__ = "agents"  # type: ignore #

    id: str = Field(primary_key=True)
    role: str
    model: str
    name: str
    params: dict[str, Any] = Field(default=None, sa_column=Column(JSON))

    projects: list[Project] = Relationship(back_populates="current_agent")
