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

    order = relationship("Order", back_populates="user")
    items = relationship("OrderDish", back_populates="user")


class Restaurant(Base):
    __tablename__ = "restaurant"

    restaurant_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    dish = relationship("Dish", back_populates="restaurant")
    items = relationship("OrderDish", back_populates="restaurant")


class Dish(Base):
    __tablename__ = "dish"

    dish_id = Column(Integer, primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurant.restaurant_id"),
        primary_key=True,
    )
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)

    restaurant = relationship("Restaurant", back_populates="dish")
    items = relationship("OrderDish", back_populates="dish")


class Order(Base):
    __tablename__ = "order"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    status = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="order")
    items = relationship("OrderDish", back_populates="order")


class OrderDish(Base):
    __tablename__ = "order_dish"

    dish_id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["dish_id", "restaurant_id"],
            ["dish.dish_id", "dish.restaurant_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurant.restaurant_id"],
            ondelete="CASCADE",
        ),
    )

    user = relationship("User", back_populates="items")
    restaurant = relationship("Restaurant", back_populates="items")
    dish = relationship("Dish", back_populates="items")
    order = relationship(
        "Order",
        primaryjoin="OrderDish.user_id == Order.user_id",
        back_populates="items",
    )
