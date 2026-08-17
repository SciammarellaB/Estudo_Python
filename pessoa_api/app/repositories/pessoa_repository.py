from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.pessoa import Pessoa


class PessoaRepository:
    """Concentra consultas e operações de persistência de Pessoa."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def adicionar(self, pessoa: Pessoa) -> None:
        self._session.add(pessoa)

    def obter(self, pessoa_id: UUID) -> Pessoa | None:
        return self._session.get(Pessoa, pessoa_id)

    def obter_por_email(self, email: str) -> Pessoa | None:
        statement = select(Pessoa).where(Pessoa.email == email)
        return self._session.scalar(statement)

    def listar(
        self,
        *,
        offset: int,
        limit: int,
        busca: str | None,
    ) -> tuple[list[Pessoa], int]:
        filters = []
        if busca:
            pattern = f"%{busca.strip()}%"
            filters.append(or_(Pessoa.nome.ilike(pattern), Pessoa.email.ilike(pattern)))

        count_statement = select(func.count()).select_from(Pessoa).where(*filters)
        total = self._session.scalar(count_statement) or 0

        statement = (
            select(Pessoa)
            .where(*filters)
            .order_by(Pessoa.nome, Pessoa.id)
            .offset(offset)
            .limit(limit)
        )
        pessoas = list(self._session.scalars(statement).all())
        return pessoas, total

    def remover(self, pessoa: Pessoa) -> None:
        self._session.delete(pessoa)
