"""Tasks Celery para orquestração de scraping.

Princípios: DRY (persistência genérica), KISS (registry simples).
Apenas spiders com APIs confirmadas estão registradas.
"""

import asyncio
import logging
import os
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.celery_app import celery_app
from app.models.produto import Loja, Preco, Produto
from app.spiders.base import BaseSpider, ProdutoScraped
from app.spiders.mercadolivre import MercadoLivreSpider
from app.spiders.shopee import ShopeeSpider

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada")

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Apenas spiders com APIs públicas confirmadas
SPIDERS_REGISTRY: list[type[BaseSpider]] = [
    MercadoLivreSpider,  # API pública, sem autenticação
    ShopeeSpider,  # API interna, best-effort
]


def _logo_url(domain: str) -> str:
    """Gera URL de favicon via Google."""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


async def _garantir_loja(db: AsyncSession, spider: BaseSpider) -> Loja:
    """Retorna loja existente ou cria nova."""
    result = await db.execute(
        select(Loja).where(Loja.nome == spider.nome_loja),
    )
    loja = result.scalar_one_or_none()
    if not loja:
        domain = spider.url_base.replace("https://", "").replace("http://", "")
        loja = Loja(
            nome=spider.nome_loja,
            url_base=spider.url_base,
            tipo_fonte=spider.tipo_fonte,
            icone=_logo_url(domain),
        )
        db.add(loja)
        await db.flush()
    return loja


async def _persistir_produtos(
    produtos: list[ProdutoScraped],
    spider: BaseSpider,
) -> int:
    """Salva produtos coletados no banco."""
    async with async_session() as db:
        loja = await _garantir_loja(db, spider)
        count = 0

        for item in produtos:
            result = await db.execute(
                select(Produto).where(Produto.nome == item.nome),
            )
            produto = result.scalar_one_or_none()

            if not produto:
                produto = Produto(
                    nome=item.nome,
                    tipo=item.tipo,
                    subtipo=item.subtipo,
                    marca=item.marca,
                    volume_ml=item.volume_ml,
                    imagem_url=item.imagem_url,
                    artesanal=item.artesanal,
                    palavras_chave=item.palavras_chave,
                    descricao=item.descricao,
                )
                db.add(produto)
                await db.flush()
            elif item.imagem_url and not produto.imagem_url:
                # Atualiza imagem se o produto não tinha
                produto.imagem_url = item.imagem_url

            preco = Preco(
                produto_id=produto.id,
                loja_id=loja.id,
                valor=Decimal(str(item.valor)),
                valor_original=(
                    Decimal(str(item.valor_original)) if item.valor_original else None
                ),
                url_oferta=item.url_oferta,
                url_redirecionamento=item.url_redirecionamento,
                em_promocao=item.em_promocao,
            )
            db.add(preco)
            count += 1

        await db.commit()
        return count


@celery_app.task(bind=True, max_retries=3)
def scrape_loja(self, spider_name: str) -> int:
    """Executa scraping de uma loja específica."""
    spider_cls = _get_spider_by_name(spider_name)
    if spider_cls is None:
        logger.error("Spider '%s' não encontrada", spider_name)
        return 0

    async def _run() -> int:
        async with spider_cls() as spider:
            produtos = await spider.executar()
            if not produtos:
                return 0
            return await _persistir_produtos(produtos, spider)

    try:
        count = asyncio.run(_run())
        logger.info("Spider %s: %d preços salvos", spider_name, count)
        return count
    except Exception as exc:
        logger.exception("Erro no scrape de %s", spider_name)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task
def scrape_todas_lojas() -> None:
    """Dispara scraping de todas as lojas registradas."""
    for spider_cls in SPIDERS_REGISTRY:
        scrape_loja.delay(spider_cls.nome_loja)
    logger.info("Disparado scraping de %d lojas", len(SPIDERS_REGISTRY))


def _get_spider_by_name(name: str) -> type[BaseSpider] | None:
    """Busca spider pelo nome_loja."""
    for spider_cls in SPIDERS_REGISTRY:
        if spider_cls.nome_loja == name:
            return spider_cls
    return None
