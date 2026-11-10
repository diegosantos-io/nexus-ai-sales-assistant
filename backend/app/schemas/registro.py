from pydantic import BaseModel, EmailStr, Field


class RegistroEmpresa(BaseModel):
    nome_empresa: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=160)
    email_empresa: EmailStr
    telefone_empresa: str | None = Field(
        default=None,
        max_length=30
    )

    nome_responsavel: str = Field(
        min_length=2,
        max_length=150
    )
    email_responsavel: EmailStr
    senha: str = Field(min_length=8, max_length=128)


from app.schemas.empresa import EmpresaResponse
from app.schemas.usuario import UsuarioResponse


class RegistroEmpresaResponse(BaseModel):
    empresa: EmpresaResponse
    administrador: UsuarioResponse

