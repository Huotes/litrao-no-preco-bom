"""Spider Mercado Livre — usa API pública de busca.

Endpoint: GET https://api.mercadolibre.com/sites/MLB/search
Não requer autenticação para buscas públicas.
Princípios: KISS (API JSON direta), DRY (herda BaseSpider).
"""

import logging
from urllib.parse import quote_plus

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

# Termos de busca para bebidas alcoólicas
TERMOS_BUSCA = [
    "cerveja lata 350ml",
    "cerveja long neck",
    "cerveja artesanal",
    "vinho tinto 750ml",
    "vinho branco",
    "espumante brut",
    "vodka 750ml",
    "whisky 1 litro",
    "gin london dry",
    "cachaça",
    "tequila",
    "drink pronto ice",
]

API_SEARCH = "https://api.mercadolibre.com/sites/MLB/search"


class MercadoLivreSpider(BaseSpider):
    """Spider para Mercado Livre via API pública REST."""

    nome_loja = "Mercado Livre"
    url_base = "https://mercadolivre.com.br"
    tipo_fonte = "marketplace"

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca bebidas na API do Mercado Livre."""
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
                logger.warning("ML: erro no termo '%s'", termo)
                continue

        return todos

    async def _buscar_termo(self, termo: str) -> list[ProdutoScraped]:
        """Busca um termo específico na API."""
        data = await self.fetch_json(API_SEARCH, params={
            "q": termo,
            "limit": "50",
            "sort": "relevance",
        })

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

        # Filtra apenas bebidas alcoólicas
        tipo = self.inferir_tipo(nome)
        if tipo == "outros":
            return None

        original = item.get("original_price")
        em_promo = original is not None and original > preco
        permalink = item.get("permalink", "")
        thumbnail = item.get("thumbnail", "")

        # Melhora qualidade da imagem (I=small, O=original)
        img_url = None
        if thumbnail:
            img_url = thumbnail.replace("-I.jpg", "-O.jpg")

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
            imagem_url=img_url,
            em_promocao=em_promo,
        )
