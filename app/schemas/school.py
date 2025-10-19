from typing import Optional
from sqlmodel import SQLModel


class SchoolPublic(SQLModel):
    id: Optional[int]
    name: str
    city_id: Optional[int]
