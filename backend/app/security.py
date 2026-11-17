import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# A chave vem de variável de ambiente. Nunca escreva a chave real no código.
SECRET_KEY = os.getenv("SECRET_KEY", "chave-apenas-para-desenvolvimento")
ALGORITHM = "HS256"
EXPIRA_MINUTOS = 30


def gerar_hash(senha: str) -> str:
    """Guarda a senha apenas como hash bcrypt, com salt individual."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token(id_usuario: int, perfil: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_MINUTOS)
    dados = {"sub": str(id_usuario), "perfil": perfil, "exp": expira}
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def ler_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
