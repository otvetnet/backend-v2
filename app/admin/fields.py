
from typing import Any

from starlette_admin import StringField
from starlette.requests import Request

from datetime import datetime, date

from app.models.city import City
from app.models.user import User


class DateField(StringField):
    """Field that formats a datetime-like attribute as date-only.

    Returns a native `datetime.date` when possible (preferred for Excel/xlsx
    exporters that write date cells). Falls back to an ISO date string.

    Usage:
        DateField(name="finished_at", label="Дата прохождения")
    """

    async def parse_obj(self, request: Request, obj) -> Any:
        # obj is the model instance; self.name is provided by the base class
        field_name = getattr(self, "name", None)
        val = getattr(obj, field_name, None)
        if val is None:
            return None

        # If it's a datetime or date-like object, return date()
        if isinstance(val, date) and not isinstance(val, datetime):
            return val
        if isinstance(val, datetime):
            return val.date()

        # If it's a string, try to parse ISO-like date or datetime
        s = str(val)
        if not s:
            return None
        # if contains whitespace (likely datetime string) take first part
        if " " in s:
            s = s.split(" ")[0]

        try:
            parsed = datetime.fromisoformat(s)
            return parsed.date()
        except Exception:
            # last-resort: return the raw date-like string (YYYY-MM-DD) so CSV consumers can parse it
            return s


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