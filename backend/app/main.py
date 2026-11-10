from fastapi import FastAPI

from app.routers.registro import router as registro_router
from app.routers.auth import router as auth_router
from app.routers.clientes import router as clientes_router
from app.routers.conversas import router as conversas_router
from app.routers.mensagens import router as mensagens_router
from app.routers.produtos import router as produtos_router


app = FastAPI(
    title="Nexus AI Sales Assistant",
    description="API de atendimento e vendas com Inteligência Artificial",
    version="1.0.0"
)


app.include_router(
    registro_router,
    prefix="/api/v1"
)

app.include_router(
    auth_router,
    prefix="/api/v1"
)

app.include_router(
    clientes_router,
    prefix="/api/v1"
)

app.include_router(
    conversas_router, 
    prefix="/api/v1"
)

app.include_router(
    mensagens_router,
      prefix="/api/v1"
)

app.include_router(
    produtos_router,
    prefix="/api/v1"
)


@app.get("/")
def home():
    return {
        "message": "Nexus AI Sales Assistant API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
