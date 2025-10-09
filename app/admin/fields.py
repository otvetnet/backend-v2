from typing import Any

from starlette_admin import StringField
from starlette.requests import Request

from app.models.city import City
from app.models.user import User


class UserFullNameField(StringField):
    name = "user_full_name"
    label = "Имя"

    async def parse_obj(self, request: Request, obj: User) -> Any:
        if obj.user:
            return f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"
        return None


class CityNameField(StringField):
    name = "city_name"
    label = "Город"

    async def parse_obj(self, request: Request, obj: City) -> Any:
        if obj.city:
            return obj.city.name
        return None