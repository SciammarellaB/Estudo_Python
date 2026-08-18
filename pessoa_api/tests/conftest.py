import os
from collections.abc import Generator

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_session
from app.main import app
from app.models.pessoa import Pessoa


def obter_url_banco_testes() -> str:
    env_values = dotenv_values(".env")
    database_url = os.getenv("TEST_DATABASE_URL") or env_values.get("TEST_DATABASE_URL")

    if not database_url:
        pytest.exit("TEST_DATABASE_URL não foi configurada.")

    database_name = make_url(database_url).database
    if database_name != "pessoa_api_test":
        pytest.exit("Os testes de integração exigem a base isolada 'pessoa_api_test'.")

    return database_url


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    engine = create_engine(obter_url_banco_testes(), pool_pre_ping=True)

    if not inspect(engine).has_table("pessoa"):
        engine.dispose()
        pytest.exit("A migration não foi aplicada em pessoa_api_test.")

    yield engine
    engine.dispose()


@pytest.fixture
def limpar_banco(test_engine: Engine) -> Generator[None, None, None]:
    with test_engine.begin() as connection:
        connection.execute(delete(Pessoa))

    yield

    with test_engine.begin() as connection:
        connection.execute(delete(Pessoa))


@pytest.fixture
def client(
    test_engine: Engine,
    limpar_banco: None,
) -> Generator[TestClient, None, None]:
    test_session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_session() -> Generator[Session, None, None]:
        with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
