import re
import json
from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
from modelo_base import ProdutoMonitorado

router = APIRouter(prefix="/vendas", tags=["Automacao"])

def extrair_preco_atual_fornecedor(url: str) -> float:
    """
    Acessa o link do Mercado Livre, extrai o preço real do produto
    e verifica se o anúncio está ativo.
    """
    # Headers para simular um navegador comum e evitar bloqueios básicos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        
        # Se o link mudou ou o produto sumiu (Erro 404), o cenário é crítico
        if resposta.status_code == 404:
            raise ValueError("Produto não encontrado (Erro 404).")
            
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # 1. Verifica se o anúncio está pausado/esgotado na página
        botao_comprar = soup.find('button', {'class': re.compile(regex_match:=r'.*ui-pdp-actions__button.*')})
        texto_pagina = soup.get_text().lower()
        if "anúncio pausado" in texto_pagina or "último disponível" not in texto_pagina and not botao_comprar:
            raise ValueError("Estoque zerado ou anúncio pausado no fornecedor.")

        # 2. Busca o preço estruturado dentro da tag meta (padrão do Mercado Livre)
        meta_price = soup.find('meta', {'property': 'item-price'}) or soup.find('meta', {'itemprop': 'price'})
        if meta_price and meta_price.get('content'):
            return float(meta_price['content'])
            
        # 3. Fallback: Se não achar na tag meta, busca no JSON estruturado da página (Schema.org)
        script_json = soup.find('script', {'type': 'application/ld+json'})
        if script_json:
            dados = json.loads(script_json.string)
            # O schema do ML pode vir como lista ou dicionário direto
            if isinstance(dados, list):
                for item in dados:
                    if item.get('@type') == 'Product' or 'offers' in item:
                        return float(item['offers']['price'])
            elif dados.get('offers', {}).get('price'):
                return float(dados['offers']['price'])
                
        raise ValueError("Preço não localizado na página do Mercado Livre.")

    except Exception as e:
        # Repassa o erro exato para a tomada de decisão do robô
        raise RuntimeError(str(e))

def atualizar_anuncio_na_plataforma(id_anuncio: str, novo_preco: float, pausar: bool = False):
    if pausar:
        print(f"\n[⚠️ API MARKETPLACE] Bloqueando anúncio {id_anuncio} imediatamente.")
    else:
        print(f"\n[✅ API MARKETPLACE] Enviando atualização do anúncio {id_anuncio}. Novo preço de venda: R$ {novo_preco}")

@router.post("/verificar-cenario")
async def verificar_e_vender(produto: ProdutoMonitorado):
    print(f"\n[Robô] Iniciando varredura no Mercado Livre...")
    
    try:
        # O robô agora acessa o LINK REAL fornecido
        preco_real_fornecedor = extrair_preco_atual_fornecedor(str(produto.link_fornecedor))
        
    except Exception as erro_cenario:
        # Se der erro de estoque ou página caída, o robô toma a decisão mais segura: PAUSA O SEU ANÚNCIO
        print(f"[Robô] Mudança crítica de cenário detectada: {erro_cenario}")
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, 0, pausar=True)
        return {
            "status": "analisado_e_pausado",
            "motivo": f"Inconsistência no fornecedor: {erro_cenario}. Seu anúncio foi pausado preventivamente."
        }

    print(f"-> Preço de custo em banco: R$ {produto.preco_custo_atual}")
    print(f"-> Preço real no Mercado Livre agora: R$ {preco_real_fornecedor}")

    # Tomada de decisão inteligente baseada no preço real coletado
    if preco_real_fornecedor > produto.preco_custo_atual:
        print("[Robô] O fornecedor aumentou o preço! Recalculando margens...")
        novo_preco_venda = round(preco_real_fornecedor * produto.markup, 2)
        
        # Aumento muito agressivo (mais de 30%): Pausa por segurança
        if preco_real_fornecedor > (produto.preco_custo_atual * 1.30):
            atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=True)
            return {
                "status": "analisado_e_pausado",
                "motivo": "Aumento excessivo do fornecedor (>30%). Anúncio pausado para revisão manual.",
                "preco_fornecedor_detectado": preco_real_fornecedor
            }
        
        # Aumento leve: Atualiza o preço mantendo a venda ativa
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=False)
        return {
            "status": "cenario_atualizado",
            "acao": "Preço reajustado no seu anúncio para manter a margem de lucro.",
            "novo_preco_venda": novo_preco_venda
        }

    else:
        # Cenário seguro (preço igual ou menor)
        preco_venda_normal = round(produto.preco_custo_atual * produto.markup, 2)
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, preco_venda_normal, pausar=False)
        return {
            "status": "autorizado_para_venda",
            "preco_venda_ativo": preco_venda_normal,
            "preco_fornecedor_atual": preco_real_fornecedor
        }
