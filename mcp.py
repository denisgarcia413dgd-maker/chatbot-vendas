# servidor_mcp.py - MCP DO DEIVAO - VERSAO CERTA PRO SEU vendas.py
# Nao manda CPF, nao manda nome do cliente. So ID e preco.

import os
from mcp.server.fastmcp import FastMCP
from vendas import extrair_preco_atual_fornecedor, ProdutoMonitorado
from medico import chamar_medico_claude

mcp = FastMCP("vendas-deivao")

@mcp.tool()
def ver_preco_fornecedor(link_fornecedor: str) -> str:
    """Ve o preco atual no link do fornecedor (Mercado Livre)."""
    try:
        preco = extrair_preco_atual_fornecedor(link_fornecedor)
        return f"Preco atual no fornecedor: R$ {preco}"
    except Exception as e:
        return f"Erro ao ver preco: {e}"

@mcp.tool()
def verificar_cenario(id_anuncio_meu: str, link_fornecedor: str, preco_custo_atual: float, markup: float = 1.6) -> str:
    """Verifica se o preco subiu, reajusta ou pausa o anuncio. Use quando for fazer varredura."""
    try:
        preco_real = extrair_preco_atual_fornecedor(link_fornecedor)
        if preco_real > preco_custo_atual:
            novo = round(preco_real * markup, 2)
            if preco_real > (preco_custo_atual * 1.30):
                return f"AUMENTO >30%. Custo era R$ {preco_custo_atual}, agora R$ {preco_real}. PAUSAR anuncio {id_anuncio_meu} para revisao."
            return f"Reajustar anuncio {id_anuncio_meu} para R$ {novo}. Custo novo: R$ {preco_real}"
        preco_normal = round(preco_custo_atual * markup, 2)
        return f"Autorizado para venda. Preco ativo: R$ {preco_normal}. Fornecedor: R$ {preco_real}"
    except Exception as e:
        diag = chamar_medico_claude(
            tipo_erro="Falha cenario fornecedor",
            detalhe_erro=str(e),
            onde_aconteceu="servidor_mcp.py - verificar_cenario"
        )
        return f"Fornecedor com problema: {e}. Diagnostico medico: {diag}"

@mcp.tool()
def chamar_medico(tipo_erro: str, detalhe_erro: str) -> str:
    """Chama o medico Claude. NUNCA mande CPF ou nome do cliente, so tipo e detalhe."""
    return chamar_medico_claude(
        tipo_erro=tipo_erro,
        detalhe_erro=detalhe_erro,
        onde_aconteceu="servidor_mcp.py"
    )

if __name__ == "__main__":
    mcp.run()
