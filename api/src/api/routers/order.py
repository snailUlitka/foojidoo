from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.db.schemes import User
from api.dependencies import get_current_user, get_order_repo, get_restaurant_repo
from api.models.order import OrderItemCreate, OrderItemRead, OrderRead
from api.repositories.order import OrderRepository
from api.repositories.restaurant import RestaurantRepository

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/items",
    summary="Add a dish to the current order",
)
def add_dish_to_order(
    payload: OrderItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
    restaurant_repo: Annotated[RestaurantRepository, Depends(get_restaurant_repo)],
) -> OrderItemRead:
    dish = restaurant_repo.get_dish(payload.restaurant_id, payload.dish_id)
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found",
        )

    order_repo.create_order(current_user)
    try:
        item = order_repo.add_item(
            user_id=current_user.user_id,
            restaurant_id=payload.restaurant_id,
            dish_id=payload.dish_id,
            quantity=payload.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return OrderItemRead(
        restaurant_id=item.restaurant_id,
        dish_id=item.dish_id,
        quantity=item.quantity,
        name=dish.name,
        description=dish.description,
        price=dish.price,
    )


@router.get(
    "/",
    summary="View the current order",
)
def view_current_order(
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
) -> OrderRead:
    try:
        order = order_repo.view_order(current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Order not found") from e

    items = []
    for it in order.items:
        dish = it.dish
        items.append(
            OrderItemRead(
                restaurant_id=it.restaurant_id,
                dish_id=it.dish_id,
                quantity=it.quantity,
                name=dish.name,
                description=dish.description,
                price=dish.price,
            )
        )

    return OrderRead(
        user_id=order.user_id,
        status=order.status,
        payment_method=order.payment_method,
        created_at=order.created_at,
        items=items,
    )


@router.delete(
    "/items/{restaurant_id}/{dish_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a dish from the current order",
)
def remove_dish_from_order(
    restaurant_id: int,
    dish_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
) -> None:
    try:
        order_repo.remove_item(
            user_id=current_user.user_id,
            restaurant_id=restaurant_id,
            dish_id=dish_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Item not found in order") from e
