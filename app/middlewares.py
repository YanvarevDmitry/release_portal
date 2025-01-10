from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RoleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_role = request.headers.get("X-User-Role")
        if user_role not in ["Администратор", "Менеджер релиза", "Разработчик"]:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        response = await call_next(request)
        return response

