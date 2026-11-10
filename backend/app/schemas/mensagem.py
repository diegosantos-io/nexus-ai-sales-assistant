from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MensagemCreate(BaseModel):
    remetente: Literal["user"]
    conteudo: str = Field(min_length=1)


class MensagemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversa_id: UUID
    remetente: str
    conteudo: str
    criada_em: datetime
