
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.login import LoginRequest, LoginResponse
from app.services.auth_service import autenticar_usuario
from app.core.dependencies import get_usuario_atual


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):
    token = autenticar_usuario(
        db=db,
        email=str(dados.email),
        senha=dados.senha
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def usuario_logado(
    usuario = Depends(get_usuario_atual)
):
    return {
        "id": str(usuario.id),
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
        "nome": usuario.nome,
        "email": usuario.email,
        "role": usuario.role
    }