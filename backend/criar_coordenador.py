"""Cria o primeiro usuário coordenador.

Uso: defina COORD_EMAIL e COORD_SENHA no ambiente e execute
    python criar_coordenador.py
"""
import os

from app import models  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.models import Usuario
from app.security import gerar_hash


def main():
    email = os.getenv("COORD_EMAIL")
    senha = os.getenv("COORD_SENHA")
    if not email or not senha or len(senha) < 8:
        raise SystemExit("Defina COORD_EMAIL e COORD_SENHA (mínimo de 8 caracteres).")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.email == email).first():
            raise SystemExit("Este e-mail já está cadastrado.")
        db.add(
            Usuario(
                nome="Coordenação",
                email=email,
                senha_hash=gerar_hash(senha),
                perfil="coordenador",
            )
        )
        db.commit()
        print("Coordenador criado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
