from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    restaurant_id: int
    dish_id: int
    quantity: Annotated[int, Field(gt=0)] = 1


class OrderItemRead(BaseModel):
    restaurant_id: int
    dish_id: int
    quantity: int
    name: str
    description: str | None

    price: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    user_id: int
    status: str
    payment_method: str
    created_at: datetime
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)
