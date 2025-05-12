from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from functools import wraps
import settings

DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Dependency for FastAPI
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def with_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db: Session = SessionLocal()
        try:
            return func(*args, db=db, **kwargs)
        finally:
            db.close()

    return wrapper
