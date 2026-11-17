from fastapi import FastAPI

from . import models  # noqa: F401  (registra as tabelas)
from .database import Base, engine
from .routes_auth import router as rotas_acesso

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cesta Certa")
app.include_router(rotas_acesso)


@app.get("/saude")
def saude():
    """Rota simples para verificar se a API está no ar."""
    return {"status": "ok"}
