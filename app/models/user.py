import uuid
from typing import List, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.city import City
from app.models.survey import SurveyResponse

if TYPE_CHECKING:
    from app.models.game import GameResult


# Base model (common attributes)
class UserBase(SQLModel):
    first_name: str = Field(default=None, max_length=50)
    middle_name: str = Field(default=None, max_length=50)
    last_name: str = Field(default=None, max_length=50)
    school: str = Field(default=None, max_length=128)
    age: int = Field(ge=6, le=18)


# Database model
class User(UserBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    hashed_password: str
    city_id: int = Field(foreign_key="city.id")
    city: City = Relationship(back_populates="users")
    responses: List["SurveyResponse"] = Relationship(back_populates="user")
    # game results relationship
    results: List["GameResult"] = Relationship(back_populates="user")