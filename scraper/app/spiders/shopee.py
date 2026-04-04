"""Spider Shopee — scraping via API interna de busca.

A API da Shopee é protegida por anti-bot. Este spider faz tentativas
com fallback gracioso: se bloqueado, retorna lista vazia sem erro.
Princípios: KISS (API JSON), DRY (herda BaseSpider).
"""

import logging

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

TERMOS_BUSCA = [
    "cerveja",
    "vinho tinto",
    "vodka",
    "whisky",
    "gin",
    "espumante",
    "drink pronto",
    "cachaça",
    "cerveja artesanal",
]

API_SEARCH = "https://shopee.com.br/api/v4/search/search_items"


class ShopeeSpider(BaseSpider):
    """Spider para Shopee via API interna de busca."""

    nome_loja = "Shopee"
    url_base = "https://shopee.com.br"
    tipo_fonte = "marketplace"

    def __init__(self) -> None:
        super().__init__()
        self.client.headers.update({
            "Referer": "https://shopee.com.br/",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
        })

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca bebidas na API da Shopee."""
        todos: list[ProdutoScraped] = []
        vistos: set[str] = set()

        for termo in TERMOS_BUSCA:
            try:
                produtos = await self._buscar_termo(termo)
                for p in produtos:
                    chave = p.nome.lower().strip()
                    if chave not in vistos:
                        vistos.add(chave)
                        todos.append(p)
            except Exception:
                logger.debug("Shopee: bloqueado ou erro no termo '%s'", termo)
                continue

        return todos

    async def _buscar_termo(self, termo: str) -> list[ProdutoScraped]:
        """Busca um termo na API da Shopee."""
        data = await self.fetch_json(API_SEARCH, params={
            "keyword": termo,
            "limit": "50",
            "newest": "0",
            "order": "relevancy",
            "by": "relevancy",
        })

        items = data.get("items") or []
        produtos = []
        for item_wrapper in items:
            item = item_wrapper.get("item_basic", item_wrapper)
            produto = self._parse_item(item)
            if produto:
                produtos.append(produto)

        return produtos

    def _parse_item(self, item: dict) -> ProdutoScraped | None:
        """Converte item da API Shopee em ProdutoScraped."""
        nome = item.get("name", "")
        price_raw = item.get("price", 0)

        # Shopee retorna preço em unidade * 100000
        preco = price_raw / 100000 if price_raw > 1000 else float(price_raw)

        if not nome or preco <= 0:
            return None

        tipo = self.inferir_tipo(nome)
        if tipo == "outros":
            return None

        original_raw = item.get("price_before_discount", 0)
        original = original_raw / 100000 if original_raw > 1000 else float(original_raw)
        em_promo = original > preco if original else False

        shop_id = item.get("shopid", "")
        item_id = item.get("itemid", "")
        url = f"https://shopee.com.br/product/{shop_id}/{item_id}"

        image = item.get("image", "")
        img_url = f"https://cf.shopee.com.br/file/{image}" if image else None

        return ProdutoScraped(
            nome=nome,
            tipo=tipo,
            subtipo=self.inferir_subtipo(nome, tipo),
            marca=self.extrair_marca(nome),
            volume_ml=self.extrair_volume(nome),
            valor=round(preco, 2),
            valor_original=round(original, 2) if em_promo else None,
            url_oferta=url,
            url_redirecionamento=url,
            imagem_url=img_url,
            em_promocao=em_promo,
        )
