"""Spider Food To Save — sacolas surpresa de bebidas (lootbox).

Food To Save oferece sacolas surpresa com bebidas próximas do
vencimento, com grandes descontos. Princípio: KISS.
"""

import logging

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

API_BASE = "https://api.foodtosave.com.br/v1"


class FoodToSaveSpider(BaseSpider):
    """Spider para Food To Save via API."""

    nome_loja = "Food To Save"
    url_base = "https://foodtosave.com.br"
    tipo_fonte = "api"

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca sacolas surpresa com bebidas."""
        try:
            data = await self.fetch_json(
                f"{API_BASE}/bags",
                params={"category": "bebidas", "limit": 50},
            )
        except Exception:
            logger.warning("Erro ao acessar API Food To Save")
            return []

        produtos = []
        for bag in data.get("bags", data.get("results", [])):
            produto = self._parse_bag(bag)
            if produto:
                produtos.append(produto)

        return produtos

    def _parse_bag(self, bag: dict) -> ProdutoScraped | None:
        """Converte sacola surpresa em ProdutoScraped."""
        nome = bag.get("name", bag.get("title", ""))
        preco = bag.get("price", bag.get("current_price"))
        if not nome or not preco:
            return None

        original = bag.get("original_price", bag.get("regular_price"))
        bag_id = bag.get("id", "")
        url = f"{self.url_base}/sacola/{bag_id}"

        return ProdutoScraped(
            nome=f"Sacola Surpresa: {nome}" if "sacola" not in nome.lower() else nome,
            tipo="outros",
            subtipo="Lootbox",
            marca="Food To Save",
            volume_ml=None,
            valor=float(preco),
            valor_original=float(original) if original else None,
            url_oferta=url,
            url_redirecionamento=url,
            imagem_url=bag.get("image_url", bag.get("photo")),
            em_promocao=True,
            descricao=(
                "Sacola surpresa com bebidas próximas do vencimento. "
                "Conteúdo variado — economia de até 70%."
            ),
        )
