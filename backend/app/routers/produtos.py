
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.produto import (
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
)


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)


def verificar_empresa(usuario: Usuario) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa."
        )

    return usuario.empresa_id


@router.post(
    "/",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_produto(
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    empresa_id = verificar_empresa(usuario)

    produto = Produto(
        empresa_id=empresa_id,
        nome=dados.nome.strip(),
        descricao=dados.descricao.strip() if dados.descricao else None,
        preco=dados.preco,
        estoque=dados.estoque
    )

    db.add(produto)
    db.commit()
    db.refresh(produto)

    return produto


@router.get(
    "/",
    response_model=list[ProdutoResponse]
)
def listar_produtos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    empresa_id = verificar_empresa(usuario)

    consulta = (
        select(Produto)
        .where(Produto.empresa_id == empresa_id)
        .order_by(Produto.criado_em.desc())
    )

    return db.scalars(consulta).all()


@router.get(
    "/{produto_id}",
    response_model=ProdutoResponse
)
def buscar_produto(
    produto_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    empresa_id = verificar_empresa(usuario)

    produto = db.scalar(
        select(Produto).where(
            Produto.id == produto_id,
            Produto.empresa_id == empresa_id
        )
    )

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )

    return produto


@router.patch(
    "/{produto_id}",
    response_model=ProdutoResponse
)
def atualizar_produto(
    produto_id: UUID,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    empresa_id = verificar_empresa(usuario)

    produto = db.scalar(
        select(Produto).where(
            Produto.id == produto_id,
            Produto.empresa_id == empresa_id
        )
    )

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
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

        if campo == "descricao" and valor is not None:
            valor = valor.strip() or None

        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)

    return produto


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def excluir_produto(
    produto_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    empresa_id = verificar_empresa(usuario)

    produto = db.scalar(
        select(Produto).where(
            Produto.id == produto_id,
            Produto.empresa_id == empresa_id
        )
    )

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )

    db.delete(produto)
    db.commit()

    return None
