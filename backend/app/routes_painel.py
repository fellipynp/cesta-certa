from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import get_db
from .deps import usuario_logado
from .models import Entrega, Familia, ItemEstoque, Movimentacao, Usuario

router = APIRouter(tags=["painel"])


@router.get("/painel/resumo")
def resumo_painel(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_logado),
):
    hoje = date.today()
    mes = hoje.strftime("%Y-%m")
    total = db.query(func.count(Familia.id_familia)).filter(Familia.ativa.is_(True)).scalar() or 0
    entregues = (
        db.query(func.count(Entrega.id_entrega))
        .filter(Entrega.mes_referencia == mes)
        .scalar()
        or 0
    )
    descartados = (
        db.query(func.coalesce(func.sum(Movimentacao.quantidade), 0))
        .filter(
            Movimentacao.tipo == "descarte",
            func.strftime("%Y-%m", Movimentacao.data_hora) == mes,
        )
        .scalar()
        or 0
    )
    return {
        "mes": hoje.strftime("%m/%Y"),
        "total_familias": total,
        "familias_atendidas": entregues,
        "familias_pendentes": max(total - entregues, 0),
        "percentual": round(entregues * 100 / total) if total else 0,
        "cestas_entregues": entregues,
        "itens_descartados": int(descartados),
    }


@router.get("/estoque/alertas")
def alertas_estoque(
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_logado),
):
    hoje = date.today()
    limite = hoje + timedelta(days=15)
    itens = (
        db.query(ItemEstoque)
        .filter(
            ItemEstoque.ativo.is_(True),
            ItemEstoque.quantidade_atual > 0,
            ItemEstoque.data_validade >= hoje,
            ItemEstoque.data_validade <= limite,
        )
        .order_by(ItemEstoque.data_validade)
        .all()
    )
    return [
        {
            "id_item": item.id_item,
            "nome_produto": item.nome_produto,
            "unidade": item.unidade,
            "quantidade": item.quantidade_atual,
            "data_validade": item.data_validade.strftime("%d/%m/%Y"),
            "dias_restantes": (item.data_validade - hoje).days,
        }
        for item in itens
    ]
