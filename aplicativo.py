import uvicorn
from fastapi import FastAPI
import apirouterpost

app = FastAPI(
    title="Robô Inteligente de Dropshipping",
    description="Sistema de monitoramento de cenário e automação para Marketplaces"
)

# Inclui as rotas inteligentes criadas no arquivo apirouterpost
app.include_router(apirouterpost.router)

@app.get("/")
async def raiz():
    return {"mensagem": "Robô online. Aguardando gatilhos de checagem de cenário."}

if __name__ == "__main__":
    # Inicia o servidor local. Para testar, acesse no navegador: http://127.0.0
    uvicorn.run("aplicativo:app", host="127.0.0.1", port=8000, reload=True)
