from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.schemes import User
from api.repositories.order import OrderRepository
from api.repositories.user import UserRepository
from api.services.auth import verify_token
from api.settings import Settings, get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_order_repo(db: Annotated[Session, Depends(get_db)]) -> OrderRepository:
    return OrderRepository(db)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    try:
        payload = verify_token(token, settings)
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Uknown user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
