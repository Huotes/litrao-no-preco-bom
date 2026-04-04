"""Serviço de busca e listagem de produtos.

Princípios: DRY, KISS, Single Responsibility.
Busca usa PostgreSQL Full Text Search com ranking por relevância.
"""

import hashlib
import math

from sqlalchemy import func, select, text, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.cache import cache_get, cache_set
from app.models.produto import Preco, Produto
from app.schemas.produto import BuscaParams, OrdenarPor, PaginacaoOut, ProdutoOut


# ---------------------------------------------------------------------------
# Helpers privados (DRY)
# ---------------------------------------------------------------------------


def _cache_key(params: BuscaParams) -> str:
    """Gera chave de cache determinística."""
    raw = params.model_dump_json(exclude_none=True)
    return f"busca:{hashlib.sha256(raw.encode()).hexdigest()}"


def _build_fts_condition(termo: str):
    """Constrói condição Full Text Search com unaccent.

    Suporta múltiplas palavras (AND) e prefixo (:*) para autocomplete.
    """
    palavras = termo.strip().split()
    tsquery_str = " & ".join(f"{p}:*" for p in palavras if p)
    return text("busca_vetor @@ to_tsquery('portuguese', unaccent(:q))").bindparams(
        q=tsquery_str
    )


def _fts_rank(termo: str):
    """Retorna expressão de ranking FTS para ordenação por relevância."""
    palavras = termo.strip().split()
    tsquery_str = " & ".join(f"{p}:*" for p in palavras if p)
    return text(
        "ts_rank_cd(busca_vetor, to_tsquery('portuguese', unaccent(:q)), 32)"
    ).bindparams(q=tsquery_str)


def _aplicar_filtros(query, params: BuscaParams):
    """Aplica filtros à query. Cada filtro é independente (KISS)."""
    if params.q:
        query = query.where(_build_fts_condition(params.q))

    if params.tipo:
        query = query.where(Produto.tipo == params.tipo)

    if params.subtipo:
        query = query.where(Produto.subtipo == params.subtipo)

    if params.marca:
        query = query.where(Produto.marca.ilike(f"%{params.marca}%"))

    if params.artesanal is not None:
        query = query.where(Produto.artesanal.is_(params.artesanal))

    # Filtros que dependem de JOIN com preço
    needs_preco = (
        params.em_promocao
        or params.preco_min is not None
        or params.preco_max is not None
    )
    if needs_preco:
        query = query.join(Preco, isouter=True)
        if params.em_promocao:
            query = query.where(Preco.em_promocao.is_(True))
        if params.preco_min is not None:
            query = query.where(Preco.valor >= params.preco_min)
        if params.preco_max is not None:
            query = query.where(Preco.valor <= params.preco_max)

    return query


def _produto_to_out(produto: Produto) -> ProdutoOut:
    """Converte model para schema de saída. Single Responsibility."""
    menor = min(produto.precos, key=lambda x: x.valor, default=None)
    return ProdutoOut(
        id=produto.id,
        nome=produto.nome,
        tipo=produto.tipo,
        subtipo=produto.subtipo,
        marca=produto.marca,
        volume_ml=produto.volume_ml,
        teor_alcoolico=(
            float(produto.teor_alcoolico) if produto.teor_alcoolico else None
        ),
        imagem_url=produto.imagem_url,
        artesanal=produto.artesanal,
        menor_preco=float(menor.valor) if menor else None,
        loja_menor_preco=menor.loja.nome if menor else None,
        url_oferta=menor.url_oferta if menor else None,
        url_redirecionamento=menor.url_redirecionamento if menor else None,
        loja_icone=menor.loja.icone if menor else None,
    )


# ---------------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------------


async def buscar_produtos(db: AsyncSession, params: BuscaParams) -> PaginacaoOut:
    """Busca produtos com FTS, filtros, cache e paginação."""
    key = _cache_key(params)
    cached = await cache_get(key)
    if cached:
        return PaginacaoOut(**cached)

    # 1) Contagem total
    count_q = select(func.count(func.distinct(Produto.id))).select_from(Produto)
    count_q = _aplicar_filtros(count_q, params)
    total = (await db.execute(count_q)).scalar_one()

    if total == 0:
        resultado = PaginacaoOut(items=[], total=0, pagina=params.pagina, paginas=0)
        await cache_set(key, resultado.model_dump(), ttl=300)
        return resultado

    # 2) IDs paginados (evita conflito joinedload + filtro JOIN)
    offset = (params.pagina - 1) * params.por_pagina
    ids_q = select(Produto.id).distinct()
    ids_q = _aplicar_filtros(ids_q, params)

    # Ordenação na query de IDs
    if params.q and params.ordenar_por == OrdenarPor.MENOR_PRECO:
        # Se tem busca textual, ordena por relevância primeiro
        ids_q = ids_q.order_by(_fts_rank(params.q).desc())
    ids_q = ids_q.offset(offset).limit(params.por_pagina)

    ids_result = await db.execute(ids_q)
    produto_ids = [row[0] for row in ids_result.all()]

    if not produto_ids:
        resultado = PaginacaoOut(items=[], total=total, pagina=params.pagina, paginas=0)
        await cache_set(key, resultado.model_dump(), ttl=300)
        return resultado

    # 3) Carrega produtos completos com preços e lojas
    query = (
        select(Produto)
        .where(Produto.id.in_(produto_ids))
        .options(joinedload(Produto.precos).joinedload(Preco.loja))
    )
    result = await db.execute(query)
    produtos = result.unique().scalars().all()

    items = [_produto_to_out(p) for p in produtos]

    # 4) Ordenação final (client-side da página)
    sort_map = {
        OrdenarPor.MENOR_PRECO: lambda x: x.menor_preco or 999999,
        OrdenarPor.MAIOR_PRECO: lambda x: -(x.menor_preco or 0),
        OrdenarPor.NOME: lambda x: x.nome.lower(),
    }
    sort_fn = sort_map.get(params.ordenar_por, sort_map[OrdenarPor.MENOR_PRECO])
    items.sort(key=sort_fn)

    paginas = math.ceil(total / params.por_pagina) if total else 0
    resultado = PaginacaoOut(
        items=items,
        total=total,
        pagina=params.pagina,
        paginas=paginas,
    )
    await cache_set(key, resultado.model_dump())
    return resultado


async def obter_produto(db: AsyncSession, produto_id: int) -> Produto | None:
    """Retorna produto com preços ordenados por valor."""
    query = (
        select(Produto)
        .options(joinedload(Produto.precos).joinedload(Preco.loja))
        .where(Produto.id == produto_id)
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()
