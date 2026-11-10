import uuid

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Mensagem(Base):
    __tablename__ = "mensagens"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    conversa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    remetente: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    conteudo: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
