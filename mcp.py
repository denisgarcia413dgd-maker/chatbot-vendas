# servidor_mcp.py - MCP DO DEIVÃO
# Deixa qualquer agente (Claude, Cursor) usar seu sistema de vendas
# SEM ver suas chaves. As chaves ficam no Render, em Environment.

import os
from mcp.server.fastmcp import FastMCP

# Importa suas funções que já existem
from vendas import buscar_produto, criar_pedido, verificar_status
from medico import chamar_medico_claude

mcp = FastMCP("vendas-deivao")

@mcp.tool()
def listar_produto(nome: str) -> str:
    """Lista um produto pelo nome. Use quando o cliente perguntar preço ou estoque."""
    resultado = buscar_produto(nome)
    if not resultado:
        return f"Produto '{nome}' não encontrado. Vou chamar o médico."
    return f"Produto: {resultado['nome']} | Preço: R$ {resultado['preco']} | Estoque: {resultado['estoque']}"

@mcp.tool()
def criar_pedido_mcp(produto: str, cliente_id: str) -> str:
    """Cria um pedido. NUNCA mande CPF ou nome do cliente aqui, só o ID."""
    pedido = criar_pedido(produto, cliente_id)
    return f"Pedido criado: {pedido['id']} | Status: {pedido['status']}"

@mcp.tool()
def verificar_pedido_mcp(pedido_id: str) -> str:
    """Verifica o status de um pedido pelo ID."""
    status = verificar_status(pedido_id)
    return f"Pedido {pedido_id}: {status}"

@mcp.tool()
def chamar_medico(problema: str) -> str:
    """Chama o médico (Claude) quando tem bug, produto sumido ou fornecedor com problema. Não mande dados do cliente."""
    return chamar_medico_claude(problema)

if __name__ == "__main__":
    mcp.run()
