from datetime import date, timedelta
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def cadastrar_pessoa(
    client: TestClient,
    *,
    nome: str = "Maria da Silva",
    email: str = "maria@example.com",
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/pessoas",
        json={
            "nome": nome,
            "email": email,
            "data_nascimento": "1990-05-20",
        },
    )
    assert response.status_code == 201
    return cast(dict[str, Any], response.json())


def test_criar_e_obter_pessoa(client: TestClient) -> None:
    response = client.post(
        "/api/v1/pessoas",
        json={
            "nome": "  Maria   da Silva  ",
            "email": "MARIA@EXAMPLE.COM",
            "data_nascimento": "1990-05-20",
        },
    )

    assert response.status_code == 201
    pessoa = response.json()
    UUID(pessoa["id"])
    assert pessoa["nome"] == "Maria da Silva"
    assert pessoa["email"] == "maria@example.com"
    assert response.headers["location"].endswith(f"/api/v1/pessoas/{pessoa['id']}")

    get_response = client.get(f"/api/v1/pessoas/{pessoa['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == pessoa


def test_listar_com_paginacao_e_busca(client: TestClient) -> None:
    cadastrar_pessoa(client, nome="Ana Lima", email="ana@example.com")
    cadastrar_pessoa(client, nome="Bruno Souza", email="bruno@example.com")
    cadastrar_pessoa(client, nome="Carla Lima", email="carla@example.com")

    response = client.get(
        "/api/v1/pessoas",
        params={"busca": "lima", "offset": 0, "limit": 1},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 2
    assert result["offset"] == 0
    assert result["limit"] == 1
    assert [item["nome"] for item in result["items"]] == ["Ana Lima"]


def test_put_e_patch(client: TestClient) -> None:
    pessoa = cadastrar_pessoa(client)

    put_response = client.put(
        f"/api/v1/pessoas/{pessoa['id']}",
        json={
            "nome": "Maria Souza",
            "email": "maria.souza@example.com",
            "data_nascimento": "1991-06-21",
        },
    )
    assert put_response.status_code == 200
    assert put_response.json()["email"] == "maria.souza@example.com"

    patch_response = client.patch(
        f"/api/v1/pessoas/{pessoa['id']}",
        json={"nome": "Maria Souza Lima", "data_nascimento": None},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["nome"] == "Maria Souza Lima"
    assert patch_response.json()["email"] == "maria.souza@example.com"
    assert patch_response.json()["data_nascimento"] is None


def test_email_duplicado_retorna_conflito(client: TestClient) -> None:
    cadastrar_pessoa(client)

    response = client.post(
        "/api/v1/pessoas",
        json={"nome": "Outra Maria", "email": "MARIA@example.com"},
    )

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["title"] == "Conflito"


def test_excluir_e_consultar_recurso_inexistente(client: TestClient) -> None:
    pessoa = cadastrar_pessoa(client)

    delete_response = client.delete(f"/api/v1/pessoas/{pessoa['id']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/api/v1/pessoas/{pessoa['id']}")
    assert get_response.status_code == 404
    assert get_response.json()["instance"] == f"/api/v1/pessoas/{pessoa['id']}"


@pytest.mark.parametrize(
    "payload",
    [
        {"nome": "A", "email": "invalido"},
        {
            "nome": "Pessoa Futura",
            "email": "futura@example.com",
            "data_nascimento": (date.today() + timedelta(days=1)).isoformat(),
        },
    ],
)
def test_dados_invalidos_retornam_problem_details(
    client: TestClient,
    payload: dict[str, Any],
) -> None:
    response = client.post("/api/v1/pessoas", json=payload)

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["title"] == "Dados inválidos"
    assert response.json()["errors"]


def test_patch_nao_aceita_null_em_campo_obrigatorio(client: TestClient) -> None:
    pessoa = cadastrar_pessoa(client)

    response = client.patch(f"/api/v1/pessoas/{pessoa['id']}", json={"nome": None})

    assert response.status_code == 422


def test_identificador_inexistente_retorna_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/pessoas/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa não encontrada."


def test_health_verifica_postgresql(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "available"}
