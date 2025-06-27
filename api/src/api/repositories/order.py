from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.db.schemes import Order, OrderDish, User


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_current_order(self, user_id: int) -> Order | None:
        """Fetch the single current order for a user, or None."""
        return self.db.query(Order).filter(Order.user_id == user_id).first()

    def create_order(
        self,
        user: User,
        status: str = "pending",
        payment_method: str = "not_selected",
    ) -> Order:
        """Create a new order if none exists for the user."""
        existing = self.get_current_order(user.user_id)
        if existing:
            return existing

        order = Order(
            user_id=user.user_id,
            status=status,
            payment_method=payment_method,
            created_at=datetime.now(UTC),
        )
        self.db.add(order)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            msg = "Order already exists for this user."
            raise ValueError(msg) from e
        self.db.refresh(order)
        return order

    def add_item(
        self,
        user_id: int,
        restaurant_id: int,
        dish_id: int,
        quantity: int = 1,
    ) -> OrderDish:
        """
        Add a dish to the user's current order.
        If the dish is already present, increment its quantity.
        """
        order = self.get_current_order(user_id)
        if not order:
            msg = "Order does not exist."
            raise ValueError(msg)

        item = (
            self.db.query(OrderDish)
            .filter_by(user_id=user_id, restaurant_id=restaurant_id, dish_id=dish_id)
            .first()
        )
        if item:
            item.quantity += quantity
        else:
            item = OrderDish(
                user_id=user_id,
                restaurant_id=restaurant_id,
                dish_id=dish_id,
                quantity=quantity,
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item(
        self,
        user_id: int,
        restaurant_id: int,
        dish_id: int,
    ) -> None:
        """Remove a dish from the user's order completely."""
        item = (
            self.db.query(OrderDish)
            .filter_by(user_id=user_id, restaurant_id=restaurant_id, dish_id=dish_id)
            .first()
        )
        if not item:
            msg = "Item not found in order."
            raise ValueError(msg)
        self.db.delete(item)
        self.db.commit()

    def view_order(self, user_id: int) -> Order:
        """
        Return the order along with its items and related dish info.
        """
        order = self.get_current_order(user_id)
        if not order:
            msg = "Order does not exist."
            raise ValueError(msg)
        return order
