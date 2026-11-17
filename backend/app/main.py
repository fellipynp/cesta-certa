from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import models  # noqa: F401  (registra as tabelas)
from .database import Base, engine
from .demo_data import carregar_dados_demo
from .erros import ErroRegra
from .routes_auth import router as rotas_acesso
from .routes_entregas import router as rotas_entregas
from .routes_familias import router as rotas_familias
from .routes_painel import router as rotas_painel

Base.metadata.create_all(bind=engine)
carregar_dados_demo()

app = FastAPI(title="Cesta Certa")
pasta_static = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=pasta_static), name="static")
app.include_router(rotas_acesso)
app.include_router(rotas_familias)
app.include_router(rotas_entregas)
app.include_router(rotas_painel)


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(pasta_static / "index.html")


@app.exception_handler(ErroRegra)
async def tratar_erro_regra(request, exc: ErroRegra):
    """Devolve erros de regra de negócio com mensagem clara e sem detalhes técnicos."""
    return JSONResponse(status_code=exc.status, content={"detail": exc.mensagem})


@app.get("/saude")
def saude():
    """Rota simples para verificar se a API está no ar."""
    return {"status": "ok"}
