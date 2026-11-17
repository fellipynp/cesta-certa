from app.database import SessionLocal
from app.models import Usuario


def test_login_valido_retorna_token(client, criar_usuario):
    criar_usuario("a@teste.com", "senha-correta-1")
    r = client.post("/login", json={"email": "a@teste.com", "senha": "senha-correta-1"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_com_senha_errada_e_recusado(client, criar_usuario):
    criar_usuario("a@teste.com", "senha-correta-1")
    r = client.post("/login", json={"email": "a@teste.com", "senha": "senha-errada"})
    assert r.status_code == 401
    assert r.json()["detail"] == "E-mail ou senha incorretos."


def test_email_inexistente_tem_a_mesma_mensagem(client):
    r = client.post("/login", json={"email": "nao@existe.com", "senha": "qualquer-1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "E-mail ou senha incorretos."


def test_conta_e_bloqueada_apos_cinco_falhas(client, criar_usuario):
    criar_usuario("a@teste.com", "senha-correta-1")
    for _ in range(5):
        r = client.post("/login", json={"email": "a@teste.com", "senha": "errada"})
        assert r.status_code == 401
    # Mesmo com a senha certa, a conta fica bloqueada por 15 minutos.
    r = client.post("/login", json={"email": "a@teste.com", "senha": "senha-correta-1"})
    assert r.status_code == 401


def test_rota_protegida_sem_token_e_recusada(client):
    assert client.get("/familias").status_code == 401


def test_token_invalido_e_recusado(client):
    r = client.get("/familias", headers={"Authorization": "Bearer token-falso"})
    assert r.status_code == 401


def test_voluntario_nao_cria_usuario(client, criar_usuario):
    criar_usuario("v@teste.com", "senha-voluntario-1", perfil="voluntario")
    login = client.post(
        "/login", json={"email": "v@teste.com", "senha": "senha-voluntario-1"}
    )
    cabecalho = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.post(
        "/usuarios",
        headers=cabecalho,
        json={
            "nome": "Novo Usuário",
            "email": "novo@teste.com",
            "senha": "outra-senha-123",
            "perfil": "voluntario",
        },
    )
    assert r.status_code == 403


def test_senha_e_guardada_apenas_como_hash(criar_usuario):
    criar_usuario("h@teste.com", "senha-correta-1")
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == "h@teste.com").first()
    db.close()
    assert usuario.senha_hash != "senha-correta-1"
    assert usuario.senha_hash.startswith("$2")  # prefixo do bcrypt
