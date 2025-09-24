from datetime import timedelta
from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.config import settings
from app.schemas.user import UserCreate, UserPublic
from app.crud.user import create_user
from app.core.security import create_access_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", response_model=dict)
def _create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create a new user
    """

    user = create_user(session=session, user_create=user_in)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "uuid": str(user.id),
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        )
    }