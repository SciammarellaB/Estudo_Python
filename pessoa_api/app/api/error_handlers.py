import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import EmailJaCadastradoError, PessoaNaoEncontradaError
from app.schemas.error import ProblemDetails

logger = logging.getLogger(__name__)


def problem_response(
    request: Request,
    *,
    status_code: int,
    title: str,
    detail: str,
    errors: list[dict[str, object]] | None = None,
) -> JSONResponse:
    problem = ProblemDetails(
        title=title,
        status=status_code,
        detail=detail,
        instance=request.url.path,
        errors=errors,
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(problem.model_dump(exclude_none=True)),
        media_type="application/problem+json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PessoaNaoEncontradaError)
    async def pessoa_nao_encontrada_handler(
        request: Request,
        error: PessoaNaoEncontradaError,
    ) -> JSONResponse:
        return problem_response(
            request,
            status_code=HTTPStatus.NOT_FOUND,
            title="Recurso não encontrado",
            detail=str(error),
        )

    @app.exception_handler(EmailJaCadastradoError)
    async def email_ja_cadastrado_handler(
        request: Request,
        error: EmailJaCadastradoError,
    ) -> JSONResponse:
        return problem_response(
            request,
            status_code=HTTPStatus.CONFLICT,
            title="Conflito",
            detail=str(error),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        return problem_response(
            request,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            title="Dados inválidos",
            detail="A requisição contém dados inválidos.",
            errors=jsonable_encoder(error.errors()),
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Erro não tratado em %s", request.url.path, exc_info=error)
        return problem_response(
            request,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            title="Erro interno",
            detail="Ocorreu um erro interno inesperado.",
        )
