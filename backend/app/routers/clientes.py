from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate
)


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_cliente(
    dados: ClienteCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    cliente = Cliente(
        empresa_id=usuario.empresa_id,
        nome=dados.nome.strip(),
        email=str(dados.email).lower() if dados.email else None,
        telefone=dados.telefone
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


@router.get(
    "/",
    response_model=list[ClienteResponse]
)
def listar_clientes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    consulta = select(Cliente).where(
        Cliente.empresa_id == usuario.empresa_id
    ).order_by(Cliente.criado_em.desc())

    return db.scalars(consulta).all()


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse
)
def buscar_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    consulta = select(Cliente).where(
        Cliente.id == cliente_id,
        Cliente.empresa_id == usuario.empresa_id
    )

    cliente = db.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    return cliente



@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse
)
def atualizar_cliente(
    cliente_id: UUID,
    dados: ClienteUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    cliente = db.scalar(
        select(Cliente).where(
            Cliente.id == cliente_id,
            Cliente.empresa_id == usuario.empresa_id
        )
    )

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    alteracoes = dados.model_dump(exclude_unset=True)

    if not alteracoes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe pelo menos um campo para atualizar."
        )

    for campo, valor in alteracoes.items():
        if campo == "nome" and valor is not None:
            valor = valor.strip()

        if campo == "email" and valor is not None:
            valor = str(valor).lower()

        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)

    return cliente


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def excluir_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    cliente = db.scalar(
        select(Cliente).where(
            Cliente.id == cliente_id,
            Cliente.empresa_id == usuario.empresa_id
        )
    )

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    db.delete(cliente)
    db.commit()

    return None
