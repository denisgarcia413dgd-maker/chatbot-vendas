import re
import json
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncIOMotorClient
import requests
from bs4 import BeautifulSoup
from medico import chamar_medico_claude

# --- BANCO ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["robo_dropshipping"]

api_router = APIRouter()
router = api_router

# --- MODELOS WEBHOOK ---
class DeliveryAddress(BaseModel):
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    recipient_name: str
    cpf: str

class OrderWebhookInput(BaseModel):
    resource_id: str
    topic: str
    status: str
    item_id: str
    quantity: int
    shipping_address: DeliveryAddress

# --- MODELO QUE FALTAVA ---
class ProdutoMonitorado(BaseModel):
    id_anuncio_meu: str
    link_fornecedor: HttpUrl
    preco_custo_atual: float
    markup: float = 1.6

# --- FUNCAO 1: EXTRAIR PRECO ---
def extrair_preco_atual_fornecedor(url: str) -> float:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 404:
            raise ValueError("Link do fornecedor nao existe mais - 404")

        soup = BeautifulSoup(resposta.text, 'html.parser')
        texto_pagina = soup.get_text().lower()

        # CORRIGIDO: sem walrus, sem re.compile quebrado
        botao_comprar = soup.find('button', class_=re.compile(r'.*ui-pdp-actions__button.*'))
        if "anuncio pausado" in texto_pagina or ("ultimo disponivel" not in texto_pagina and not botao_comprar):
            raise ValueError("Estoque zerado ou anuncio pausado no fornecedor.")

        meta_price = soup.find('meta', {'property': 'item-price'}) or soup.find('meta', {'itemprop': 'price'})
        if meta_price and meta_price.get('content'):
            return float(meta_price['content'])

        script_json = soup.find('script', {'type': 'application/ld+json'})
        if script_json and script_json.string:
            dados = json.loads(script_json.string)
            if isinstance(dados, list):
                for item in dados:
                    if item.get('@type') == 'Product' or 'offers' in item:
                        return float(item['offers']['price'])
            elif dados.get('offers', {}).get('price'):
                return float(dados['offers']['price'])

        raise ValueError("Preco nao localizado na pagina do Mercado Livre.")
    except Exception as e:
        raise RuntimeError(str(e))

def atualizar_anuncio_na_plataforma(id_anuncio: str, novo_preco: float, pausar: bool = False):
    if pausar:
        print(f"\n[API MARKETPLACE] Bloqueando anuncio {id_anuncio} imediatamente.")
    else:
        print(f"\n[API MARKETPLACE] Atualizando anuncio {id_anuncio}. Novo preco: R$ {novo_preco}")

# --- FUNCAO 2: VERIFICAR CENARIO ---
@api_router.post("/vendas/verificar-cenario")
async def verificar_e_vender(produto: ProdutoMonitorado):
    print(f"\n[Robo] Iniciando varredura no Mercado Livre...")
    try:
        preco_real_fornecedor = extrair_preco_atual_fornecedor(str(produto.link_fornecedor))
    except Exception as erro_cenario:
        print(f"[Robo] Mudanca critica: {erro_cenario}")
        # Chama o medico sem expor dados
        diagnostico = chamar_medico_claude(
            tipo_erro="Falha cenario fornecedor",
            detalhe_erro=str(erro_cenario),
            onde_aconteceu="vendas.py - verificar_e_vender"
        )
        await db.status_checks.insert_one({
            "client_name": "Medico Claude",
            "timestamp": datetime.now(timezone.utc),
            "detail": f"DIAGNOSTICO CENARIO: {diagnostico}"
        })
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, 0, pausar=True)
        return {"status": "analisado_e_pausado", "motivo": f"Inconsistencia no fornecedor: {erro_cenario}. Anuncio pausado."}

    print(f"-> Custo banco: R$ {produto.preco_custo_atual}")
    print(f"-> Preco real ML agora: R$ {preco_real_fornecedor}")

    if preco_real_fornecedor > produto.preco_custo_atual:
        novo_preco_venda = round(preco_real_fornecedor * produto.markup, 2)
        if preco_real_fornecedor > (produto.preco_custo_atual * 1.30):
            atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=True)
            return {"status": "analisado_e_pausado", "motivo": "Aumento >30%. Pausado para revisao.", "preco_fornecedor_detectado": preco_real_fornecedor}
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=False)
        return {"status": "cenario_atualizado", "acao": "Preco reajustado.", "novo_preco_venda": novo_preco_venda}
    else:
        preco_venda_normal = round(produto.preco_custo_atual * produto.markup, 2)
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, preco_venda_normal, pausar=False)
        return {"status": "autorizado_para_venda", "preco_venda_ativo": preco_venda_normal, "preco_fornecedor_atual": preco_real_fornecedor}

# --- FUNCAO 3: WEBHOOK VENDA ---
@api_router.post("/webhook/venda-notificada")
async def receber_e_processar_venda(notificacao: OrderWebhookInput):
    if notificacao.status != "paid":
        return {"status": "ignored", "message": "Apenas pagamento aprovado."}
    ja_existe = await db.orders.find_one({"id_venda_origem": notificacao.resource_id})
    if ja_existe:
        return {"status": "ignored", "message": "Venda ja processada."}
    produto_vinculado = await db.products.find_one({"id_interno": notificacao.item_id})
    if not produto_vinculado:
        produto_vinculado = await db.products.find_one({"remote_id": notificacao.item_id})
    if not produto_vinculado:
        diagnostico = chamar_medico_claude(
            tipo_erro="Produto nao encontrado",
            detalhe_erro=f"item_id={notificacao.item_id} nao achado",
            onde_aconteceu="vendas.py - receber_e_processar_venda"
        )
        await db.status_checks.insert_one({"client_name": "Medico Claude", "timestamp": datetime.now(timezone.utc), "detail": f"DIAGNOSTICO: {diagnostico}"})
        raise HTTPException(status_code=404, detail="Produto nao encontrado.")
    link_fornecedor = produto_vinculado.get("link_fornecedor")
    ordem = {
        "id_venda_origem": notificacao.resource_id,
        "link_compra_fornecedor": link_fornecedor,
        "quantidade": notificacao.quantity,
        "dados_cliente_final": notificacao.shipping_address.model_dump(),
        "status_automacao": "Pendente - Pronto para Envio Automatico",
        "data_captura": datetime.now(timezone.utc)
    }
    await db.orders.insert_one(ordem)
    await db.status_checks.insert_one({"client_name": "Robo Despachante", "timestamp": datetime.now(timezone.utc), "detail": f"VENDA DETECTADA: Pedido {notificacao.resource_id} pronto para envio."})
    return {"status": "success", "message": "Fulfillment iniciado.", "order_id": notificacao.resource_id}
# --- PORTAS PRO APP DO CELULAR ---
import collections
LOGS_MEMORIA = collections.deque(maxlen=100)

def add_log(msg: str):
    LOGS_MEMORIA.appendleft({"message": msg, "level": "info", "created_at": datetime.now(timezone.utc).isoformat()})
    print(msg)

@api_router.get("/logs")
async def get_logs():
    try:
        docs = await db.status_checks.find().sort("timestamp", -1).limit(50).to_list(50)
        logs_db = [{"message": d.get("detail", ""), "level": "info", "created_at": str(d.get("timestamp", ""))} for d in docs]
        return list(LOGS_MEMORIA) + logs_db
    except:
        return list(LOGS_MEMORIA)

@api_router.get("/stats")
async def get_stats():
    try:
        total = await db.orders.count_documents({})
        return {"total_vendas": total, "lucro_total": 0, "anuncios_ativos": 0}
    except:
        return {"total_vendas": 0, "lucro_total": 0, "anuncios_ativos": 0}

@api_router.post("/bot/cycle")
async def bot_cycle():
    add_log("Robo: ciclo iniciado pelo app")
    return {"status": "ok", "message": "Ciclo executado"}

@api_router.get("/bot/status")
async def bot_status():
    return {"active": True, "running": False}
