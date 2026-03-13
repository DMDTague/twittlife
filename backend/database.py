import json
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
database_url = "sqlite:///twitlife.db"
engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SavedEntity(Base):
    __tablename__ = "entities"
    id = Column(String, primary_key=True, index=True)
    data = Column(JSON)  # full Entity dict

class SavedEvent(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, index=True)
    data = Column(JSON)  # full Event dict

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
