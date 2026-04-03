"""Serviço de busca e listagem de produtos."""

import hashlib
import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.cache import cache_get, cache_set
from app.models.produto import Preco, Produto
from app.schemas.produto import BuscaParams, PaginacaoOut, ProdutoOut


def _escape_like(value: str) -> str:
    """Escapa caracteres especiais do LIKE/ILIKE (%, _)."""
    return value.replace("%", r"\%").replace("_", r"\_")


def _cache_key(params: BuscaParams) -> str:
    """Gera chave de cache determinística a partir dos filtros."""
    raw = params.model_dump_json(exclude_none=True)
    return f"busca:{hashlib.sha256(raw.encode()).hexdigest()}"


def _aplicar_filtros(query, params: BuscaParams):
    """Aplica filtros incrementalmente à query."""
    needs_preco_join = (
        params.em_promocao
        or params.preco_min is not None
        or params.preco_max is not None
    )
    if needs_preco_join:
        query = query.join(Preco, isouter=True)

    if params.q:
        query = query.where(
            Produto.nome.ilike(f"%{_escape_like(params.q)}%")
        )
    if params.tipo:
        query = query.where(Produto.tipo == params.tipo)
    if params.subtipo:
        query = query.where(Produto.subtipo == params.subtipo)
    if params.marca:
        query = query.where(
            Produto.marca.ilike(f"%{_escape_like(params.marca)}%")
        )
    if params.em_promocao:
        query = query.where(Preco.em_promocao.is_(True))
    if params.preco_min is not None:
        query = query.where(Preco.valor >= params.preco_min)
    if params.preco_max is not None:
        query = query.where(Preco.valor <= params.preco_max)
    return query


async def buscar_produtos(db: AsyncSession, params: BuscaParams) -> PaginacaoOut:
    """Busca produtos com filtros, cache e paginação."""
    key = _cache_key(params)
    cached = await cache_get(key)
    if cached:
        return PaginacaoOut(**cached)

    # Contagem
    count_q = select(func.count(func.distinct(Produto.id))).select_from(Produto)
    count_q = _aplicar_filtros(count_q, params)
    total = (await db.execute(count_q)).scalar_one()

    # Busca paginada
    offset = (params.pagina - 1) * params.por_pagina
    query = (
        select(Produto)
        .options(joinedload(Produto.precos).joinedload(Preco.loja))
    )
    query = _aplicar_filtros(query, params)
    query = query.offset(offset).limit(params.por_pagina)

    result = await db.execute(query)
    produtos = result.unique().scalars().all()

    items = []
    for p in produtos:
        menor = min(p.precos, key=lambda x: x.valor, default=None)
        items.append(ProdutoOut.model_validate(
            p,
            update={
                "menor_preco": float(menor.valor) if menor else None,
                "loja_menor_preco": menor.loja.nome if menor else None,
            },
        ))

    paginas = math.ceil(total / params.por_pagina) if total else 0
    resultado = PaginacaoOut(items=items, total=total, pagina=params.pagina, paginas=paginas)

    await cache_set(key, resultado.model_dump())
    return resultado


async def obter_produto(db: AsyncSession, produto_id: int) -> Produto | None:
    """Retorna produto com todos os preços carregados."""
    query = (
        select(Produto)
        .options(joinedload(Produto.precos).joinedload(Preco.loja))
        .where(Produto.id == produto_id)
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()
