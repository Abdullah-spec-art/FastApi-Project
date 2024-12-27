from sqlmodel import create_engine, Session
from core.config import settings
from typing import Generator


engine = create_engine(settings.DATABASE_URL, echo=True)



def get_db() -> Generator:
    with Session(engine) as session:
        yield session