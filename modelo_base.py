from pydantic import BaseModel, HttpUrl

class ProdutoMonitorado(BaseModel):
    id_anuncio_meu: str       # ID do seu anúncio no Mercado Livre / Shopee
    link_fornecedor: HttpUrl   # Link do produto no fornecedor
    preco_custo_atual: float   # O último preço de custo que você registrou
    markup: float              # Margem multiplicadora (ex: 1.4 = 40% de lucro/taxas)
