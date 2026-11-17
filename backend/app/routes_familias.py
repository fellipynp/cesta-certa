from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import get_db
from .deps import usuario_logado
from .models import Usuario
from .service_familias import cadastrar_familia, listar_familias

router = APIRouter(tags=["familias"])


class FamiliaEntrada(BaseModel):
    nome_responsavel: str = Field(min_length=2, max_length=120)
    telefone: str = Field(pattern=r"^\d{10,11}$")  # só dígitos, com DDD
    endereco: str = Field(min_length=3, max_length=200)
    qtd_pessoas: int = Field(gt=0, le=30)


@router.post("/familias", status_code=201)
def criar_familia(
    dados: FamiliaEntrada,
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_logado),
):
    familia = cadastrar_familia(db, dados.model_dump())
    return {"id_familia": familia.id_familia, "nome_responsavel": familia.nome_responsavel}


@router.get("/familias")
def buscar_familias(
    busca: str = "",
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_logado),
):
    mes = date.today().strftime("%Y-%m")
    return listar_familias(db, busca.strip()[:60], mes)
