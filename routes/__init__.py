from fastapi import APIRouter

from routes import route_user
from routes import route_todo


router=APIRouter()

router.include_router(route_user.router, prefix="/user",tags=["User"])
router.include_router(route_todo.router, prefix="/todos",tags=["Todos"])

__all__ = ["router"]


