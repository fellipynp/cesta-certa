import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# A URL do banco vem de variável de ambiente (nunca fica no código).
# Sem a variável, usa um SQLite local, só para desenvolvimento.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cesta_certa.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Abre uma sessão do banco por requisição e a fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
