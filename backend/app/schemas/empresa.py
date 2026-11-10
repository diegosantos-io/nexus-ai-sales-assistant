from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmpresaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=160)
    email: EmailStr
    telefone: str | None = Field(default=None, max_length=30)


class EmpresaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    slug: str
    email: EmailStr
    telefone: str | None
    ativo: bool
    criado_em: datetime
