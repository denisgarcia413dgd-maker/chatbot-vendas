# servidor_mcp.py - MCP DO DEIVAO
# Deixa Claude / Cursor usar seu chatbot-vendas sem ver suas chaves
# As chaves ficam no Render em Environment, nunca aqui.

import os

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Falta instalar: pip install mcp")
    raise

mcp = FastMCP("vendas-deivao")

# Tenta usar seu vendas.py que ja existe. Se nao achar, nao quebra.
try:
    import vendas
except ImportError:
    vendas = None

@mcp.tool()
def listar_produto(nome: str) -> str:
    """Lista produto pelo nome. Use quando cliente perguntar preco ou estoque."""
    if vendas and hasattr(vendas, "buscar_produto"):
        r = vendas.buscar_produto(nome)
        if not r:
            return f"Produto '{nome}' nao encontrado."
        return f"Produto: {r.get('nome', nome)} | Preco: {r.get('preco')} | Estoque: {r.get('estoque')}"
    return f"Produto '{nome}' - vendas.py nao tem funcao buscar_produto ainda. Verifica no AGENTS.md"

@mcp.tool()
def criar_pedido(produto: str, cliente_id: str) -> str:
    """Cria pedido. NUNCA mande CPF ou nome do cliente, so o ID."""
    if vendas and hasattr(vendas, "criar_pedido"):
        p = vendas.criar_pedido(produto, cliente_id)
        return f"Pedido criado: {p.get('id')} | Status: {p.get('status')}"
    return f"Pedido para {produto} / cliente {cliente_id} - funcao criar_pedido nao encontrada em vendas.py"

@mcp.tool()
def verificar_pedido(pedido_id: str) -> str:
    """Verifica status de um pedido pelo ID."""
    if vendas and hasattr(vendas, "verificar_status"):
        s = vendas.verificar_status(pedido_id)
        return f"Pedido {pedido_id}: {s}"
    return f"Pedido {pedido_id} - funcao verificar_status nao encontrada em vendas.py"

@mcp.tool()
def chamar_medico(problema: str) -> str:
    """Chama o medico (Claude) quando tem bug ou produto sumido. Nao mande dados do cliente."""
    try:
        from medico import chamar_medico_claude
        return chamar_medico_claude(problema)
    except Exception as e:
        return f"Medico nao disponivel agora: {e}. Verifica se ANTHROPIC_API_KEY esta no Environment do Render."

if __name__ == "__main__":
    mcp.run()
