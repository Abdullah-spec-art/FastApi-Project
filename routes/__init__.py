from fastapi import APIRouter

from routes import user
from routes import todo


router=APIRouter()

router.include_router(user.router,tags=["User"])
router.include_router(todo.router,tags=["Todos"])

__all__ = ["router"]


