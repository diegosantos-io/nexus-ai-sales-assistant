from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from datetime import datetime, timezone
from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.models.cliente import Cliente
from app.models.conversa import Conversa
from app.models.usuario import Usuario
from app.schemas.conversa import ConversaCreate, ConversaResponse


router = APIRouter(prefix="/conversas", tags=["Conversas"])


@router.post(
    "/",
    response_model=ConversaResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_conversa(
    dados: ConversaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está vinculado a uma empresa."
        )

    cliente = db.scalar(
        select(Cliente).where(
            Cliente.id == dados.cliente_id,
            Cliente.empresa_id == usuario.empresa_id
        )
    )

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )

    conversa = Conversa(
        empresa_id=usuario.empresa_id,
        cliente_id=cliente.id,
        canal=dados.canal,
        status="aberta"
    )

    db.add(conversa)
    db.commit()
    db.refresh(conversa)

    return conversa


@router.get(
    "/",
    response_model=list[ConversaResponse]
)
def listar_conversas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está vinculado a uma empresa."
        )

    consulta = (
        select(Conversa)
        .where(Conversa.empresa_id == usuario.empresa_id)
        .order_by(Conversa.criada_em.desc())
    )

    return db.scalars(consulta).all()


@router.get(
    "/{conversa_id}",
    response_model=ConversaResponse
)
def buscar_conversa(
    conversa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está vinculado a uma empresa."
        )

    conversa = db.scalar(
        select(Conversa).where(
            Conversa.id == conversa_id,
            Conversa.empresa_id == usuario.empresa_id
        )
    )

    if conversa is None:
        raise HTTPException(
            status_code=404,
            detail="Conversa não encontrada."
        )

    return conversa


@router.patch(
    "/{conversa_id}/encerrar",
    response_model=ConversaResponse
)
def encerrar_conversa(
    conversa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está vinculado a uma empresa."
        )

    conversa = db.scalar(
        select(Conversa).where(
            Conversa.id == conversa_id,
            Conversa.empresa_id == usuario.empresa_id
        )
    )

    if conversa is None:
        raise HTTPException(
            status_code=404,
            detail="Conversa não encontrada."
        )

    if conversa.status == "encerrada":
        raise HTTPException(
            status_code=409,
            detail="Esta conversa já está encerrada."
        )

    conversa.status = "encerrada"
    conversa.encerrada_em = datetime.now(timezone.utc)

    db.commit()
    db.refresh(conversa)

    return conversa
