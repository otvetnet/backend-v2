from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class SchoolBase(SQLModel):
    name: str = Field(index=True)
    city_id: Optional[int] = Field(default=None, foreign_key="city.id", index=True)


class School(SchoolBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Backrefs can be added if needed
