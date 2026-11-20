import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import vendas

app = FastAPI(title="Robo Inteligente de Dropshipping")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vendas.router)

@app.get("/")
async def raiz():
    return {"status": "online", "robo": "Robo de Vendas ligado"}

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run("aplicativo:app", host="0.0.0.0", port=porta)


