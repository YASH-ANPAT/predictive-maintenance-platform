from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Create a configured Session class
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)




def get_db():
    """
    Dependency that provides a database session.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()