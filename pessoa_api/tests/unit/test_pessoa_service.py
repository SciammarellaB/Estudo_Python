from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, create_autospec
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EmailJaCadastradoError, PessoaNaoEncontradaError
from app.models.pessoa import Pessoa
from app.repositories.pessoa_repository import PessoaRepository
from app.schemas.pessoa import PessoaCreate, PessoaUpdate
from app.services.pessoa_service import PessoaService


def criar_service() -> tuple[PessoaService, MagicMock, MagicMock]:
    repository: MagicMock = create_autospec(PessoaRepository, instance=True)
    session: MagicMock = create_autospec(Session, instance=True)
    return PessoaService(repository, session), repository, session


def test_criar_normaliza_dados_e_confirma_transacao() -> None:
    service, repository, session = criar_service()
    repository.obter_por_email.return_value = None
    entrada = PessoaCreate(
        nome="  Maria   da Silva ",
        email="MARIA@EXAMPLE.COM",
        data_nascimento=date(1990, 5, 20),
    )

    pessoa = service.criar(entrada)

    assert pessoa.nome == "Maria da Silva"
    assert pessoa.email == "maria@example.com"
    repository.adicionar.assert_called_once_with(pessoa)
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(pessoa)


def test_criar_rejeita_email_duplicado_sem_iniciar_escrita() -> None:
    service, repository, session = criar_service()
    repository.obter_por_email.return_value = Pessoa(
        id=uuid4(),
        nome="Existente",
        email="maria@example.com",
    )
    entrada = PessoaCreate(nome="Maria Silva", email="maria@example.com")

    with pytest.raises(EmailJaCadastradoError):
        service.criar(entrada)

    repository.adicionar.assert_not_called()
    session.commit.assert_not_called()


def test_obter_rejeita_identificador_inexistente() -> None:
    service, repository, _ = criar_service()
    repository.obter.return_value = None

    with pytest.raises(PessoaNaoEncontradaError):
        service.obter(uuid4())


def test_atualizar_modifica_apenas_campos_enviados() -> None:
    service, repository, session = criar_service()
    pessoa_id = uuid4()
    pessoa = Pessoa(
        id=pessoa_id,
        nome="Maria Silva",
        email="maria@example.com",
        data_nascimento=date(1990, 5, 20),
    )
    repository.obter.return_value = pessoa

    resultado = service.atualizar(pessoa_id, PessoaUpdate(nome="Maria Souza"))

    assert resultado.nome == "Maria Souza"
    assert resultado.email == "maria@example.com"
    assert resultado.data_nascimento == date(1990, 5, 20)
    repository.obter_por_email.assert_not_called()
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(pessoa)


def test_constraint_unica_de_email_e_traduzida_para_conflito() -> None:
    service, repository, session = criar_service()
    repository.obter_por_email.return_value = None
    original_error = Exception("unique violation")
    original_error.diag = SimpleNamespace(constraint_name="uq_pessoa_email")  # type: ignore[attr-defined]
    session.commit.side_effect = IntegrityError("insert", {}, original_error)

    with pytest.raises(EmailJaCadastradoError):
        service.criar(PessoaCreate(nome="Maria Silva", email="maria@example.com"))

    session.rollback.assert_called_once_with()


def test_erro_de_integridade_desconhecido_nao_e_mascarado() -> None:
    service, repository, session = criar_service()
    repository.obter_por_email.return_value = None
    integrity_error = IntegrityError("insert", {}, Exception("outra constraint"))
    session.commit.side_effect = integrity_error

    with pytest.raises(IntegrityError) as captured:
        service.criar(PessoaCreate(nome="Maria Silva", email="maria@example.com"))

    assert captured.value is integrity_error
    session.rollback.assert_called_once_with()
