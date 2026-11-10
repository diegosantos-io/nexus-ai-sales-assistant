import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Conversa(Base):
    __tablename__ = "conversas"

    __table_args__ = (
        ForeignKeyConstraint(
            ["empresa_id", "cliente_id"],
            ["clientes.empresa_id", "clientes.id"],
            ondelete="CASCADE",
            name="fk_conversas_cliente_empresa",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    cliente_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True
    )

    canal: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="aberta",
        nullable=False
    )

    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    encerrada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
