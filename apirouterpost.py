import random
from fastapi import APIRouter, HTTPException
from modelo_base import ProdutoMonitorado

router = APIRouter(prefix="/vendas", tags=["Automacao"])

# Função simulada para representar o Web Scraping do robô acessando o link do fornecedor
def extrair_preco_atual_fornecedor(url: str) -> float:
    # Na vida real, aqui você usaria Requests/BeautifulSoup/Selenium para ler a página do fornecedor.
    # Para testar, vamos simular que o robô descobriu um preço aleatório próximo a R$ 100
    return round(random.uniform(90.0, 130.0), 2)

# Função simulada para representar o envio de dados via API oficial (Mercado Livre / Shopee)
def atualizar_anuncio_na_plataforma(id_anuncio: str, novo_preco: float, pausar: bool = False):
    if pausar:
        print(f"[API MARKETPLACE] Cenário crítico! Pausando anúncio {id_anuncio} para evitar prejuízo.")
    else:
        print(f"[API MARKETPLACE] Cenário seguro. Atualizando anúncio {id_anuncio} para o novo preço: R$ {novo_preco}")

@router.post("/verificar-cenario")
async def verificar_e_vender(produto: ProdutoMonitorado):
    # 1. O robô vai até o link do fornecedor e descobre a situação em tempo real
    try:
        preco_real_fornecedor = extrair_preco_atual_fornecedor(str(produto.link_fornecedor))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao acessar o link do fornecedor.")

    print(f"\n[Robô] Analisando cenário do fornecedor...")
    print(f"-> Preço de custo guardado no sistema: R$ {produto.preco_custo_atual}")
    print(f"-> Preço real detectado no link agora: R$ {preco_real_fornecedor}")

    # 2. Tomada de decisão inteligente baseada no cenário
    if preco_real_fornecedor > produto.preco_custo_atual:
        # CENÁRIO MUDOU PARA PIOR: O fornecedor aumentou o preço!
        print("[Robô] Alerta! O fornecedor aumentou o preço de custo. Recalculando valor...")
        
        # Recalcula o novo valor de venda com base no seu markup personalizado
        novo_preco_venda = round(preco_real_fornecedor * produto.markup, 2)
        
        # Se o aumento for abusivo (ex: mais de 25% de surpresa), o robô toma a decisão segura de pausar
        if preco_real_fornecedor > (produto.preco_custo_atual * 1.25):
            atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=True)
            return {
                "status": "analisado_e_pausado",
                "motivo": "Aumento excessivo no preço do fornecedor. Venda bloqueada por segurança.",
                "preco_fornecedor_detectado": preco_real_fornecedor
            }
        
        # Se for um aumento gerenciável, o robô apenas corrige o preço na plataforma para você não perder margem
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, novo_preco_venda, pausar=False)
        return {
            "status": "cenario_atualizado",
            "acao": "Preço corrigido automaticamente no Marketplace para manter o lucro.",
            "novo_preco_venda": novo_preco_venda
        }

    else:
        # CENÁRIO ESTÁVEL OU MELHOR: O preço continua igual ou até caiu!
        print("[Robô] Cenário seguro! O produto continua viável para venda.")
        preco_venda_normal = round(produto.preco_custo_atual * produto.markup, 2)
        
        atualizar_anuncio_na_plataforma(produto.id_anuncio_meu, preco_venda_normal, pausar=False)
        return {
            "status": "autorizado_para_venda",
            "preco_venda_ativo": preco_venda_normal,
            "preco_fornecedor_atual": preco_real_fornecedor
        }
