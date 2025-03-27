from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.project import Project
from db.session import get_db
from crud.project import create_project
from schemas.project import ProjectRead, ProjectCreate
from schemas.message import Message as MessageRead, MessageCreate
from crud.project import add_message

router = APIRouter(prefix="/project", tags=["project"])


# TODO: consider not returning the entire project object
@router.get("/all", response_model=list[ProjectRead])
def read_all_projects_endpoint(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


# TODO: consider not returning the entire project object
@router.get("/{id}", response_model=ProjectRead)
def read_project_endpoint(id: str, db: Session = Depends(get_db)):
    project = db.get(Project, id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {id} not found")
    return project


@router.post("/", response_model=ProjectRead)
def create_project_endpoint(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = create_project(db, project)
    return db_project


@router.post("/{id}/message", response_model=MessageRead)
def add_message_endpoint(
    id: str, message: MessageCreate, db: Session = Depends(get_db)
):
    message_response = add_message(db, project_id=id, message=message)
    return message_response
