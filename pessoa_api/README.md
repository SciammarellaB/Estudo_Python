# Pessoa API

API REST didática para estudar a construção de um backend Python sem esconder as
responsabilidades de cada camada. O projeto usa FastAPI, Pydantic, SQLAlchemy 2,
Alembic e PostgreSQL.

## Arquitetura

O projeto mantém uma arquitetura em camadas dentro de um único pacote Python:

```text
Requisição HTTP
    -> Router FastAPI
    -> Schema Pydantic
    -> PessoaService
    -> PessoaRepository
    -> SQLAlchemy Session
    -> PostgreSQL
```

| ASP.NET Core | Pessoa API |
|---|---|
| `Program.cs` | `app/main.py` |
| Controller | `app/api/v1` |
| DTO/Request/Response model | `app/schemas` |
| Service | `app/services` |
| Repository | `app/repositories` |
| Entity do EF Core | `app/models` |
| `DbContext` scoped | SQLAlchemy `Session` por requisição |
| EF Migrations | Alembic |
| `appsettings.json` e `IOptions` | `.env` e Pydantic Settings |
| xUnit | pytest |

O modelo SQLAlchemy é a entidade persistida. Os schemas Pydantic são contratos
HTTP independentes para criação, substituição, atualização parcial e resposta.

## Requisitos

- Python 3.12 ou superior;
- `uv` instalado;
- PostgreSQL acessível localmente.

## Configuração

Crie o ambiente local a partir do exemplo e altere somente os valores locais:

```bash
cp .env.example .env
uv sync --dev
```

O arquivo `.env` é ignorado pelo Git. Nunca versione credenciais reais.
`DATABASE_URL` é obrigatória; a aplicação não possui uma conexão padrão de
fallback.

Crie duas bases PostgreSQL independentes:

```text
pessoa_api
pessoa_api_test
```

A aplicação lê `DATABASE_URL`. Os testes de integração leem
`TEST_DATABASE_URL` e nunca utilizam automaticamente a base da aplicação.

## Migrations

Aplicar todas as migrations:

```bash
uv run alembic upgrade head
```

Aplicar as mesmas migrations na base exclusiva de testes:

```bash
set -a
source .env
set +a
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic upgrade head
```

Gerar uma nova migration candidata:

```bash
uv run alembic revision --autogenerate -m "descricao da alteracao"
```

Toda migration gerada automaticamente deve ser revisada antes de ser aplicada.

## Execução

```bash
uv run uvicorn app.main:app --reload
```

Recursos locais:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Endpoints

```text
POST   /api/v1/pessoas
GET    /api/v1/pessoas
GET    /api/v1/pessoas/{id}
PUT    /api/v1/pessoas/{id}
PATCH  /api/v1/pessoas/{id}
DELETE /api/v1/pessoas/{id}
```

Exemplo de criação:

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/pessoas \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "Maria da Silva",
    "email": "maria@example.com",
    "data_nascimento": "1990-05-20"
  }'
```

Listagem paginada e filtrada:

```bash
curl 'http://127.0.0.1:8000/api/v1/pessoas?offset=0&limit=20&busca=maria'
```

## Respostas e erros

- `201 Created`: pessoa criada, com header `Location`;
- `200 OK`: consulta ou atualização concluída;
- `204 No Content`: exclusão concluída;
- `404 Not Found`: pessoa inexistente;
- `409 Conflict`: e-mail já cadastrado;
- `422 Unprocessable Content`: contrato inválido.

Erros seguem um formato inspirado em Problem Details:

```json
{
  "type": "about:blank",
  "title": "Recurso não encontrado",
  "status": 404,
  "detail": "Pessoa não encontrada.",
  "instance": "/api/v1/pessoas/00000000-0000-0000-0000-000000000000"
}
```

## Qualidade e testes

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy app tests
uv run pytest
uv run pytest --cov=app --cov-report=term-missing
```

Os testes unitários não acessam infraestrutura. Os testes marcados como
`integration` utilizam exclusivamente `TEST_DATABASE_URL`.

## Decisões didáticas

- A `Session` é síncrona e cada endpoint é uma função `def`. O FastAPI executa
  esse trabalho em seu pool de threads. Uma futura versão poderá comparar esse
  fluxo com `AsyncSession`, sem misturar os dois modelos agora.
- O service controla `commit` e `rollback`; o repository não encerra a
  transação silenciosamente.
- A consulta preventiva de e-mail produz uma mensagem amigável, mas a
  constraint única do PostgreSQL continua sendo a garantia contra concorrência.
- Apenas a constraint `uq_pessoa_email` é traduzida para `409 Conflict`. Outros
  erros de integridade continuam visíveis como falhas inesperadas para não serem
  diagnosticados incorretamente.
- Não há generic repository: consultas permanecem explícitas e tipadas.
- Não há uma segunda entidade de domínio sem comportamento. O modelo SQLAlchemy
  é a entidade persistida, enquanto Pydantic representa os contratos HTTP.

## Container local criado para este estudo

No ambiente em que o projeto foi montado, o PostgreSQL está no container
`pessoa-api-postgres`. O Docker escolheu uma porta livre e a URL correspondente
foi gravada somente no `.env` local.

```bash
docker start pessoa-api-postgres
docker stop pessoa-api-postgres
docker port pessoa-api-postgres 5432/tcp
```

O volume `pessoa_api_postgres_data` preserva as duas bases quando o container é
parado.
