from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

#engine = create_engine(DATABASE_URL)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300) #neon auto disconnects after 5 minute thats why we have to do it

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
