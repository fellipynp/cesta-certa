from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .erros import ErroRegra
from .models import Entrega, Familia


def registrar_entrega(
    db: Session, id_familia: int, id_usuario: int, hoje: date | None = None
) -> Entrega:
    """Registra a cesta do mês: no máximo uma entrega por família por mês."""
    hoje = hoje or date.today()

    familia = db.get(Familia, id_familia)
    if familia is None or not familia.ativa:
        raise ErroRegra(404, "Família não encontrada.")

    mes = hoje.strftime("%Y-%m")
    anterior = (
        db.query(Entrega)
        .filter(Entrega.id_familia == id_familia, Entrega.mes_referencia == mes)
        .first()
    )
    if anterior:
        data = anterior.data_entrega.strftime("%d/%m/%Y")
        raise ErroRegra(409, f"Esta família já recebeu a cesta em {data}.")

    entrega = Entrega(
        id_familia=id_familia,
        id_usuario=id_usuario,
        data_entrega=hoje,
        mes_referencia=mes,
    )
    db.add(entrega)
    try:
        db.commit()
    except IntegrityError:
        # Segunda barreira: a restrição única do banco também impede a duplicidade.
        db.rollback()
        raise ErroRegra(409, "Esta família já recebeu a cesta neste mês.")
    db.refresh(entrega)
    return entrega
