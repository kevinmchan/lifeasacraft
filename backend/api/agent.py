from fastapi import APIRouter, Depends
from schemas.agent import AgentRead, AgentCreate
from db.session import get_db
from sqlalchemy.orm import Session
from crud.agent import read_agent, read_all_agents, create_agent

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/all", response_model=list[AgentRead])
def read_all_agents_endpoint(db: Session = Depends(get_db)):
    """Get all agent objects"""
    agents = read_all_agents(db)
    return agents


@router.get("/{id}", response_model=AgentRead)
def read_agent_endpoint(id: str, db: Session = Depends(get_db)):
    """Get an agent object by it's id"""
    return read_agent(id, db)


@router.post("/", response_model=AgentRead)
def create_agent_endpoint(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent object"""
    db_agent = create_agent(db, agent)
    return db_agent
