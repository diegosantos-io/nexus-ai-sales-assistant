from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.registro import (
    RegistroEmpresa,
    RegistroEmpresaResponse,
)
from app.services.registro_service import registrar_empresa


router = APIRouter(
    prefix="/registro",
    tags=["Registro"]
)


@router.post(
    "/empresa",
    response_model=RegistroEmpresaResponse,
    status_code=status.HTTP_201_CREATED
)
def cadastrar_empresa(
    dados: RegistroEmpresa,
    db: Session = Depends(get_db)
):
    try:
        empresa, administrador = registrar_empresa(db, dados)

        return {
            "empresa": empresa,
            "administrador": administrador
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )
