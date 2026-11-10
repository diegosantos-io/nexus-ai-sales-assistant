from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    descricao: str | None = None
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    estoque: int = Field(default=0, ge=0)


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    descricao: str | None = None
    preco: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2
    )
    estoque: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nome: str
    descricao: str | None
    preco: Decimal
    estoque: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
