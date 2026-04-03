"""Tasks Celery para orquestração de scraping."""

import asyncio
import logging
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.models.produto import Loja, Preco, Produto
from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada")

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Registre novas spiders aqui
SPIDERS_REGISTRY: list[type[BaseSpider]] = [
    # ExemploSpider,  # Descomentar quando implementar
]


async def _persistir_produtos(produtos: list[ProdutoScraped], loja_nome: str) -> int:
    """Salva produtos no banco, criando ou atualizando preços."""
    async with async_session() as db:
        # Garantir que a loja existe
        result = await db.execute(select(Loja).where(Loja.nome == loja_nome))
        loja = result.scalar_one_or_none()
        if not loja:
            loja = Loja(nome=loja_nome, url_base=f"https://{loja_nome.lower().replace(' ', '')}.com.br")
            db.add(loja)
            await db.flush()

        count = 0
        for item in produtos:
            # Buscar produto existente ou criar
            result = await db.execute(
                select(Produto).where(Produto.nome == item.nome)
            )
            produto = result.scalar_one_or_none()

            if not produto:
                produto = Produto(
                    nome=item.nome,
                    tipo=item.tipo,
                    marca=item.marca,
                    volume_ml=item.volume_ml,
                    imagem_url=item.imagem_url,
                )
                db.add(produto)
                await db.flush()

            # Registrar novo preço
            preco = Preco(
                produto_id=produto.id,
                loja_id=loja.id,
                valor=item.valor,
                valor_original=item.valor_original,
                url_oferta=item.url_oferta,
                em_promocao=item.em_promocao,
            )
            db.add(preco)
            count += 1

        await db.commit()
        return count


@celery_app.task(bind=True, max_retries=3)
def scrape_loja(self, spider_name: str):
    """Executa scraping de uma loja específica."""
    spider_cls = _get_spider_by_name(spider_name)
    if spider_cls is None:
        logger.error("Spider '%s' não encontrada no registry", spider_name)
        return

    async def _run():
        async with spider_cls() as spider:
            produtos = await spider.executar()
            if not produtos:
                return 0
            return await _persistir_produtos(produtos, spider.nome_loja)

    try:
        count = asyncio.run(_run())
        logger.info("Spider %s: %d preços salvos", spider_name, count)
        return count
    except Exception as exc:
        logger.exception("Erro no scrape de %s", spider_name)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task
def scrape_todas_lojas():
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
