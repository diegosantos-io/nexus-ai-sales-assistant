from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nome: str
    email: EmailStr | None
    telefone: str | None
    criado_em: datetime


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
