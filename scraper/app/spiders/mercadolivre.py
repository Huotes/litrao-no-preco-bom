"""Spider Mercado Livre — API pública de busca (única confirmada).

Endpoint: GET https://api.mercadolibre.com/sites/MLB/search
Documentação: https://developers.mercadolivre.com.br/en_us/items-and-searches
Não requer autenticação para buscas públicas.
"""

import logging

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)

TERMOS_BUSCA = [
    "cerveja lata 350ml",
    "cerveja long neck",
    "cerveja artesanal 600ml",
    "cerveja ipa",
    "vinho tinto 750ml",
    "vinho branco 750ml",
    "espumante brut",
    "vodka 750ml",
    "whisky 1 litro",
    "gin london dry 750ml",
    "cachaça",
    "tequila 750ml",
    "drink pronto ice",
    "campari",
]

API_SEARCH = "https://api.mercadolibre.com/sites/MLB/search"


class MercadoLivreSpider(BaseSpider):
    """Spider para Mercado Livre via API pública REST.

    Única API brasileira confirmada como pública e funcional.
    Retorna nome, preço, imagem, permalink.
    """

    nome_loja = "Mercado Livre"
    url_base = "https://www.mercadolivre.com.br"
    tipo_fonte = "marketplace"

    async def scrape(self) -> list[ProdutoScraped]:
        """Busca bebidas alcoólicas na API do Mercado Livre."""
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

        logger.info("ML: %d produtos únicos coletados", len(todos))
        return todos

    async def _buscar_termo(self, termo: str) -> list[ProdutoScraped]:
        """Busca um termo na API."""
        data = await self.fetch_json(API_SEARCH, params={
            "q": termo,
            "limit": "50",
            "sort": "relevance",
        })

        return [
            p for item in data.get("results", [])
            if (p := self._parse_item(item)) is not None
        ]

    def _parse_item(self, item: dict) -> ProdutoScraped | None:
        """Converte item da API em ProdutoScraped."""
        nome = item.get("title", "")
        preco = item.get("price")
        if not nome or not preco:
            return None

        tipo = self.inferir_tipo(nome)
        if tipo == "outros":
            return None

        original = item.get("original_price")
        em_promo = original is not None and original > preco
        permalink = item.get("permalink", "")

        # Imagem: thumbnail → qualidade alta (-O ao invés de -I)
        thumbnail = item.get("thumbnail", "")
        img_url = None
        if thumbnail:
            img_url = thumbnail.replace("-I.jpg", "-O.jpg").replace("-I.webp", "-O.webp")

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
