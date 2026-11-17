FAMILIA = {
    "nome_responsavel": "Ana Exemplo",
    "telefone": "61900000001",
    "endereco": "Rua Demo 1, Centro Demo",
    "qtd_pessoas": 4,
}


def test_cadastro_valido_cria_familia(client, cabecalho):
    r = client.post("/familias", headers=cabecalho, json=FAMILIA)
    assert r.status_code == 201
    assert r.json()["nome_responsavel"] == "Ana Exemplo"


def test_cadastro_duplicado_e_bloqueado(client, cabecalho):
    client.post("/familias", headers=cabecalho, json=FAMILIA)
    r = client.post("/familias", headers=cabecalho, json=FAMILIA)
    assert r.status_code == 409


def test_telefone_invalido_e_recusado(client, cabecalho):
    dados = {**FAMILIA, "telefone": "abc"}
    r = client.post("/familias", headers=cabecalho, json=dados)
    assert r.status_code == 422


def test_numero_de_pessoas_zero_e_recusado(client, cabecalho):
    dados = {**FAMILIA, "qtd_pessoas": 0}
    r = client.post("/familias", headers=cabecalho, json=dados)
    assert r.status_code == 422


def test_busca_encontra_familia_pelo_nome(client, cabecalho):
    client.post("/familias", headers=cabecalho, json=FAMILIA)
    r = client.get("/familias", headers=cabecalho, params={"busca": "Ana"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["status_mes"] == "pendente"


def test_injecao_de_sql_na_busca_nao_retorna_dados(client, cabecalho):
    client.post("/familias", headers=cabecalho, json=FAMILIA)
    r = client.get("/familias", headers=cabecalho, params={"busca": "' OR '1'='1"})
    assert r.status_code == 200
    assert r.json() == []
