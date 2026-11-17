import os

# Define o banco de teste ANTES de importar a aplicação,
# para nunca tocar no banco de verdade.
os.environ["DATABASE_URL"] = "sqlite:///./teste_pytest.db"
os.environ["SECRET_KEY"] = "chave-apenas-para-testes"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Usuario  # noqa: E402
from app.security import gerar_hash  # noqa: E402


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria as tabelas vazias antes de cada teste."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def criar_usuario():
    def _criar(email, senha, perfil="coordenador"):
        db = SessionLocal()
        db.add(
            Usuario(
                nome="Usuário de Teste",
                email=email,
                senha_hash=gerar_hash(senha),
                perfil=perfil,
            )
        )
        db.commit()
        db.close()

    return _criar


@pytest.fixture
def cabecalho(client, criar_usuario):
    """Cabeçalho de acesso de um coordenador logado."""
    criar_usuario("coord@teste.com", "senha-de-teste-1")
    resposta = client.post(
        "/login", json={"email": "coord@teste.com", "senha": "senha-de-teste-1"}
    )
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}
