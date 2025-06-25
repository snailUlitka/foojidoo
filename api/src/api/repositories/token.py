from datetime import UTC, datetime

from sqlalchemy.orm import Session

from api.db.schemes import RefreshToken


class TokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(rt)
        self.db.commit()

    def is_refresh_token_valid(self, user_id: int, token: str) -> bool:
        rt = self.db.query(RefreshToken).filter_by(user_id=user_id, token=token).first()
        return bool(rt and rt.expires_at > datetime.now(UTC))

    def revoke_refresh_token(self, user_id: int, token: str) -> None:
        (self.db.query(RefreshToken).filter_by(user_id=user_id, token=token).delete())
        self.db.commit()
