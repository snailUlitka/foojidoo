from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound

from api.dependencies import get_restaurant_repo
from api.models.restaurant import (
    DishCreate,
    DishRead,
    MenuRead,
    RestaurantCreate,
    RestaurantRead,
)
from api.repositories.restaurant import RestaurantRepository

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get(
    "/",
    summary="List with all restaurants",
)
def list_restaurants(
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> list[RestaurantRead]:
    return [RestaurantRead.model_validate(r) for r in repo.list_restaurants()]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new restaurant",
)
def create_restaurant(
    payload: RestaurantCreate,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> RestaurantRead:
    return repo.create_restaurant(
        name=payload.name,
        description=payload.description or "",
        address=payload.address,
        phone=payload.phone,
    )


@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a restaurant",
)
def delete_restaurant(
    restaurant_id: int,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> None:
    try:
        repo.delete_restaurant(restaurant_id)
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        ) from e


@router.get(
    "/{restaurant_id}/menu",
    summary="Restaurants menu (List with dishes)",
)
def get_menu(
    restaurant_id: int,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> MenuRead:
    restaurant = repo.get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uknown restaurant",
        )

    dishes = [DishRead.model_validate(d) for d in repo.list_menu(restaurant_id)]

    return MenuRead(
        restaurant=restaurant,
        dishes=dishes,
    )


@router.get(
    "/{restaurant_id}/dishes/{dish_id}",
    summary="Dish details",
)
def get_dish(
    restaurant_id: int,
    dish_id: int,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> DishRead:
    dish = repo.get_dish(restaurant_id, dish_id)

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uknown dish",
        )

    return DishRead.model_validate(dish)


@router.post(
    "/{restaurant_id}/dishes",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dish in a restaurant",
)
def create_dish(
    restaurant_id: int,
    payload: DishCreate,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> DishRead:
    if not repo.get_restaurant(restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return repo.create_dish(
        restaurant_id=restaurant_id,
        name=payload.name,
        description=payload.description or "",
        price=payload.price,
    )


@router.delete(
    "/{restaurant_id}/dishes/{dish_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dish from a restaurant",
)
def delete_dish(
    restaurant_id: int,
    dish_id: int,
    repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> None:
    try:
        repo.delete_dish(restaurant_id, dish_id)
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found",
        ) from e
