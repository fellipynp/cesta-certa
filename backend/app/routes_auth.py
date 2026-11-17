from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import get_db
from .deps import apenas_coordenador
from .models import Usuario
from .security import criar_token, gerar_hash, verificar_senha

router = APIRouter(tags=["acesso"])

MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
ERRO_LOGIN = "E-mail ou senha incorretos."  # mesma mensagem para qualquer falha


class LoginEntrada(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    senha: str = Field(min_length=1, max_length=72)


class UsuarioEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=120)
    senha: str = Field(min_length=8, max_length=72)
    perfil: str = Field(pattern="^(coordenador|voluntario)$")


@router.post("/login")
def login(dados: LoginEntrada, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    agora = datetime.now()

    if usuario and usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
        raise HTTPException(status_code=401, detail=ERRO_LOGIN)

    senha_ok = (
        usuario is not None
        and usuario.ativo
        and verificar_senha(dados.senha, usuario.senha_hash)
    )
    if not senha_ok:
        if usuario is not None:
            usuario.tentativas_falhas += 1
            if usuario.tentativas_falhas >= MAX_TENTATIVAS:
                usuario.bloqueado_ate = agora + timedelta(minutes=BLOQUEIO_MINUTOS)
                usuario.tentativas_falhas = 0
            db.commit()
        raise HTTPException(status_code=401, detail=ERRO_LOGIN)

    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    db.commit()
    return {
        "access_token": criar_token(usuario.id_usuario, usuario.perfil),
        "token_type": "bearer",
    }


@router.post("/usuarios", status_code=201)
def criar_usuario(
    dados: UsuarioEntrada,
    db: Session = Depends(get_db),
    _: Usuario = Depends(apenas_coordenador),
):
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash(dados.senha),
        perfil=dados.perfil,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"id_usuario": novo.id_usuario, "nome": novo.nome, "perfil": novo.perfil}
