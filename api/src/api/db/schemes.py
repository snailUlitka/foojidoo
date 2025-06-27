from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    password = Column(String, nullable=False)
    order = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    items = relationship(
        "OrderDish",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="User.user_id == OrderDish.user_id",
        foreign_keys="[OrderDish.user_id]",
        overlaps="items",
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Restaurant(Base):
    __tablename__ = "restaurant"

    restaurant_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    dish = relationship(
        "Dish",
        back_populates="restaurant",
    )
    items = relationship(
        "OrderDish",
        back_populates="restaurant",
        primaryjoin="Restaurant.restaurant_id == OrderDish.restaurant_id",
        foreign_keys="[OrderDish.restaurant_id]",
        overlaps="items",
    )


class Dish(Base):
    __tablename__ = "dish"

    dish_id = Column(Integer, primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)

    restaurant = relationship(
        "Restaurant",
        back_populates="dish",
    )
    items = relationship(
        "OrderDish",
        back_populates="dish",
        primaryjoin=(
            "and_(OrderDish.dish_id == Dish.dish_id, "
            "OrderDish.restaurant_id == Dish.restaurant_id)"
        ),
        foreign_keys="[OrderDish.dish_id, OrderDish.restaurant_id]",
        overlaps="items,restaurant",
    )


class Order(Base):
    __tablename__ = "order"

    user_id = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    status = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship(
        "User",
        back_populates="order",
    )
    items = relationship(
        "OrderDish",
        back_populates="order",
        primaryjoin="Order.user_id == OrderDish.user_id",
        foreign_keys="[OrderDish.user_id]",
        overlaps="items,user",
    )


class OrderDish(Base):
    __tablename__ = "order_dish"

    dish_id = Column(
        Integer,
        primary_key=True,
    )
    restaurant_id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["dish_id", "restaurant_id"],
            ["dish.dish_id", "dish.restaurant_id"],
            ondelete="CASCADE",
        ),
    )

    user = relationship(
        "User",
        back_populates="items",
        primaryjoin="OrderDish.user_id == User.user_id",
        foreign_keys="[OrderDish.user_id]",
        overlaps="items",
    )
    restaurant = relationship(
        "Restaurant",
        back_populates="items",
        primaryjoin="OrderDish.restaurant_id == Restaurant.restaurant_id",
        foreign_keys="[OrderDish.restaurant_id]",
        overlaps="items,restaurant",
    )
    dish = relationship(
        "Dish",
        back_populates="items",
        primaryjoin=(
            "and_(OrderDish.dish_id == Dish.dish_id, "
            "OrderDish.restaurant_id == Dish.restaurant_id)"
        ),
        foreign_keys="[OrderDish.dish_id, OrderDish.restaurant_id]",
        overlaps="items,restaurant",
    )
    order = relationship(
        "Order",
        back_populates="items",
        primaryjoin="OrderDish.user_id == Order.user_id",
        foreign_keys="[OrderDish.user_id]",
        overlaps="items,user",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship(
        "User",
        back_populates="refresh_tokens",
        primaryjoin="RefreshToken.user_id == User.user_id",
        foreign_keys="[RefreshToken.user_id]",
    )
