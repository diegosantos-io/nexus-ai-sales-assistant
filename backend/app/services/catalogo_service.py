from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produto import Produto


def obter_catalogo_empresa(
    empresa_id: UUID,
    db: Session,
    limite: int = 50
) -> list[dict[str, str | int]]:

    consulta = (
        select(Produto)
        .where(
            Produto.empresa_id == empresa_id,
            Produto.ativo.is_(True)
        )
        .order_by(Produto.nome.asc())
        .limit(limite)
    )

    produtos = db.scalars(consulta).all()

    return [
        {
            "nome": produto.nome,
            "descricao": produto.descricao or "Sem descrição cadastrada.",
            "preco": str(produto.preco),
            "estoque": produto.estoque
        }
        for produto in produtos
    ]
