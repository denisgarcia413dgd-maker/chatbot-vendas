import os
import requests
from datetime import datetime, timezone

# NÃO manda CPF, nome, endereço pro Claude. Só o erro.
# Chave vai no Render em Environment, nunca no código.

def chamar_medico_claude(tipo_erro: str, detalhe_erro: str, onde_aconteceu: str):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        print("Medico sem chave - pulando")
        return None

    prompt = f"""
    Voce e o medico de um robo de dropshipping em Python / FastAPI / MongoDB.
    Analise este erro e devolva em 3 linhas: 1) Causa provavel, 2) Arquivo e linha para corrigir, 3) Codigo corrigido.
    Erro em: {onde_aconteceu}
    Tipo: {tipo_erro}
    Detalhe: {detalhe_erro}
    NAO invente dados de cliente. NAO peca CPF.
    """

    try:
        resposta = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": chave,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=20
        )
        dados = resposta.json()
        texto = dados["content"][0]["text"]
        return texto
    except Exception as e:
        print(f"Medico falhou: {e}")
        return None
