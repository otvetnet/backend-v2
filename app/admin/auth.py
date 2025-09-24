from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider


class AdminAuth(AuthProvider):
    async def login(
            self, username: str, password: str,
            remember_me: bool, request: Request,
            response: Response
    ) -> Response:
        if username == "admin" and password == "pass":
            request.session.update({"user": username})
            return response
        return response

    async def is_authenticated(self, request: Request) -> Response:
        return request.session.get("user") is not None

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.session.get("user", "")
        return AdminUser(username=user)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response