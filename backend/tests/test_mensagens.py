from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_usuario_atual
from app.database.connection import get_db
from app.routers.mensagens import gerar_resposta


def test_falha_da_ia_retorna_503_e_preserva_mensagem(monkeypatch):
    empresa_id = uuid4()
    conversa_id = uuid4()

    usuario = SimpleNamespace(
        id=uuid4(),
        empresa_id=empresa_id,
        ativo=True
    )

    conversa = SimpleNamespace(
        id=conversa_id,
        empresa_id=empresa_id,
        status="aberta"
    )

    mensagens_salvas = []

    class BancoFake:
        def scalar(self, consulta):
            return conversa

        def add(self, mensagem):
            mensagens_salvas.append(mensagem)

        def commit(self):
            pass

        def refresh(self, mensagem):
            pass

    banco = BancoFake()

    def substituir_usuario():
        return usuario

    def substituir_banco():
        yield banco

    def falhar_ia(mensagens):
        raise RuntimeError("Ollama indisponível")

    monkeypatch.setattr(
        "app.routers.mensagens.obter_historico_conversa",
        lambda conversa_id, db: []
    )

    monkeypatch.setattr(
        "app.routers.mensagens.obter_catalogo_empresa",
        lambda empresa_id, db: []
    )

    monkeypatch.setattr(
        "app.routers.mensagens.gerar_resposta",
        falhar_ia
    )

    app.dependency_overrides[get_usuario_atual] = substituir_usuario
    app.dependency_overrides[get_db] = substituir_banco

    try:
        with TestClient(app) as cliente:
            resposta = cliente.post(
                f"/api/v1/conversas/{conversa_id}/mensagens/",
                json={
                    "conteudo": "Gostaria de conhecer os produtos."
                }
            )

        assert resposta.status_code == 503

        assert "Sua mensagem foi salva" in resposta.json()["detail"]

        assert len(mensagens_salvas) == 1

        assert mensagens_salvas[0].remetente == "user"

        assert (
            mensagens_salvas[0].conteudo
            == "Gostaria de conhecer os produtos."
        )

    finally:
        app.dependency_overrides.clear()


def test_usuario_nao_acessa_conversa_de_outra_empresa(monkeypatch):
    empresa_a_id = uuid4()
    empresa_b_id = uuid4()
    conversa_id = uuid4()

    usuario_empresa_a = SimpleNamespace(
        id=uuid4(),
        empresa_id=empresa_a_id,
        ativo=True
    )

    class BancoFake:
        def scalar(self, consulta):
            # A consulta filtra pela empresa A.
            # A conversa pertence à empresa B.
            return None

    banco = BancoFake()

    def substituir_usuario():
        return usuario_empresa_a

    def substituir_banco():
        yield banco

    app.dependency_overrides[get_usuario_atual] = substituir_usuario
    app.dependency_overrides[get_db] = substituir_banco

    try:
        with TestClient(app) as cliente:
            resposta = cliente.post(
                f"/api/v1/conversas/{conversa_id}/mensagens/",
                json={
                    "conteudo": "Quero consultar um produto."
                }
            )

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Conversa não encontrada."

    finally:
        app.dependency_overrides.clear()


def test_nao_permite_mensagem_em_conversa_encerrada():
    empresa_id = uuid4()
    conversa_id = uuid4()

    usuario = SimpleNamespace(
        id=uuid4(),
        empresa_id=empresa_id,
        ativo=True
    )

    conversa = SimpleNamespace(
        id=conversa_id,
        empresa_id=empresa_id,
        status="encerrada"
    )

    class BancoFake:
        def scalar(self, consulta):
            return conversa

    banco = BancoFake()

    def substituir_usuario():
        return usuario

    def substituir_banco():
        yield banco

    app.dependency_overrides[get_usuario_atual] = substituir_usuario
    app.dependency_overrides[get_db] = substituir_banco

    try:
        with TestClient(app) as cliente:
            resposta = cliente.post(
                f"/api/v1/conversas/{conversa_id}/mensagens/",
                json={
                    "conteudo": "Gostaria de comprar um produto."
                }
            )

        assert resposta.status_code == 409

        assert (
            resposta.json()["detail"]
            == "Não é possível enviar mensagens em uma conversa encerrada."
        )

    finally:
        app.dependency_overrides.clear()



def test_nao_permite_mensagem_com_apenas_espacos():
    empresa_id = uuid4()
    conversa_id = uuid4()

    usuario = SimpleNamespace(
        id=uuid4(),
        empresa_id=empresa_id,
        ativo=True
    )

    conversa = SimpleNamespace(
        id=conversa_id,
        empresa_id=empresa_id,
        status="aberta"
    )

    mensagens_salvas = []

    class BancoFake:
        def scalar(self, consulta):
            return conversa

        def add(self, mensagem):
            mensagens_salvas.append(mensagem)

    banco = BancoFake()

    def substituir_usuario():
        return usuario

    def substituir_banco():
        yield banco

    app.dependency_overrides[get_usuario_atual] = substituir_usuario
    app.dependency_overrides[get_db] = substituir_banco

    try:
        with TestClient(app) as cliente:
            resposta = cliente.post(
                f"/api/v1/conversas/{conversa_id}/mensagens/",
                json={"conteudo": "   "}
            )

        assert resposta.status_code == 422

        assert (
            resposta.json()["detail"]
            == "O conteúdo da mensagem não pode estar vazio."
        )

        assert len(mensagens_salvas) == 0

    finally:
        app.dependency_overrides.clear()
