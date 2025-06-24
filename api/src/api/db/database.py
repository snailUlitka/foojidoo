from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.settings import Settings, get_settings


def get_engine(settings: Annotated[Settings, Depends(get_settings)]) -> Engine:
    return create_engine(str(settings.database_url))


def get_session_local(engine: Annotated[Engine, Depends(get_engine)]) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db(
    session_local: Annotated[sessionmaker, Depends(get_session_local)],
) -> Generator[Session, None, None]:
    db = session_local()

    try:
        yield db
    finally:
        db.close()
