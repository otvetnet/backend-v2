import uuid

from sqlmodel import SQLModel, Field
from pydantic import constr

from app.models.user import UserBase


class UserCreate(UserBase):
    password: constr(min_length=8, max_length=64)
    city_id: int


class UserPublic(SQLModel):
    id: uuid.UUID
    access_token: str


# class UserRegister(SQLModel):
#     first_name: str = Field(max_length=50)
#     middle_name: str = Field(default=None, max_length=50)
#     last_name: str = Field(max_length=50)
#     age: int = Field(ge=6, le=18)
#     city_id: int