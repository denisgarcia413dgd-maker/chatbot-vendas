from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()

@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

api_router = APIRouter(prefix="/api")

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Novo modelo para credenciais do Mercado Livre
class MeliCredentialsUpdate(BaseModel):
    client_id: str
    client_secret: str

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# --- NOVAS ROTAS PARA O MERCADO LIVRE ---
@api_router.post("/config/mercadolivre")
async def update_meli_config(credentials: MeliCredentialsUpdate):
    # Atualiza ou armazena as chaves de integração do Mercado Livre no banco de dados
    await db.integrations.update_one(
        {"platform": "mercadolivre"},
        {"$set": {"client_id": credentials.client_id, "client_secret": credentials.client_secret, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"status": "success", "message": "Credenciais do Mercado Livre salvas."}

@api_router.get("/config/mercadolivre/status")
async def get_meli_status():
    integration = await db.integrations.find_one({"platform": "mercadolivre"})
    if integration:
        return {"connected": True, "client_id": integration.get("client_id", "")}
    return {"connected": False, "client_id": ""}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
