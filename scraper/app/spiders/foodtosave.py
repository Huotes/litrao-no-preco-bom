"""Spider Food To Save — sacolas surpresa de bebidas (lootbox).

Food To Save oferece sacolas surpresa com bebidas próximas do
vencimento, com grandes descontos.
Princípios: KISS (tentativa de API + fallback gracioso).
"""

import logging

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

# URLs possíveis da API Food To Save
API_URLS = [
    "https://api.foodtosave.com.br/v1/bags",
    "https://api.foodtosave.com.br/v2/bags",
]


class FoodToSaveSpider(BaseSpider):
    """Spider para Food To Save via API."""

    nome_loja = "Food To Save"
    url_base = "https://foodtosave.com.br"
    tipo_fonte = "api"

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca sacolas surpresa com bebidas."""
        for api_url in API_URLS:
            try:
                data = await self.fetch_json(
                    api_url,
                    params={"category": "bebidas", "limit": "50"},
                )
                bags = data.get("bags", data.get("results", data.get("data", [])))
                if bags:
                    return [p for p in (self._parse_bag(b) for b in bags) if p]
            except Exception:
                logger.debug("FoodToSave: falha em %s", api_url)
                continue

        logger.info("FoodToSave: nenhuma API respondeu, retornando vazio")
        return []

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
