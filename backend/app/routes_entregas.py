from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import get_db
from .deps import usuario_logado
from .models import Usuario
from .service_entregas import registrar_entrega

router = APIRouter(tags=["entregas"])


class EntregaEntrada(BaseModel):
    id_familia: int = Field(gt=0)


@router.post("/entregas", status_code=201)
def criar_entrega(
    dados: EntregaEntrada,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_logado),
):
    # O responsável vem do token, nunca de um campo enviado pelo cliente.
    entrega = registrar_entrega(db, dados.id_familia, usuario.id_usuario)
    return {
        "id_entrega": entrega.id_entrega,
        "id_familia": entrega.id_familia,
        "data_entrega": entrega.data_entrega.strftime("%d/%m/%Y"),
    }
