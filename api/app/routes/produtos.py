"""Rotas de produtos e busca.

Princípio KISS: rotas finas, lógica no service.
"""

import re
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.produto import Loja, TipoBebida
from app.schemas.produto import (
    BuscaParams,
    LinkBuscaOut,
    PaginacaoOut,
    PrecoOut,
    ProdutoDetalhe,
)
from app.services.produto_service import buscar_produtos, obter_produto

router = APIRouter(prefix="/produtos", tags=["produtos"])

# Templates de busca por loja (slug_sep indica formato slug)
_BUSCA_TEMPLATES: dict[str, dict] = {
    "Mercado Livre": {
        "tpl": "https://lista.mercadolivre.com.br/{q}",
        "slug_sep": "-",
    },
    "Shopee": {
        "tpl": "https://shopee.com.br/search?keyword={q}",
    },
    "Carrefour": {
        "tpl": "https://www.carrefour.com.br/busca/{q}",
        "slug_sep": "-",
    },
    "Pão de Açúcar": {
        "tpl": "https://www.paodeacucar.com/busca?terms={q}",
    },
    "Amazon": {
        "tpl": "https://www.amazon.com.br/s?k={q}",
    },
    "Magazine Luiza": {
        "tpl": "https://www.magazineluiza.com.br/busca/{q}/",
        "slug_sep": "-",
    },
    "Americanas": {
        "tpl": "https://www.americanas.com.br/busca/{q}",
        "slug_sep": "-",
    },
}


def _termo_curto(nome: str) -> str:
    """Gera termo de busca curto a partir do nome completo."""
    n = re.sub(r"\b(pack|caixa|unidades?|kit|combo|c/\d+)\b", "", nome, flags=re.I)
    n = re.sub(r"\s{2,}", " ", n).strip()
    palavras = [p for p in n.split() if len(p) > 1][:4]
    return " ".join(palavras)


def _gerar_url_busca(loja_nome: str, termo: str) -> str | None:
    """Gera URL de busca para uma loja."""
    cfg = _BUSCA_TEMPLATES.get(loja_nome)
    if not cfg:
        return None
    if cfg.get("slug_sep"):
        q = termo.lower().replace(" ", cfg["slug_sep"])
    else:
        q = quote_plus(termo)
    return cfg["tpl"].format(q=q)


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
    """Retorna produto com preços reais e links de busca em outras lojas."""
    produto = await obter_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    precos_ordenados = sorted(produto.precos, key=lambda p: p.valor)
    menor = precos_ordenados[0] if precos_ordenados else None

    # Lojas que JÁ têm preço coletado para este produto
    lojas_com_preco = {p.loja.nome for p in produto.precos}

    # Gerar links de busca para lojas SEM preço coletado
    termo = _termo_curto(produto.nome)
    result_lojas = await db.execute(select(Loja).where(Loja.ativa.is_(True)))
    todas_lojas = result_lojas.scalars().all()

    links_busca = []
    for loja in todas_lojas:
        if loja.nome in lojas_com_preco:
            continue
        url = _gerar_url_busca(loja.nome, termo)
        if url:
            links_busca.append(LinkBuscaOut(
                loja_nome=loja.nome,
                loja_icone=loja.icone,
                url_busca=url,
            ))

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
        links_busca=links_busca,
    )
