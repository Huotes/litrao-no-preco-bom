"""Spider Mercado Livre — usa API pública de busca.

Endpoint: GET https://api.mercadolibre.com/sites/MLB/search
Não requer autenticação para buscas públicas.
Princípios: KISS (API JSON direta), DRY (herda BaseSpider).
"""

import logging

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

# Termos de busca para bebidas alcoólicas
TERMOS_BUSCA = [
    "cerveja lata",
    "cerveja long neck",
    "cerveja artesanal",
    "vinho tinto",
    "vinho branco",
    "espumante",
    "vodka",
    "whisky",
    "gin",
    "cachaça",
    "tequila",
    "drink pronto",
]

API_SEARCH = "https://api.mercadolibre.com/sites/MLB/search"
CATEGORY_BEBIDAS = "MLB1403"  # Categoria: Alimentos e Bebidas


class MercadoLivreSpider(BaseSpider):
    """Spider para Mercado Livre via API pública."""

    nome_loja = "Mercado Livre"
    url_base = "https://mercadolivre.com.br"
    tipo_fonte = "marketplace"

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca bebidas na API do Mercado Livre."""
        todos_produtos: list[ProdutoScraped] = []
        vistos: set[str] = set()

        for termo in TERMOS_BUSCA:
            produtos = await self._buscar_termo(termo)
            for p in produtos:
                if p.url_oferta not in vistos:
                    vistos.add(p.url_oferta)
                    todos_produtos.append(p)

        return todos_produtos

    async def _buscar_termo(self, termo: str) -> list[ProdutoScraped]:
        """Busca um termo específico na API."""
        try:
            data = await self.fetch_json(API_SEARCH, params={
                "q": termo,
                "category": CATEGORY_BEBIDAS,
                "limit": 50,
                "sort": "relevance",
            })
        except Exception:
            logger.warning("Erro ao buscar '%s' no ML", termo)
            return []

        produtos = []
        for item in data.get("results", []):
            produto = self._parse_item(item)
            if produto:
                produtos.append(produto)

        return produtos

    def _parse_item(self, item: dict) -> ProdutoScraped | None:
        """Converte item da API em ProdutoScraped."""
        nome = item.get("title", "")
        preco = item.get("price")
        if not nome or not preco:
            return None

        original = item.get("original_price")
        em_promo = original is not None and original > preco
        permalink = item.get("permalink", "")
        thumbnail = item.get("thumbnail", "")

        tipo = self.inferir_tipo(nome)

        return ProdutoScraped(
            nome=nome,
            tipo=tipo,
            subtipo=self.inferir_subtipo(nome, tipo),
            marca=self.extrair_marca(nome),
            volume_ml=self.extrair_volume(nome),
            valor=float(preco),
            valor_original=float(original) if original else None,
            url_oferta=permalink,
            url_redirecionamento=permalink,
            imagem_url=thumbnail.replace("-I.jpg", "-O.jpg") if thumbnail else None,
            em_promocao=em_promo,
        )
