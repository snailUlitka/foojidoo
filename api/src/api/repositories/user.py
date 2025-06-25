from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.db.schemes import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.name == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).get(user_id)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(
        self,
        username: str,
        password: str,
        phone: str,
        address: str,
    ) -> User:
        hashed = pwd_context.hash(password)

        user = User(name=username, password=hashed, phone=phone, address=address)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update_user(self, user: User, **fields: str | bytes) -> User:
        for attr, val in fields.items():
            if val is None:
                continue

            setattr(
                user,
                attr,
                pwd_context.hash(val) if attr == "password" else val,
            )
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
