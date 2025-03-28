import uuid

from sqlalchemy.orm import Session

from schemas.project import ProjectCreate
from models.project import Project, Message
from schemas.message import MessageCreate


def read_project(db: Session, id: str) -> Project | None:
    """Get a project object by it's id"""
    return db.get(Project, id)


def create_project(db: Session, project: ProjectCreate) -> Project:
    """Create a new convo object"""
    project_id = str(uuid.uuid4())
    db_project = Project(
        id=project_id,
        **project.model_dump(),
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def add_message(db: Session, project_id: str, message: MessageCreate) -> Message:
    """Add a message to a project"""
    message_id = str(uuid.uuid4())
    if message.agent_role == "user":
        # TODO: Consider if the timestamp should be in the user/client's timezone vs UTC (current)
        template = "<metadata><from>{agent_name}</from><timestamp>{timestamp}</timestamp></metadata>\\n{content}"
        content_assistant_view = template.format(
            agent_name=message.agent_name,
            timestamp=message.timestamp,
            content=message.content,
        )
    else:
        content_assistant_view = message.content

    db_message = Message(
        id=message_id,
        project_id=project_id,
        content_assistant_view=content_assistant_view,
        **message.model_dump(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
