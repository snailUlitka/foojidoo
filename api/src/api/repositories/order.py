from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.db.schemes import Order, User


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_current_order(self, user_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.user_id == user_id).first()

    def create_order(
        self,
        user: User,
        status: str = "pending",
        payment_method: str = "not_selected",
    ) -> Order:
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

    def update_order(
        self,
        user_id: int,
        status: str | None = None,
        payment_method: str | None = None,
    ) -> Order:
        order = self.get_current_order(user_id)
        if not order:
            msg = "Order does not exist."
            raise ValueError(msg)

        if status:
            order.status = status
        if payment_method:
            order.payment_method = payment_method

        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, user_id: int) -> None:
        order = self.get_current_order(user_id)
        if order:
            self.db.delete(order)
            self.db.commit()
