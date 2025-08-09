from sqlalchemy.orm import Session
from models.project import Agent
from schemas.agent import AgentCreate


def read_agent(id: str, db: Session):
    return db.get(Agent, id)


def read_all_agents(db: Session):
    return db.query(Agent).all()


def create_agent(db: Session, agent: AgentCreate):
    """Create a new agent object"""
    db_agent = Agent(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, id: str, agent: AgentCreate):
    """Update an agent object"""
    db_agent = db.get(Agent, id)
    if db_agent is None:
        return None
    for key, value in agent.model_dump().items():
        setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent
