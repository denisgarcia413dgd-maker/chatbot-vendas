import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import vendas

app = FastAPI(
    title="Robo Inteligente de Dropshipping",
    description="Sistema de monitoramento de cenario e automacao para Marketplaces"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vendas.router)

@app.get("/")
async def raiz():
    return FileResponse("index.html")

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run("aplicativo:app", host="0.0.0.0", port=porta)


