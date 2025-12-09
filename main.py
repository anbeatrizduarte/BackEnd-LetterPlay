# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Importar nossos novos arquivos
from database import get_db, engine, Base
import models

app = FastAPI()

# Criar tabelas ao iniciar (útil para testes rápidos, mas ideal é usar Alembic)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Configura CORS (Mantenha o seu original)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anbeatrizduarte.github.io", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seus Schemas Pydantic (Mantidos do seu código)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_pic_url: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- ROTAS ATUALIZADAS PARA USAR O BANCO REAL ---

@app.get("/")
async def root():
    return {"message": "API Conectada ao Banco de Dados!"}

@app.post("/users/", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verificar se usuário já existe
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    # Criar novo usuário no Banco
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password # Em produção, use hash da senha!
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.get("/users/me/", response_model=UserResponse)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    # Buscar no banco ao invés do dicionário
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
