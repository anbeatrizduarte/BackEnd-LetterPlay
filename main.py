from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Configura CORS para o frontend GitHub Pages
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

# Models
class User(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    password: str = None

# Rotas
@app.post("/users/")
async def register_user(user: User):
    # lógica de salvar usuário
    return {"message": "Usuário registrado com sucesso", "user": user.dict()}

@app.get("/users/me/")
async def get_user_profile():
    # lógica para retornar usuário logado
    return {"username": "Beatriz", "email": "beatriz@example.com"}

@app.patch("/users/me/upload-pictures/")
async def upload_profile_picture(profile_pic: UploadFile = File(...)):
    # lógica para salvar a foto
    return {"filename": profile_pic.filename, "message": "Foto enviada com sucesso"}

@app.patch("/users/atualizar/{user_id}/")
async def update_user(user_id: int, dados: UserUpdate):
    # lógica para atualizar usuário
    return {"user_id": user_id, "updated": dados.dict()}
