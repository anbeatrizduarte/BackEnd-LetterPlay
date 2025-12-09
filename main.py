from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cria o app FastAPI
app = FastAPI()

# Lista de origens permitidas (seu frontend GitHub Pages)
origins = [
    "https://anbeatrizduarte.github.io",  # seu frontend
    "http://localhost:5173",              # opcional, para testes locais
]

# Middleware para permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # quem pode acessar
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, PUT, DELETE...
    allow_headers=["*"],         # headers
)

# Exemplo de rota
@app.get("/users/me")
async def read_users_me():
    return {"user": "Beatriz"}

# Outras rotas do seu backend...
# @app.post("/users/") ...
# @app.get("/outra-rota/") ...
