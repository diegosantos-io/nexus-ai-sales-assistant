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
            timeout=120
        )

        resposta.raise_for_status()

        dados = resposta.json()
        conteudo = dados.get("message", {}).get("content", "")

        if not conteudo or not conteudo.strip():
            raise ValueError("A IA retornou uma resposta vazia.")

        return conteudo.strip()

    except requests.RequestException as erro:
        raise RuntimeError(
            f"Erro ao se comunicar com o Ollama: {erro}"
        ) from erro
