from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .erros import ErroRegra
from .models import Entrega, Familia

MSG_DUPLICADA = "Já existe uma família cadastrada com este responsável e telefone."


def cadastrar_familia(db: Session, dados: dict) -> Familia:
    existente = (
        db.query(Familia)
        .filter(
            Familia.nome_responsavel == dados["nome_responsavel"],
            Familia.telefone == dados["telefone"],
        )
        .first()
    )
    if existente:
        raise ErroRegra(409, MSG_DUPLICADA)
    familia = Familia(**dados)
    db.add(familia)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErroRegra(409, MSG_DUPLICADA)
    db.refresh(familia)
    return familia


def listar_familias(db: Session, busca: str, mes_referencia: str) -> list[dict]:
    """Lista famílias ativas, com o status de entrega no mês."""
    consulta = db.query(Familia).filter(Familia.ativa.is_(True))
    if busca:
        consulta = consulta.filter(Familia.nome_responsavel.ilike(f"%{busca}%"))
    familias = consulta.order_by(Familia.nome_responsavel).limit(50).all()

    entregas = {
        e.id_familia: e
        for e in db.query(Entrega).filter(Entrega.mes_referencia == mes_referencia)
    }
    resultado = []
    for f in familias:
        entrega = entregas.get(f.id_familia)
        resultado.append(
            {
                "id_familia": f.id_familia,
                "nome_responsavel": f.nome_responsavel,
                "endereco": f.endereco,
                "status_mes": "recebeu" if entrega else "pendente",
                "data_entrega": entrega.data_entrega.strftime("%d/%m/%Y")
                if entrega
                else None,
            }
        )
    return resultado
