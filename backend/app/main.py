from fastapi import FastAPI

app = FastAPI(title="Cesta Certa")


@app.get("/saude")
def saude():
    """Rota simples para verificar se a API está no ar."""
    return {"status": "ok"}
