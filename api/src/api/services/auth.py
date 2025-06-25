from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends
from jose import jwt

from api.settings import Settings, get_settings


def create_tokens(
    user_id: int,
    settings: Annotated[Settings, Depends(get_settings)],
) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    access_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    access_token = jwt.encode(
        access_payload,
        settings.token_secret_key.get_secret_value(),
        algorithm=settings.token_algorithm,
    )

    expire_rt = now + timedelta(days=settings.refresh_token_expire_days)
    refresh_payload = {"sub": str(user_id), "exp": expire_rt}
    refresh_token = jwt.encode(
        refresh_payload,
        settings.token_secret_key.get_secret_value(),
        algorithm=settings.token_algorithm,
    )

    return access_token, refresh_token, expire_rt


def verify_token(
    token: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    return jwt.decode(
        token,
        settings.token_secret_key.get_secret_value(),
        algorithms=[settings.token_algorithm],
    )
