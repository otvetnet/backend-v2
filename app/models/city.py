from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class CityBase(SQLModel):
    name: str = Field(index=True)


class City(CityBase, table=True):
    id: int = Field(default=None, primary_key=True)
    users: List["User"] = Relationship(back_populates="city")