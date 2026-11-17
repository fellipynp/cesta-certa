
"""Dados fictícios opcionais para demonstração. Ative apenas em ambiente de teste."""
import os
from datetime import date, timedelta

from .database import SessionLocal
from .models import Familia, ItemEstoque, Usuario
from .security import gerar_hash


def carregar_dados_demo():
    if os.getenv("DEMO_MODE", "false").lower() != "true":
        return

    email = os.getenv("DEMO_EMAIL", "maria@cestacerta.com")
    senha = os.getenv("DEMO_PASSWORD", "Maria123!")
    db = SessionLocal()

    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()

        if usuario is None:
            usuario = Usuario(
                nome="Maria",
                email=email,
                senha_hash=gerar_hash(senha),
                perfil="coordenador",
            )
            db.add(usuario)
        else:
            usuario.nome = "Maria"
            usuario.senha_hash = gerar_hash(senha)
            usuario.perfil = "coordenador"
            usuario.ativo = True
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate = None

        if db.query(Familia).count() == 0:
            db.add_all([
                Familia(nome_responsavel="Ana Souza", telefone="61999990001",
                        endereco="Rua das Flores, 120", qtd_pessoas=4),
                Familia(nome_responsavel="João Oliveira", telefone="61999990002",
                        endereco="Qd. 10, Casa 5", qtd_pessoas=3),
                Familia(nome_responsavel="Carla Santos", telefone="61999990003",
                        endereco="Rua do Sol, 45", qtd_pessoas=5),
                Familia(nome_responsavel="Pedro Lima", telefone="61999990004",
                        endereco="Av. Central, 300", qtd_pessoas=2),
            ])

        if db.query(ItemEstoque).count() == 0:
            db.add_all([
                ItemEstoque(nome_produto="Arroz 5 kg", unidade="pacote",
                            quantidade_atual=12, data_validade=date.today()+timedelta(days=10)),
                ItemEstoque(nome_produto="Feijão 1 kg", unidade="pacote",
                            quantidade_atual=20, data_validade=date.today()+timedelta(days=45)),
                ItemEstoque(nome_produto="Óleo 900 ml", unidade="unidade",
                            quantidade_atual=8, data_validade=date.today()+timedelta(days=7)),
            ])

        db.commit()
    finally:
        db.close()
