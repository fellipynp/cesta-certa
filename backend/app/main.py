from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import models  # noqa: F401  (registra as tabelas)
from .database import Base, engine
from .erros import ErroRegra
from .routes_auth import router as rotas_acesso
from .routes_entregas import router as rotas_entregas
from .routes_familias import router as rotas_familias

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cesta Certa")
app.include_router(rotas_acesso)
app.include_router(rotas_familias)
app.include_router(rotas_entregas)


@app.exception_handler(ErroRegra)
async def tratar_erro_regra(request, exc: ErroRegra):
    """Devolve erros de regra de negócio com mensagem clara e sem detalhes técnicos."""
    return JSONResponse(status_code=exc.status, content={"detail": exc.mensagem})


@app.get("/saude")
def saude():
    """Rota simples para verificar se a API está no ar."""
    return {"status": "ok"}
