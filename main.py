from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Configura CORS para frontend GitHub Pages
origins = [
    "https://anbeatrizduarte.github.io",
    "http://localhost:5173",  # opcional, teste local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class User(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# Banco de dados fake (apenas para exemplo)
fake_users_db = {}

# Rota raiz
@app.get("/")
async def root():
    return {"message": "Backend LetterPlay está funcionando!"}

# Cadastro de usuário
@app.post("/users/")
async def register_user(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    fake_users_db[user.username] = user.dict()
    return {"message": "Usuário registrado com sucesso", "user": user.dict()}

# Perfil do usuário (exemplo simplificado)
@app.get("/users/me/")
async def get_user_profile(username: str = "biaateste"):
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

# Upload de foto de perfil
@app.patch("/users/me/upload-pictures/")
async def upload_profile_picture(profile_pic: UploadFile = File(...)):
    # apenas retorna o nome do arquivo, sem salvar
    return {"filename": profile_pic.filename, "message": "Foto enviada com sucesso"}

# Atualizar usuário
@app.patch("/users/atualizar/{user_id}/")
async def update_user(user_id: str, dados: UserUpdate):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    update_data = dados.dict(exclude_unset=True)
    user.update(update_data)
    fake_users_db[user_id] = user
    return {"user_id": user_id, "updated": user}

# Login via token
@app.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    return {"access_token": f"fake-token-for-{user['username']}", "token_type": "bearer"}
