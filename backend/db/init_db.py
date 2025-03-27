from sqlmodel import SQLModel

from models.project import Project, Message, Agent  # type: ignore | importing so SQLModel can discover models

from db.session import engine


def init_db():
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
