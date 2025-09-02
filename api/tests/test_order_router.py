from __future__ import annotations

import pytest

from api.dependencies import get_current_user, get_order_repo, get_restaurant_repo


class DummyUser:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id


class DummyDish:
    def __init__(self, name: str, description: str, price: float) -> None:
        self.name = name
        self.description = description
        self.price = price


class DummyOrderItem:
    def __init__(self, restaurant_id: int, dish_id: int, quantity: int, dish: DummyDish) -> None:
        self.restaurant_id = restaurant_id
        self.dish_id = dish_id
        self.quantity = quantity
        self.dish = dish


class DummyOrder:
    def __init__(self, user_id: int, items: list[DummyOrderItem]) -> None:
        self.user_id = user_id
        self.status = "open"
        self.payment_method = "cash"
        self.created_at = "now"
        self.items = items


class DummyRestaurantRepo:
    def __init__(self) -> None:
        self.dishes: dict[tuple[int, int], DummyDish] = {
            (1, 1): DummyDish("pizza", "cheese", 10.0)
        }

    def get_dish(self, restaurant_id: int, dish_id: int) -> DummyDish | None:
        return self.dishes.get((restaurant_id, dish_id))


class DummyOrderRepo:
    def __init__(self, restaurant_repo: DummyRestaurantRepo) -> None:
        self.restaurant_repo = restaurant_repo
        self.items: list[DummyOrderItem] = []

    def create_order(self, user: DummyUser) -> None:  # pragma: no cover - simple placeholder
        self.user_id = user.user_id

    def add_item(
        self, *, user_id: int, restaurant_id: int, dish_id: int, quantity: int
    ) -> DummyOrderItem:
        dish = self.restaurant_repo.get_dish(restaurant_id, dish_id)
        if not dish:
            raise ValueError("dish not found")
        item = DummyOrderItem(restaurant_id, dish_id, quantity, dish)
        self.items.append(item)
        return item

    def view_order(self, user_id: int) -> DummyOrder:
        if not self.items:
            raise ValueError("no order")
        return DummyOrder(user_id, self.items)

    def remove_item(self, *, user_id: int, restaurant_id: int, dish_id: int) -> None:
        for idx, it in enumerate(self.items):
            if it.restaurant_id == restaurant_id and it.dish_id == dish_id:
                self.items.pop(idx)
                return
        raise ValueError("not found")


@pytest.fixture
def order_setup(client):
    restaurant_repo = DummyRestaurantRepo()
    order_repo = DummyOrderRepo(restaurant_repo)
    user = DummyUser(1)
    client.app.dependency_overrides[get_current_user] = lambda: user
    client.app.dependency_overrides[get_order_repo] = lambda: order_repo
    client.app.dependency_overrides[get_restaurant_repo] = lambda: restaurant_repo
    return client, order_repo, restaurant_repo, user


def test_add_dish_to_order_success(order_setup) -> None:
    client, _, _, _ = order_setup
    payload = {"restaurant_id": 1, "dish_id": 1, "quantity": 2}
    response = client.post("/order/orders/items", json=payload)
    assert response.status_code == 200
    assert response.json()["quantity"] == 2


def test_add_dish_to_order_dish_not_found(order_setup) -> None:
    client, _, restaurant_repo, _ = order_setup
    restaurant_repo.dishes.clear()
    payload = {"restaurant_id": 1, "dish_id": 2, "quantity": 1}
    response = client.post("/order/orders/items", json=payload)
    assert response.status_code == 404


def test_view_current_order_success(order_setup) -> None:
    client, order_repo, _, user = order_setup
    order_repo.add_item(user_id=user.user_id, restaurant_id=1, dish_id=1, quantity=1)
    response = client.get("/order/orders/")
    assert response.status_code == 200
    assert response.json()["items"][0]["dish_id"] == 1


def test_remove_dish_success(order_setup) -> None:
    client, order_repo, _, user = order_setup
    order_repo.add_item(user_id=user.user_id, restaurant_id=1, dish_id=1, quantity=1)
    response = client.delete("/order/orders/items/1/1")
    assert response.status_code == 204
    assert order_repo.items == []


def test_remove_dish_not_found(order_setup) -> None:
    client, _, _, _ = order_setup
    response = client.delete("/order/orders/items/1/1")
    assert response.status_code == 404
