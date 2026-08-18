from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Pessoa(Base):
    """Entidade persistida; equivale a uma entity mapeada pelo EF Core."""

    __tablename__ = "pessoa"
    __table_args__ = (UniqueConstraint("email", name="uq_pessoa_email"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
