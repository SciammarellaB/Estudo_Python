from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_session

router = APIRouter(tags=["health"])
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.get(
    "/health",
    response_model=None,
    summary="Verifica aplicação e banco de dados",
)
def health(session: DatabaseSession) -> dict[str, str] | JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "unavailable"},
        )

    return {"status": "healthy", "database": "available"}
