import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# 1. Pega a URL do Render.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./watchlist.db")

# 2. CORREÇÃO ROBUSTA PARA O DRIVER ASSÍNCRONO
# Garante que usamos 'postgresql+asyncpg://' não importa como o Render entregue a URL
if "postgres" in DATABASE_URL:
    # Remove qualquer prefixo existente incorreto e força o correto
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Cria o motor de conexão
# 'check_same_thread' é apenas para SQLite, removemos se for Postgres
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args=connect_args
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
