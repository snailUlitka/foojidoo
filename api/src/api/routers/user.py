from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.db.schemes import User
from api.dependencies import get_current_user, get_order_repo, get_user_repo
from api.models.user import UserCreate, UserRead, UserUpdate
from api.repositories.order import OrderRepository
from api.repositories.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
def create_user(
    payload: UserCreate,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
) -> UserRead:
    if user_repo.get_by_username(payload.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists",
        )

    user = user_repo.create_user(
        username=payload.name,
        password=payload.password,
        phone=payload.phone,
        address=payload.address,
    )

    _ = order_repo.create_order(user)

    return UserRead.model_validate(user)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
def read_own_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    summary="Update own profile",
)
def update_profile(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    return repo.update_user(current_user, **payload.model_dump())


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete own account",
)
def delete_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> None:
    repo.delete_user(current_user)
