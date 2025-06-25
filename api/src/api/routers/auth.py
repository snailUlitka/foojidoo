from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.repositories.token import TokenRepository
from api.repositories.user import UserRepository
from api.services.auth import create_tokens, verify_token
from api.settings import Settings, get_settings

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(form.username)

    if not user or not user_repo.verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, refresh_token, rt_expiry = create_tokens(user.user_id, settings)
    TokenRepository(db).add_refresh_token(user.user_id, refresh_token, rt_expiry)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/refresh")
def refresh(
    refresh_token: str,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    try:
        payload = verify_token(refresh_token, settings)
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

    token_repo = TokenRepository(db)
    if not token_repo.is_refresh_token_valid(user_id, refresh_token):
        raise HTTPException(status_code=401, detail="Refresh expired")

    access_token, new_refresh, rt_expiry = create_tokens(user_id, settings)
    token_repo.revoke_refresh_token(user_id, refresh_token)
    token_repo.add_refresh_token(user_id, new_refresh, rt_expiry)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/logout")
def logout(
    refresh_token: str,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    try:
        payload = verify_token(refresh_token, settings)
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

    TokenRepository(db).revoke_refresh_token(user_id, refresh_token)
    return {"detail": "Success logout"}
