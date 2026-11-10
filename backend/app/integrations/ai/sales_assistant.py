
import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3.5:4b"


def gerar_resposta(mensagens: list[dict[str, str]]) -> str:
    try:
        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": mensagens,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=(10, 120)
        )

        resposta.raise_for_status()

        dados = resposta.json()

        if not isinstance(dados, dict):
            raise ValueError("Formato de resposta inválido do Ollama.")

        mensagem = dados.get("message")

        if not isinstance(mensagem, dict):
            raise ValueError("A resposta do Ollama não contém uma mensagem válida.")

        conteudo = mensagem.get("content")

        if not isinstance(conteudo, str) or not conteudo.strip():
            raise ValueError("A IA retornou uma resposta vazia ou inválida.")

        return conteudo.strip()

    except requests.RequestException as erro:
        raise RuntimeError(
            f"Erro ao se comunicar com o Ollama: {erro}"
        ) from erro
