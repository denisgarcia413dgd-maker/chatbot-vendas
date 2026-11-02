import re
import json
import random
import os
from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
from modelo_base import ProdutoMonitorado

router = APIRouter(prefix="/vendas", tags=["Automacao"])

ACCESS_TOKEN = "SEU_ACCESS_TOKEN_REAL_AQUI"
GATILHOS_TITULO = ["Envio Rápido", "Original", "Novo Nfe", "Pronta Entrega", "Oferta Do Dia", "Garanta O Seu"]
DB_FILE = "banco_dados.json"

def carregar_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def salvar_no_db(dados):
    with open(DB_FILE, "w") as f:
        json.dump(dados, f, indent=4)

def extrair_id_item_do_link(url: str) -> str:
    padrao = re.search(r"MLB-?(\d+)", url)
    if padrao:
        return f"MLB{padrao.group(1)}"
    raise ValueError("Link do Mercado Livre inválido.")

def buscar_dados_publicos_api(id_item: str) -> dict:
    """
    Acessa a API oficial e pública do Mercado Livre para coletar a categoria exata,
    preço real atualizado e status do estoque de forma 100% precisa.
    """
    url = f"https://mercadolibre.com{id_item}"
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            dados = resposta.json()
            return {
                "preco": float(dados.get("price", 0)),
                "categoria": dados.get("category_id", "MLB1051"),
                "status": dados.get("status", "active"),
                "titulo": dados.get("title", "")
            }
    except:
        pass
    return {}

def buscar_descricao_oficial(id_item: str) -> str:
    url_desc = f"https://mercadolibre.com{id_item}/description"
    try:
        resposta = requests.get(url_desc, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get("plain_text", "")
    except:
        pass
    return "Produto novo de alta qualidade com nota fiscal e garantia."

def atualizar_anuncio_na_plataforma(id_anuncio: str, novo_preco: float, pausar: bool = False):
    url_api = f"https://mercadolibre.com{id_anuncio}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"status": "paused"} if pausar else {"price": novo_preco, "status": "active"}
    
    try:
        resposta = requests.put(url_api, json=payload, headers=headers, timeout=10)
        return resposta.status_code == 200
    except:
        return False

@router.post("/clonar-e-anunciar")
async def clonar_e_anunciar(link_origem: str, markup: float):
    print(f"\n[Robô] Analisando link de origem para clonagem...")
    
    try:
        id_fornecedor = extrair_id_item_do_link(link_origem)
        info_fornecedor = buscar_dados_publicos_api(id_fornecedor)
        
        if not info_fornecedor or info_fornecedor["status"] != "active":
            raise HTTPException(status_code=400, detail="O produto de origem está pausado ou indisponível.")
            
        # 1. Ajuste Inteligente do Título e Cópia de Descrição
        gatilho = random.choice(GATILHOS_TITULO)
        titulo_novo = f"{info_fornecedor['titulo']} {gatilho}"[:60]
        descricao = buscar_descricao_oficial(id_fornecedor)
        
        # 2. Captura Automatizada da Categoria Correta
        categoria_correta = info_fornecedor["categoria"]
        preco_custo = info_fornecedor["preco"]
        preco_revenda = round(preco_custo * markup, 2)
        
        # 3. Fazendo Scraping apenas das imagens na página
        headers = {"User-Agent": "Mozilla/5.0"}
        res_html = requests.get(link_origem, headers=headers, timeout=10)
        soup = BeautifulSoup(res_html.text, 'html.parser')
        fotos = [img.get('data-zoom') or img.get('src') for img in soup.find_all('img', {'class': re.compile(r'.*ui-pdp-gallery__figure__image.*')})]
        if not fotos:
            fotos = ["https://mlstatic.com"]

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar dados de origem: {str(e)}")

    # 4. Criando anúncio na Categoria Correta
    payload_novo = {
        "title": titulo_novo,
        "category_id": categoria_correta, # Mapeamento automático ativo!
        "price": preco_revenda,
        "currency_id": "BRL",
        "available_quantity": 5,
        "buying_mode": "buy_now",
        "listing_type_id": "bronze",
        "condition": "new",
        "pictures": [{"source": url} for url in fotos[:5]],
        "description": {"plain_text": description}
    }

    url_api_ml = "https://mercadolibre.com"
    headers_api = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    resposta_api = requests.post(url_api_ml, json=payload_novo, headers=headers_api, timeout=10)

    if resposta_api.status_code == 201:
        dados_resposta = resposta_api.json()
        id_novo = dados_resposta['id']
        
        # Salva o monitoramento no arquivo local para a rotina do Timer ler depois
        db = carregar_db()
        db.append({
            "id_anuncio_meu": id_novo,
            "id_fornecedor": id_fornecedor,
            "link_fornecedor": link_origem,
            "preco_custo_original": preco_custo,
            "markup": markup
        })
        salvar_no_db(db)
        
        return {"status": "sucesso", "id_novo_anuncio": id_novo, "categoria_mapeada": categoria_correta, "preco_venda": preco_revenda}
    else:
        raise HTTPException(status_code=400, detail=f"Erro na API do Mercado Livre: {resposta_api.text}")

def rotina_auditoria_de_cenario():
    """
    Função automatizada disparada pelo Timer. 
    Ela lê todos os produtos salvos e decide se o mercado mudou.
    """
    print("\n[Timer Ativo] Iniciando checagem cíclica de segurança dos anúncios...")
    produtos = carregar_db()
    
    if not produtos:
        print("[Timer] Nenhum anúncio cadastrado para monitoramento ainda.")
        return

    for p in produtos:
        info_atual_fornecedor = buscar_dados_publicos_api(p["id_fornecedor"])
        
        if not info_atual_fornecedor or info_atual_fornecedor["status"] != "active":
            print(f"[Alerta Cenário] Fornecedor de {p['id_anuncio_meu']} pausou ou sumiu! Pausando seu anúncio por segurança.")
            atualizar_anuncio_na_plataforma(p["id_anuncio_meu"], 0, pausar=True)
            continue
            
        preco_real_agora = info_atual_fornecedor["preco"]
        
        # Se o preço do fornecedor subiu em relação ao custo original que você registrou
        if preco_real_agora > p["preco_custo_original"]:
            novo_preco_venda = round(preco_real_agora * p["markup"], 2)
            
            # Se subiu mais de 30%, bloqueia preventivamente
            if preco_real_agora > (p["preco_custo_original"] * 1.30):
                print(f"[Cenário Crítico] Alta abusiva no fornecedor de {p['id_anuncio_meu']}. Pausando vendas.")
                atualizar_anuncio_na_plataforma(p["id_anuncio_meu"], novo_preco_venda, pausar=True)
            else:
                print(f"[Cenário Alterado] Reajustando preço do anúncio {p['id_anuncio_meu']} para R$ {novo_preco_venda} devido a alteração no fornecedor.")
                atualizar_anuncio_na_plataforma(p["id_anuncio_meu"], novo_preco_venda, pausar=False)
                
                # Atualiza o novo preço de custo base no nosso banco
                p["preco_custo_original"] = preco_real_agora
                salvar_no_db(produtos)
        else:
            print(f"[Cenário Seguro] Anúncio {p['id_anuncio_meu']} verificado. Fornecedor mantém cenário estável.")
