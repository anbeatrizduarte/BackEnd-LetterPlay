# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Pega a URL do Render. Se não achar, usa um SQLite local temporário para testes
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./watchlist.db")

# Correção necessária para o Render (Postgres)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Dependência para injetar o banco nas rotas
async def get_db():
    async with SessionLocal() as session:
        yield session
