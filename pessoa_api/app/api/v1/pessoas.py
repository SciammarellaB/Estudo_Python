from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from app.api.dependencies import PessoaServiceDependency
from app.schemas.error import ProblemDetails
from app.schemas.pessoa import (
    PessoaCreate,
    PessoaListResponse,
    PessoaReplace,
    PessoaResponse,
    PessoaUpdate,
)

router = APIRouter(prefix="/pessoas", tags=["pessoas"])

error_responses: dict[int | str, dict[str, Any]] = {
    int(HTTPStatus.NOT_FOUND): {
        "model": ProblemDetails,
        "description": "Pessoa não encontrada",
    },
    int(HTTPStatus.CONFLICT): {
        "model": ProblemDetails,
        "description": "E-mail já cadastrado",
    },
    int(HTTPStatus.UNPROCESSABLE_ENTITY): {
        "model": ProblemDetails,
        "description": "Dados inválidos",
    },
}


@router.post(
    "",
    response_model=PessoaResponse,
    status_code=HTTPStatus.CREATED,
    responses=error_responses,
    summary="Cadastra uma pessoa",
)
def criar_pessoa(
    entrada: PessoaCreate,
    request: Request,
    response: Response,
    service: PessoaServiceDependency,
) -> PessoaResponse:
    pessoa = service.criar(entrada)
    response.headers["Location"] = str(request.url_for("obter_pessoa", pessoa_id=pessoa.id))
    return PessoaResponse.model_validate(pessoa)


@router.get(
    "",
    response_model=PessoaListResponse,
    summary="Lista pessoas com paginação por offset",
)
def listar_pessoas(
    service: PessoaServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    busca: Annotated[str | None, Query(min_length=1, max_length=120)] = None,
) -> PessoaListResponse:
    pessoas, total = service.listar(offset=offset, limit=limit, busca=busca)
    return PessoaListResponse(
        items=[PessoaResponse.model_validate(pessoa) for pessoa in pessoas],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{pessoa_id}",
    response_model=PessoaResponse,
    responses=error_responses,
    name="obter_pessoa",
    summary="Obtém uma pessoa pelo identificador",
)
def obter_pessoa(pessoa_id: UUID, service: PessoaServiceDependency) -> PessoaResponse:
    return PessoaResponse.model_validate(service.obter(pessoa_id))


@router.put(
    "/{pessoa_id}",
    response_model=PessoaResponse,
    responses=error_responses,
    summary="Substitui os dados editáveis de uma pessoa",
)
def substituir_pessoa(
    pessoa_id: UUID,
    entrada: PessoaReplace,
    service: PessoaServiceDependency,
) -> PessoaResponse:
    return PessoaResponse.model_validate(service.substituir(pessoa_id, entrada))


@router.patch(
    "/{pessoa_id}",
    response_model=PessoaResponse,
    responses=error_responses,
    summary="Atualiza parcialmente uma pessoa",
)
def atualizar_pessoa(
    pessoa_id: UUID,
    entrada: PessoaUpdate,
    service: PessoaServiceDependency,
) -> PessoaResponse:
    return PessoaResponse.model_validate(service.atualizar(pessoa_id, entrada))


@router.delete(
    "/{pessoa_id}",
    status_code=HTTPStatus.NO_CONTENT,
    responses=error_responses,
    summary="Remove uma pessoa",
)
def remover_pessoa(pessoa_id: UUID, service: PessoaServiceDependency) -> Response:
    service.remover(pessoa_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)
