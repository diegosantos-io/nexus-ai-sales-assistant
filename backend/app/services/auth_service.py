from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    create_access_token
)
from app.models.usuario import Usuario


def autenticar_usuario(
    db: Session,
    email: str,
    senha: str
) -> str | None:

    usuario = db.scalar(
        select(Usuario).where(
            Usuario.email == email.strip().lower()
        )
    )

    if usuario is None:
        return None

    if not usuario.ativo:
        return None

    if not verify_password(senha, usuario.senha_hash):
        return None

    token = create_access_token(
        subject=str(usuario.id)
    )

    return token
