from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.registro import RegistroEmpresa


def registrar_empresa(
    db: Session,
    dados: RegistroEmpresa
) -> tuple[Empresa, Usuario]:

    try:
        # Criar empresa
        empresa = Empresa(
            nome=dados.nome_empresa.strip(),
            slug=dados.slug.strip().lower(),
            email=str(dados.email_empresa).lower(),
            telefone=dados.telefone_empresa
        )

        db.add(empresa)

        # Obter o UUID da empresa
        db.flush()

        # Criar administrador da empresa
        administrador = Usuario(
            empresa_id=empresa.id,
            nome=dados.nome_responsavel.strip(),
            email=str(dados.email_responsavel).lower(),
            senha_hash=hash_password(dados.senha),
            role="admin",
            ativo=True
        )

        db.add(administrador)

        # Confirmar as duas operações
        db.commit()

        db.refresh(empresa)
        db.refresh(administrador)

        return empresa, administrador

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "E-mail ou identificador da empresa já cadastrado."
        )

    except Exception:
        db.rollback()
        raise
