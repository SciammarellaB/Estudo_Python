from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def normalizar_nome(value: str) -> str:
    return " ".join(value.split())


def validar_data_nascimento(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("A data de nascimento não pode estar no futuro.")
    return value


class PessoaBase(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: EmailStr
    data_nascimento: date | None = None

    @field_validator("nome")
    @classmethod
    def normaliza_nome(cls, value: str) -> str:
        return normalizar_nome(value)

    @field_validator("email")
    @classmethod
    def normaliza_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_nao_pode_estar_no_futuro(cls, value: date | None) -> date | None:
        return validar_data_nascimento(value)


class PessoaCreate(PessoaBase):
    pass


class PessoaReplace(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    email: EmailStr | None = None
    data_nascimento: date | None = None

    @field_validator("nome")
    @classmethod
    def normaliza_nome(cls, value: str | None) -> str | None:
        return normalizar_nome(value) if value is not None else None

    @field_validator("email")
    @classmethod
    def normaliza_email(cls, value: EmailStr | None) -> str | None:
        return str(value).strip().lower() if value is not None else None

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_nao_pode_estar_no_futuro(cls, value: date | None) -> date | None:
        return validar_data_nascimento(value)

    @model_validator(mode="after")
    def campos_obrigatorios_nao_aceitam_null(self) -> "PessoaUpdate":
        for field_name in ("nome", "email"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"O campo '{field_name}' não aceita null.")
        return self


class PessoaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    email: EmailStr
    data_nascimento: date | None
    criado_em: datetime
    atualizado_em: datetime


class PessoaListResponse(BaseModel):
    items: list[PessoaResponse]
    total: int
    offset: int
    limit: int
