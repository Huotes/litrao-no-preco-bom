"""Rotas de produtos e busca.

Princípio KISS: rotas finas, lógica no service.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.produto import TipoBebida
from app.schemas.produto import (
    BuscaParams,
    PaginacaoOut,
    PrecoOut,
    ProdutoDetalhe,
)
from app.services.produto_service import buscar_produtos, obter_produto

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("/", response_model=PaginacaoOut)
async def listar_produtos(
    params: BuscaParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginacaoOut:
    """Busca produtos com Full Text Search, filtros e paginação."""
    return await buscar_produtos(db, params)


@router.get("/tipos/", response_model=list[str])
async def listar_tipos() -> list[str]:
    """Lista todos os tipos de bebida disponíveis."""
    return [t.value for t in TipoBebida]


@router.get("/{produto_id}", response_model=ProdutoDetalhe)
async def detalhe_produto(
    produto_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProdutoDetalhe:
    """Retorna produto com histórico de preços por loja."""
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
        teor_alcoolico=(
            float(produto.teor_alcoolico) if produto.teor_alcoolico else None
        ),
        imagem_url=produto.imagem_url,
        descricao=produto.descricao,
        artesanal=produto.artesanal,
        palavras_chave=produto.palavras_chave,
        menor_preco=float(menor.valor) if menor else None,
        loja_menor_preco=menor.loja.nome if menor else None,
        url_oferta=menor.url_oferta if menor else None,
        url_redirecionamento=menor.url_redirecionamento if menor else None,
        loja_icone=menor.loja.icone if menor else None,
        precos=[PrecoOut.model_validate(p) for p in precos_ordenados],
    )
