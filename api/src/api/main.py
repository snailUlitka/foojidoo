import uvicorn
from fastapi import FastAPI

from api import __version__
from api.routers import auth, order, restaurant, user

app = FastAPI(title="foojidoo", version=__version__)

app.include_router(auth.router, prefix="/auth")
app.include_router(order.router, prefix="/order")
app.include_router(restaurant.router, prefix="/restaurant")
app.include_router(user.router, prefix="/user")


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104


if __name__ == "__main__":
    main()
