from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.repositories.pessoa_repository import PessoaRepository
from app.services.pessoa_service import PessoaService

DatabaseSession = Annotated[Session, Depends(get_session)]


def get_pessoa_service(session: DatabaseSession) -> PessoaService:
    repository = PessoaRepository(session)
    return PessoaService(repository, session)


PessoaServiceDependency = Annotated[PessoaService, Depends(get_pessoa_service)]
