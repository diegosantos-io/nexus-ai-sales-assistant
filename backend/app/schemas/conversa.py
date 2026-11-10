from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversaCreate(BaseModel):
    cliente_id: UUID
    canal: Literal["site", "whatsapp"]


class ConversaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    cliente_id: UUID
    canal: str
    status: str
    criada_em: datetime
    encerrada_em: datetime | None
