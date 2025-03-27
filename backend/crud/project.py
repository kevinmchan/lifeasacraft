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
    db_message = Message(
        id=message_id,
        project_id=project_id,
        **message.model_dump(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
