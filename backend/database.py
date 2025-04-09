from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL Database URL Format: mysql://user:password@host:port/database
DATABASE_URL = "mysql://django_user:python10534@localhost:3306/event_db"

engine = create_engine(DATABASE_URL, echo=True)

# Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
