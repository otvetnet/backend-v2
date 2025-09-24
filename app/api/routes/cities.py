from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import SessionDep
from sqlmodel import select, func

from app.models.city import CityBase, City
from app.schemas.city import CitiesPublic

router = APIRouter(
    prefix="/cities",
    tags=["cities"]
)

@router.get("/", response_model=CitiesPublic)
def get_cities(session: SessionDep, skip: int = 0, limit: int = 100, query: str = Query(default=None)) -> Any:
    """
    Get all cities
    """

    statement = select(City)

    if query:
        statement = statement.where(
            func.lower(City.name).contains(
                query.lower()
            )
        )

    statement = statement.offset(skip).limit(limit)
    cities = session.exec(statement).all()

    return CitiesPublic(cities=cities)