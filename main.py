from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

# Importando nossos módulos locais (que criamos nos passos anteriores)
from database import get_db, engine, Base
from models import User

app = FastAPI()

# --- Configuração CORS (Para seu Frontend GitHub Pages funcionar) ---
origins = [
    "https://anbeatrizduarte.github.io",
    "http://localhost:5173",  # Para testes locais
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inicialização do Banco de Dados ---
@app.on_event("startup")
async def startup():
    # Cria as tabelas automaticamente se não existirem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Modelos Pydantic (Validação de dados que entram e saem) ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_pic_url: Optional[str] = None
    
    class Config:
        from_attributes = True # Permite converter do modelo SQLAlchemy

# --- Rotas da API ---

@app.get("/")
async def root():
    return {"message": "Backend LetterPlay está online e conectado ao PostgreSQL!"}

# 1. Cadastro de Usuário (Salvando no Banco)
@app.post("/users/", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verifica se usuário ou email já existem
    query = select(User).where((User.username == user.username) | (User.email == user.email))
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário ou email já cadastrado")

    # Cria novo usuário
    new_user = User(
        username=user.username,
        email=user.email,
        password=user.password # Dica: Em produção, use hash (bcrypt) aqui!
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# 2. Perfil do Usuário
# Mantive o default="biaateste" para compatibilidade com seu frontend atual,
# mas o ideal é o frontend enviar o username ou um token.
@app.get("/users/me/", response_model=UserResponse)
async def get_user_profile(username: str = "biaateste", db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

# 3. Upload de Foto de Perfil
@app.patch("/users/me/upload-pictures/")
async def upload_profile_picture(profile_pic: UploadFile = File(...)):
    # O Render apaga arquivos locais após 15min ou restart. 
    # Para produção real, você precisaria enviar para AWS S3 ou Cloudinary.
    return {
        "filename": profile_pic.filename, 
        "message": "Foto recebida (Aviso: No Render gratuito, arquivos locais são temporários!)"
    }

# 4. Atualizar Usuário
@app.patch("/users/atualizar/{user_id}/")
async def update_user(user_id: int, dados: UserUpdate, db: AsyncSession = Depends(get_db)):
    # Busca o usuário pelo ID
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza apenas os campos que foram enviados
    if dados.username:
        user.username = dados.username
    if dados.email:
        user.email = dados.email
    if dados.password:
        user.password = dados.password
    
    await db.commit()
    await db.refresh(user)
    return {"message": "Usuário atualizado com sucesso", "user": user}

# 5. Login (Autenticação)
@app.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Busca usuário no banco pelo username
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    # Verifica se usuário existe e a senha bate
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    return {
        "access_token": f"token-falso-para-{user.username}", 
        "token_type": "bearer",
        "user_id": user.id # Retornar o ID ajuda o frontend
    }

# Para rodar localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
