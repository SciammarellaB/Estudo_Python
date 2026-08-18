from fastapi import APIRouter

from app.api.v1.pessoas import router as pessoas_router

router = APIRouter(prefix="/api/v1")
router.include_router(pessoas_router)
