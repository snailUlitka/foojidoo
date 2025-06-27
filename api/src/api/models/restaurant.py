from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class DishRead(BaseModel):
    dish_id: int
    restaurant_id: int
    name: str
    description: str | None
    price: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]

    model_config = ConfigDict(from_attributes=True)


class RestaurantRead(BaseModel):
    restaurant_id: int
    name: str
    description: str | None
    address: str
    phone: str

    model_config = ConfigDict(from_attributes=True)


class MenuRead(BaseModel):
    restaurant: RestaurantRead
    dishes: list[DishRead]


class RestaurantCreate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    address: Annotated[str, StringConstraints(min_length=1)]
    phone: Annotated[str, StringConstraints(min_length=1)]


class DishCreate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    price: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
