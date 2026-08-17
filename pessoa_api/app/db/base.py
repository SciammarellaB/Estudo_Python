from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# O import torna os modelos conhecidos pelo metadata usado pelo Alembic.
from app import models  # noqa: E402, F401
