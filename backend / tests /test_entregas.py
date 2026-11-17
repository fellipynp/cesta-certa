from datetime import date

import pytest

from app.database import SessionLocal
from app.erros import ErroRegra
from app.models import Usuario
from app.service_entregas import registrar_entrega

FAMILIA = {
    "nome_responsavel": "Ana Exemplo",
    "telefone": "61900000001",
    "endereco": "Rua Demo 1, Centro Demo",
    "qtd_pessoas": 4,
}


def criar_familia(client, cabecalho):
    return client.post("/familias", headers=cabecalho, json=FAMILIA).json()["id_familia"]


def test_primeira_entrega_do_mes_e_registrada(client, cabecalho):
    id_familia = criar_familia(client, cabecalho)
    r = client.post("/entregas", headers=cabecalho, json={"id_familia": id_familia})
    assert r.status_code == 201


def test_segunda_entrega_no_mesmo_mes_retorna_409_com_a_data_anterior(client, cabecalho):
    id_familia = criar_familia(client, cabecalho)
    client.post("/entregas", headers=cabecalho, json={"id_familia": id_familia})
    r = client.post("/entregas", headers=cabecalho, json={"id_familia": id_familia})
    assert r.status_code == 409
    assert date.today().strftime("%d/%m/%Y") in r.json()["detail"]


def test_status_da_familia_muda_para_recebeu_apos_a_entrega(client, cabecalho):
    id_familia = criar_familia(client, cabecalho)
    client.post("/entregas", headers=cabecalho, json={"id_familia": id_familia})
    r = client.get("/familias", headers=cabecalho)
    assert r.json()[0]["status_mes"] == "recebeu"


def test_entrega_sem_login_e_recusada(client):
    r = client.post("/entregas", json={"id_familia": 1})
    assert r.status_code == 401


def test_familia_inexistente_retorna_404(client, cabecalho):
    r = client.post("/entregas", headers=cabecalho, json={"id_familia": 9999})
    assert r.status_code == 404


def test_mes_seguinte_libera_nova_entrega(client, cabecalho):
    id_familia = criar_familia(client, cabecalho)
    db = SessionLocal()
    id_usuario = db.query(Usuario).first().id_usuario

    registrar_entrega(db, id_familia, id_usuario, hoje=date(2026, 10, 10))
    registrar_entrega(db, id_familia, id_usuario, hoje=date(2026, 11, 10))
    with pytest.raises(ErroRegra):
        registrar_entrega(db, id_familia, id_usuario, hoje=date(2026, 11, 20))
    db.close()
