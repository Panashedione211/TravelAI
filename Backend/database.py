import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
"""database.py sets up the database connection and session management for the application. 
It uses SQLAlchemy to create an engine and a session factory that can be used to interact with the 
database in the API endpoints. The get_db function is a dependency that can be injected into API 
endpoints to provide a database session that is properly closed after the request is completed."""
# database connection string, it can be set in the .env file or it defaults to a local SQLite database file named travelai.db in the current directory.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travelai.db")

# sets up databases connection and session management, it creates a SQLAlchemy engine and a session factory that can be used to interact with the database in the API endpoints.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# creates database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
