import uvicorn
from fastapi import FastAPI

from api.routers import auth, order, restaurant, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(order.router)
app.include_router(restaurant.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104
