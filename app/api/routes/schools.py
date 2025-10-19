from typing import Any, List

from fastapi import APIRouter, Query
from sqlmodel import select, func

from app.api.deps import SessionDep
from app.models.school import School
from app.schemas.school import SchoolPublic

router = APIRouter(
    prefix="/schools",
    tags=["schools"]
)


@router.get("/", response_model=List[SchoolPublic])
def get_schools(session: SessionDep, skip: int = 0, limit: int = 100, query: str = Query(default=None), city_id: int = Query(default=None)) -> Any:
    """
    Get schools. Supports optional text query and optional city_id to filter by city.
    """

    statement = select(School)

    if query:
        statement = statement.where(
            func.lower(School.name).contains(query.lower())
        )

    if city_id is not None:
        statement = statement.where(School.city_id == city_id)

    statement = statement.offset(skip).limit(limit)
    schools = session.exec(statement).all()

    return schools
