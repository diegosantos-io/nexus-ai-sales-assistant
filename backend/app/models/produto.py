import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    preco: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estoque: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
