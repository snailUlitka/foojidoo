from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class UserCreate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3)]
    password: Annotated[str, StringConstraints(min_length=6)]
    phone: str
    address: str


class UserRead(BaseModel):
    user_id: int
    name: str
    phone: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Annotated[str | None, StringConstraints(min_length=3)]
    password: Annotated[str | None, StringConstraints(min_length=6)]
    phone: str | None
    address: str | None
