from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.models.conversa import Conversa
from app.models.mensagem import Mensagem
from app.models.usuario import Usuario
from app.schemas.mensagem import MensagemCreate, MensagemResponse


router = APIRouter(
    prefix="/conversas/{conversa_id}/mensagens",
    tags=["Mensagens"]
)


def obter_conversa_da_empresa(
    conversa_id: UUID,
    usuario: Usuario,
    db: Session
) -> Conversa:
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


@router.post(
    "/",
    response_model=MensagemResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_mensagem(
    conversa_id: UUID,
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    conversa = obter_conversa_da_empresa(
        conversa_id, usuario, db
    )

    if conversa.status != "aberta":
        raise HTTPException(
            status_code=409,
            detail="Não é possível enviar mensagens em uma conversa encerrada."
        )

    mensagem = Mensagem(
        conversa_id=conversa.id,
        remetente=dados.remetente,
        conteudo=dados.conteudo.strip()
    )

    if not mensagem.conteudo:
        raise HTTPException(
            status_code=422,
            detail="O conteúdo da mensagem não pode estar vazio."
        )

    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)

    return mensagem


@router.get(
    "/",
    response_model=list[MensagemResponse]
)
def listar_mensagens(
    conversa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    conversa = obter_conversa_da_empresa(
        conversa_id, usuario, db
    )

    consulta = (
        select(Mensagem)
        .where(Mensagem.conversa_id == conversa.id)
        .order_by(Mensagem.criada_em.asc())
    )

    return db.scalars(consulta).all()
