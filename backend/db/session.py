import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: sqlite not intended for production use
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lifeasacraft.db")
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)  # SQLite specific

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
