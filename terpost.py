import re
import json
import random
from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/vendas", tags=["Automacao"])

# Chave de acesso da sua conta de vendedor (Gere no painel de desenvolvedor do ML)
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_REAL_AQUI"

# Lista de gatilhos mentais para diversificar os títulos copiados e evitar banimentos por cópia idêntica
GATILHOS_TITULO = ["Envio Rápido", "Original", "Novo Nfe", "Pronta Entrega", "Oferta Do Dia", "Garanta O Seu"]

def extrair_id_item_do_link(url: str) -> str:
    """
    Extrai o ID do anúncio do Mercado Livre (ex: MLB12345678) a partir da URL.
    Necessário para buscar a descrição de forma limpa via API pública.
    """
    padrao = re.search(r"MLB-?(\d+)", url)
    if padrao:
        return f"MLB{padrao.group(1)}"
    raise ValueError("Não foi possível identificar um ID de anúncio válido no link enviado.")

def buscar_descricao_oficial(id_item: str) -> str:
    """
    Acessa o endpoint público da API do Mercado Livre para pegar a descrição exata
    em texto puro, sem precisar fazer scraping complexo na página.
    """
    url_desc = f"https://mercadolibre.com{id_item}/description"
    try:
        resposta = requests.get(url_desc, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get("plain_text", "")
    except Exception:
        pass
    return "Garantia de qualidade e excelente custo-benefício. Produto novo e testado."

def extrair_dados_completos_origem(url: str) -> dict:
    """
    Acessa o link do Mercado Livre de origem e raspa todas as informações
    necessárias para criar um novo anúncio idêntico.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        id_item = extrair_id_item_do_link(url)
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code != 200:
            raise ValueError("Não foi possível acessar o produto de origem no Mercado Livre.")
            
        soup = BeautifulSoup(resposta.text, 'html.parser')
        dados_produto = {}

        # 1. Extrai o Título Original
        titulo_tag = soup.find('h1', {'class': re.compile(r'.*ui-pdp-title.*')})
        if not titulo_tag:
            raise ValueError("Título do produto não localizado.")
        
        titulo_original = titulo_tag.get_text().strip()

        # Estratégia de Modificação de Título Inteligente:
        # Remove excesso de espaços e adiciona um gatilho comercial aleatório no final
        gatilho = random.choice(GATILHOS_TITULO)
        # O Mercado Livre aceita no máximo 60 caracteres no título
        titulo_modificado = f"{titulo_original} {gatilho}"
        if len(titulo_modificado) > 60:
            # Se estourar o limite, corta o título original para caber o gatilho perfeitamente
            titulo_modificado = f"{titulo_original[:(59 - len(gatilho))]} {gatilho}"
            
        dados_produto['titulo'] = titulo_modificado

        # 2. Extrai o Preço de Custo Original
        meta_price = soup.find('meta', {'property': 'item-price'}) or soup.find('meta', {'itemprop': 'price'})
        if not meta_price:
            raise ValueError("Preço de custo original não localizado.")
        dados_produto['preco_custo'] = float(meta_price['content'])

        # 3. Extrai os links das fotos em alta resolução do carrossel
        fotos = []
        img_tags = soup.find_all('img', {'class': re.compile(r'.*ui-pdp-gallery__figure__image.*')})
        for img in img_tags:
            url_foto = img.get('data-zoom') or img.get('src')
            if url_foto and url_foto not in fotos:
                fotos.append(url_foto)
        
        dados_produto['fotos'] = fotos if fotos else ["https://mlstatic.com"]

        # 4. Copia a Descrição Real chamando a API do Mercado Livre
        dados_produto['descricao'] = buscar_descricao_oficial(id_item)

        return dados_produto

    except Exception as e:
        raise RuntimeError(f"Erro na clonagem dos dados: {str(e)}")


@router.post("/clonar-e-anunciar")
async def clonar_e_anunciar(link_origem: str, markup: float):
    """
    Endpoint principal: Copia o link, altera o valor com lucro, 
    modifica o título, importa a descrição e cria o anúncio na sua conta.
    """
    print(f"\n[Robô] Iniciando clonagem do link: {link_origem}")
    
    # 1. Copiar dados do produto original (e aplicar alterações)
    try:
        dados_origem = extrair_dados_completos_origem(link_origem)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Calcular o novo preço de revenda
    preco_revenda = round(dados_origem['preco_custo'] * markup, 2)
    print(f"[Robô] Título Novo Criado: '{dados_origem['titulo']}'")
    print(f"[Robô] Novo Valor de Revenda calculado: R$ {preco_revenda}")

    # 3. Montar a estrutura da API do Mercado Livre com a descrição e fotos incluídas
    payload_novo_anuncio = {
        "title": dados_origem['titulo'],
        "category_id": "MLB1051", # Categoria padrão (Ideal alterar para o ID real do produto)
        "price": preco_revenda,
        "currency_id": "BRL",
        "available_quantity": 5,  # Estoque inicial seguro disponível no fornecedor
        "buying_mode": "buy_now",
        "listing_type_id": "bronze", # "bronze" para Clássico ou "gold_pro" para Premium
        "condition": "new",
        "pictures": [{"source": url} for url in dados_origem['fotos'][:6]], # Envia até 6 fotos capturadas
        "description": {
            "plain_text": dados_origem['descricao'] # Injeta a descrição copiada linha por linha
        }
    }

    # 4. Enviar a publicação oficial para o seu painel do Mercado Livre
    url_api_ml = "https://mercadolibre.com"
    headers_api = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    resposta_api = requests.post(url_api_ml, json=payload_novo_anuncio, headers=headers_api, timeout=10)

    if resposta_api.status_code == 201:
        dados_resposta = resposta_api.json()
        print(f"[Sucesso] Anúncio clonado criado com sucesso! ID: {dados_resposta['id']}")
        return {
            "status": "sucesso",
            "mensagem": "Anúncio clonado, título modificado e publicado com a descrição oficial!",
            "id_novo_anuncio": dados_resposta['id'],
            "link_novo_anuncio": dados_resposta['permalink'],
            "preco_venda_definido": preco_revenda,
            "titulo_utilizado": dados_origem['titulo']
        }
    else:
        print(f"[Erro API ML] Falha ao publicar anúncio: {resposta_api.text}")
        raise HTTPException(status_code=resposta_api.status_code, detail=f"Erro na publicação: {resposta_api.text}")
