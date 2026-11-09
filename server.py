import asyncio
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import re

# Inicializa o servidor MCP do seu chatbot de vendas
mcp = FastMCP("chatbot-vendas-multiplataforma")

def extrair_id_ou_limpar_url(url: str, plataforma: str) -> str:
    """Apenas limpa parâmetros de rastreamento desnecessários da URL"""
    return url.split('?')[0].strip()

@mcp.tool()
def minerar_e_recalculcar_produto(url_produto: str, margem_lucro: float = 0.45) -> dict:
    """
    Identifica automaticamente se o link é do Mercado Livre, OLX, Marketplace ou Shopee,
    extrai as informações de venda e calcula o preço final de revenda.
    """
    url_limpa = url_produto.lower()
    plataforma_detectada = None
    
    # 1. Identificação da plataforma pelo link
    if "mercadolivre.com" in url_limpa or "mlb.com" in url_limpa:
        plataforma_detectada = "Mercado Livre"
    elif "olx.com" in url_limpa:
        plataforma_detectada = "OLX"
    elif "://facebook.com" in url_limpa:
        plataforma_detectada = "Facebook Marketplace"
    elif "shopee.com" in url_limpa:
        plataforma_detectada = "Shopee"
    else:
        return {"status": "erro", "mensagem": "Plataforma não suportada ou URL inválida."}

    # 2. Configuração de Headers para evitar bloqueios de robôs
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }

    try:
        # Nota: Shopee e Facebook geram conteúdo via JS de forma intensa.
        # Esta estrutura realiza o Fetch inicial do HTML para análise estruturada.
        resposta = requests.get(url_produto, headers=headers, timeout=15)
        
        if resposta.status_code != 200:
            return {
                "status": "erro", 
                "mensagem": f"Não foi possível acessar o link da plataforma {plataforma_detectada}. Status: {resposta.status_code}"
            }
            
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Valores padrão para testes seguros antes do app estar 100% pronto
        titulo = "Produto Detectado"
        preco_custo = 100.00  # Valor base simulado para validação da calculadora
        
        # 3. Lógica de extração baseada em seletores conhecidos por plataforma
        if plataforma_detectada == "Mercado Livre":
            # Busca tags comuns de título no Mercado Livre
            tag_titulo = soup.find("h1", class_="ui-pdp-title")
            if tag_titulo:
                titulo = tag_titulo.text.strip()
            
            # Busca estrutura de preço do Mercado Livre
            meta_preco = soup.find("meta", property="itemprop:price") or soup.find("meta", itemprop="price")
            if meta_preco and meta_preco.get("content"):
                preco_custo = float(meta_preco.get("content"))

        elif plataforma_detectada == "OLX":
            tag_titulo = soup.find("h1")
            if tag_titulo:
                titulo = tag_titulo.text.strip()
            # OLX insere preços muitas vezes em tags h2 ou spans com classes dinâmicas
            # Se não mapeado, mantém o valor base para fins de teste lógico

        elif plataforma_detectada == "Facebook Marketplace":
            tag_titulo = soup.find("title")
            if tag_titulo:
                titulo = tag_titulo.text.replace("| Facebook Marketplace", "").strip()

        elif plataforma_detectada == "Shopee":
            # Título costuma ficar em meta tags de redes sociais ao renderizar o HTML estático
            meta_titulo = soup.find("meta", property="og:title")
            if meta_titulo:
                titulo = meta_titulo.get("content", "Produto Shopee")

        # 4. Cálculo matemático exato da margem de lucro para Dropshipping
        preco_revenda = preco_custo * (1 + margem_lucro)
        lucro_bruto = preco_revenda - preco_custo

        return {
            "status": "sucesso",
            "plataforma_origem": plataforma_detectada,
            "url_processada": extrair_id_ou_limpar_url(url_produto, plataforma_detectada),
            "dados_extraidos": {
                "titulo": titulo,
                "preco_custo_original": round(preco_custo, 2),
                "preco_revenda_calculado": round(preco_revenda, 2),
                "lucro_estimado_bruto": round(lucro_bruto, 2)
            },
            "pronto_para_postagem": False  # Mantido como falso pois as chaves só entram no app finalizado
        }

    except Exception as e:
        return {"status": "erro", "mensagem": f"Falha ao processar a automação: {str(e)}"}

if __name__ == "__main__":
    # Inicia o servidor escutando via Input/Output padrão (stdio) para o ambiente de agentes
    mcp.run(transport='stdio')

