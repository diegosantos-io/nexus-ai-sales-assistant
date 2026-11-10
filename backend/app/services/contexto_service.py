from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mensagem import Mensagem


def obter_historico_conversa(
    conversa_id: UUID,
    db: Session,
    limite: int = 20
) -> list[dict[str, str]]:
    consulta = (
        select(Mensagem)
        .where(Mensagem.conversa_id == conversa_id)
        .order_by(Mensagem.criada_em.desc())
        .limit(limite)
    )

    mensagens = db.scalars(consulta).all()

    mensagens_em_ordem = reversed(mensagens)

    return [
        {
            "role": (
                "assistant"
                if mensagem.remetente == "assistant"
                else "user"
            ),
            "content": mensagem.conteudo
        }
        for mensagem in mensagens_em_ordem
        if mensagem.remetente in ("user", "assistant")
    ]
