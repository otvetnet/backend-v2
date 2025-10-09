from typing import List

from app.models.city import CityBase
from sqlmodel import SQLModel


class CityPublic(CityBase):
    id: int


class CitiesPublic(SQLModel):
    cities: List[CityPublic]