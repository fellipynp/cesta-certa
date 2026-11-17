from fastapi import FastAPI

from . import models  # noqa: F401  (registra as tabelas)
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cesta Certa")


@app.get("/saude")
def saude():
    """Rota simples para verificar se a API está no ar."""
    return {"status": "ok"}
