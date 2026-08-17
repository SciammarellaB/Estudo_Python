from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EmailJaCadastradoError, PessoaNaoEncontradaError
from app.models.pessoa import Pessoa
from app.repositories.pessoa_repository import PessoaRepository
from app.schemas.pessoa import PessoaCreate, PessoaReplace, PessoaUpdate


class PessoaService:
    """Executa casos de uso e controla a fronteira transacional."""

    def __init__(self, repository: PessoaRepository, session: Session) -> None:
        self._repository = repository
        self._session = session

    def criar(self, entrada: PessoaCreate) -> Pessoa:
        if self._repository.obter_por_email(str(entrada.email)) is not None:
            raise EmailJaCadastradoError

        pessoa = Pessoa(**entrada.model_dump())
        self._repository.adicionar(pessoa)
        self._commit_traduzindo_conflito()
        self._session.refresh(pessoa)
        return pessoa

    def obter(self, pessoa_id: UUID) -> Pessoa:
        pessoa = self._repository.obter(pessoa_id)
        if pessoa is None:
            raise PessoaNaoEncontradaError
        return pessoa

    def listar(
        self,
        *,
        offset: int,
        limit: int,
        busca: str | None,
    ) -> tuple[list[Pessoa], int]:
        return self._repository.listar(offset=offset, limit=limit, busca=busca)

    def substituir(self, pessoa_id: UUID, entrada: PessoaReplace) -> Pessoa:
        pessoa = self.obter(pessoa_id)
        self._validar_email_disponivel(str(entrada.email), pessoa_id)

        for field_name, value in entrada.model_dump().items():
            setattr(pessoa, field_name, value)

        self._commit_traduzindo_conflito()
        self._session.refresh(pessoa)
        return pessoa

    def atualizar(self, pessoa_id: UUID, entrada: PessoaUpdate) -> Pessoa:
        pessoa = self.obter(pessoa_id)
        changes = entrada.model_dump(exclude_unset=True)

        if "email" in changes:
            self._validar_email_disponivel(str(changes["email"]), pessoa_id)

        for field_name, value in changes.items():
            setattr(pessoa, field_name, value)

        self._commit_traduzindo_conflito()
        self._session.refresh(pessoa)
        return pessoa

    def remover(self, pessoa_id: UUID) -> None:
        pessoa = self.obter(pessoa_id)
        self._repository.remover(pessoa)
        self._commit_traduzindo_conflito()

    def _validar_email_disponivel(self, email: str, pessoa_id: UUID) -> None:
        pessoa_com_email = self._repository.obter_por_email(email)
        if pessoa_com_email is not None and pessoa_com_email.id != pessoa_id:
            raise EmailJaCadastradoError

    def _commit_traduzindo_conflito(self) -> None:
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            if self._constraint_name(error) == "uq_pessoa_email":
                raise EmailJaCadastradoError from error
            raise

    @staticmethod
    def _constraint_name(error: IntegrityError) -> str | None:
        diagnostic = getattr(error.orig, "diag", None)
        return getattr(diagnostic, "constraint_name", None)
