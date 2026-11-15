import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import vendas

app = FastAPI(
    title="Robô Inteligente de Dropshipping",
    description="Sistema de monitoramento de cenário e automação para Marketplaces"
)

# Libera o acesso para a tela do aplicativo no seu Samsung A12
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas inteligentes do arquivo vendas.py
app.include_router(vendas.router)

@app.get("/")
async def raiz():
    return {"mensagem": "Robô online no Samsung A12!"}

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run("aplicativo:app", host="0.0.0.0", port=porta)

