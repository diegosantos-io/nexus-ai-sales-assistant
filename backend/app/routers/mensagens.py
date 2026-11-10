from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.integrations.ai.sales_assistant import gerar_resposta
from app.models.conversa import Conversa
from app.models.mensagem import Mensagem
from app.models.usuario import Usuario
from app.schemas.mensagem import MensagemCreate, MensagemResponse
from app.services.contexto_service import obter_historico_conversa


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
    response_model=list[MensagemResponse],
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

    mensagem_usuario = Mensagem(
        conversa_id=conversa.id,
        remetente="user",
        conteudo=dados.conteudo.strip()
    )

    if not mensagem_usuario.conteudo:
        raise HTTPException(
            status_code=422,
            detail="O conteúdo da mensagem não pode estar vazio."
        )

    db.add(mensagem_usuario)
    db.commit()
    db.refresh(mensagem_usuario)

    historico = obter_historico_conversa(
        conversa_id=conversa.id,
        db=db
    )

    instrucoes = {
        "role": "system",
        "content": (
            "Você é o Nexus, um assistente virtual especializado em vendas. "
            "Responda em português brasileiro, com clareza, educação e objetividade. "
            "Entenda as necessidades do cliente, faça perguntas quando necessário "
            "e ajude-o a encontrar produtos ou serviços adequados. "
            "Não invente preços, disponibilidade ou características de produtos. "
            "Quando não souber uma informação, seja transparente."
        )
    }

    try:
        resposta_ia = gerar_resposta(
            [instrucoes, *historico]
        )
    except (RuntimeError, ValueError):
        raise HTTPException(
            status_code=503,
            detail=(
                "Não foi possível gerar uma resposta no momento. "
                "Sua mensagem foi salva. Tente novamente mais tarde."
            )
        )

    mensagem_assistente = Mensagem(
        conversa_id=conversa.id,
        remetente="assistant",
        conteudo=resposta_ia
    )

    db.add(mensagem_assistente)
    db.commit()
    db.refresh(mensagem_assistente)

    return [mensagem_usuario, mensagem_assistente]


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
