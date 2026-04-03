"""Rotas de produtos e busca."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.produto import TipoBebida
from app.schemas.produto import BuscaParams, PaginacaoOut, ProdutoDetalhe, PrecoOut
from app.services.produto_service import buscar_produtos, obter_produto

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("/", response_model=PaginacaoOut)
async def listar_produtos(
    q: str | None = None,
    tipo: TipoBebida | None = None,
    subtipo: str | None = None,
    marca: str | None = None,
    preco_min: float | None = Query(None, ge=0),
    preco_max: float | None = Query(None, ge=0),
    em_promocao: bool | None = None,
    ordenar_por: str = "menor_preco",
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Busca e filtra produtos com paginação."""
    params = BuscaParams(
        q=q, tipo=tipo, subtipo=subtipo, marca=marca,
        preco_min=preco_min, preco_max=preco_max,
        em_promocao=em_promocao, ordenar_por=ordenar_por,
        pagina=pagina, por_pagina=por_pagina,
    )
    return await buscar_produtos(db, params)


@router.get("/{produto_id}", response_model=ProdutoDetalhe)
async def detalhe_produto(
    produto_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna produto com histórico de preços."""
    produto = await obter_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    precos_ordenados = sorted(produto.precos, key=lambda p: p.valor)
    menor = precos_ordenados[0] if precos_ordenados else None

    return ProdutoDetalhe(
        id=produto.id,
        nome=produto.nome,
        tipo=produto.tipo,
        subtipo=produto.subtipo,
        marca=produto.marca,
        volume_ml=produto.volume_ml,
        teor_alcoolico=produto.teor_alcoolico,
        imagem_url=produto.imagem_url,
        descricao=produto.descricao,
        menor_preco=float(menor.valor) if menor else None,
        loja_menor_preco=menor.loja.nome if menor else None,
        precos=[PrecoOut.model_validate(p) for p in precos_ordenados],
    )


@router.get("/tipos/", response_model=list[str])
async def listar_tipos():
    """Lista todos os tipos de bebida disponíveis."""
    return [t.value for t in TipoBebida]
