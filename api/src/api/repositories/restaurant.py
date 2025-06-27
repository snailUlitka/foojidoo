from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.db.schemes import Dish, Restaurant


class RestaurantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_restaurants(self) -> list[Restaurant]:
        """Return all restaurants."""
        return self.db.query(Restaurant).all()

    def get_restaurant(self, restaurant_id: int) -> Restaurant | None:
        """Fetch a single restaurant by its ID."""
        return (
            self.db.query(Restaurant)
            .filter(Restaurant.restaurant_id == restaurant_id)
            .first()
        )

    def create_restaurant(
        self,
        name: str,
        description: str,
        address: str,
        phone: str,
    ) -> Restaurant:
        """Create a new restaurant."""
        restaurant = Restaurant(
            name=name,
            description=description,
            address=address,
            phone=phone,
        )
        self.db.add(restaurant)
        self.db.commit()
        self.db.refresh(restaurant)
        return restaurant

    def delete_restaurant(self, restaurant_id: int) -> None:
        """Delete a restaurant (and cascade-delete its dishes)."""
        restaurant = self.get_restaurant(restaurant_id)
        if not restaurant:
            msg = f"Restaurant {restaurant_id} not found"
            raise NoResultFound(msg)
        self.db.delete(restaurant)
        self.db.commit()

    def list_menu(self, restaurant_id: int) -> list[Dish]:
        """Return all dishes for a restaurant."""
        return self.db.query(Dish).filter(Dish.restaurant_id == restaurant_id).all()

    def get_dish(
        self,
        restaurant_id: int,
        dish_id: int,
    ) -> Dish | None:
        """Fetch a single Dish by its composite key."""
        return (
            self.db.query(Dish)
            .filter(
                Dish.restaurant_id == restaurant_id,
                Dish.dish_id == dish_id,
            )
            .first()
        )

    def create_dish(
        self,
        restaurant_id: int,
        name: str,
        description: str,
        price: Decimal,
    ) -> Dish:
        """Create a new Dish in a given restaurant."""
        if not self.get_restaurant(restaurant_id):
            msg = "Restaurant not found"
            raise ValueError(msg)

        max_id = (
            self.db.query(func.max(Dish.dish_id))
            .filter(Dish.restaurant_id == restaurant_id)
            .scalar()
        ) or 0

        new_id = max_id + 1

        dish = Dish(
            dish_id=new_id,
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
        )

        self.db.add(dish)
        self.db.commit()
        self.db.refresh(dish)

        return dish

    def delete_dish(self, restaurant_id: int, dish_id: int) -> None:
        """Delete a Dish by its composite key."""
        dish = self.get_dish(restaurant_id, dish_id)
        if not dish:
            msg = f"Dish {dish_id} in restaurant {restaurant_id} not found"
            raise NoResultFound(msg)
        self.db.delete(dish)
        self.db.commit()
