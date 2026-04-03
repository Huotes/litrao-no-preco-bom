"""Tasks Celery para orquestração de scraping."""

import asyncio
import logging
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://litrao_user:changeme@postgres:5432/litrao",
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Registre novas spiders aqui
SPIDERS_REGISTRY: list[type[BaseSpider]] = [
    # ExemploSpider,  # Descomentar quando implementar
]


async def _persistir_produtos(produtos: list[ProdutoScraped], loja_nome: str) -> int:
    """Salva produtos no banco, criando ou atualizando preços."""
    # Import local para evitar circular
    from app.spiders.base import ProdutoScraped  # noqa: F811

    # Lazy import dos models (evita import circular com Base)
    import importlib
    models = importlib.import_module("app.models.produto")
    Produto = models.Produto
    Preco = models.Preco
    Loja = models.Loja

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


def _run_async(coro):
    """Executa coroutine em contexto síncrono do Celery."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3)
def scrape_loja(self, spider_index: int):
    """Executa scraping de uma loja específica."""
    if spider_index >= len(SPIDERS_REGISTRY):
        logger.error("Spider index %d fora do range", spider_index)
        return

    spider_cls = SPIDERS_REGISTRY[spider_index]

    async def _run():
        async with spider_cls() as spider:
            produtos = await spider.executar()
            if not produtos:
                return 0
            return await _persistir_produtos(produtos, spider.nome_loja)

    try:
        count = _run_async(_run())
        logger.info("Spider %s: %d preços salvos", spider_cls.nome_loja, count)
        return count
    except Exception as exc:
        logger.exception("Erro no scrape de %s", spider_cls.nome_loja)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task
def scrape_todas_lojas():
    """Dispara scraping de todas as lojas registradas."""
    for i in range(len(SPIDERS_REGISTRY)):
        scrape_loja.delay(i)
    logger.info("Disparado scraping de %d lojas", len(SPIDERS_REGISTRY))
