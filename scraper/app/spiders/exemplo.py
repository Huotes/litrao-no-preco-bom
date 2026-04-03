"""Spider de exemplo — substituir pela implementação real da loja."""

from selectolax.parser import HTMLParser

from app.spiders.base import BaseSpider, ProdutoScraped


class ExemploSpider(BaseSpider):
    """Spider modelo para demonstrar o padrão de implementação.

    Para adicionar uma nova loja:
    1. Copie este arquivo e renomeie.
    2. Ajuste nome_loja, url_base e os seletores CSS.
    3. Registre no SPIDERS_REGISTRY em scrape_tasks.py.
    """

    nome_loja = "Exemplo Bebidas"
    url_base = "https://exemplo.com.br/bebidas"

    async def scrape(self) -> list[ProdutoScraped]:
        """Extrai produtos da página de listagem."""
        html = await self.fetch(self.url_base)
        tree = HTMLParser(html)

        produtos = []
        for card in tree.css(".product-card"):
            nome_el = card.css_first(".product-name")
            preco_el = card.css_first(".product-price")
            if not nome_el or not preco_el:
                continue

            nome = nome_el.text(strip=True)
            valor = self._parse_preco(preco_el.text(strip=True))
            if not valor:
                continue

            preco_original_el = card.css_first(".product-original-price")
            valor_original = (
                self._parse_preco(preco_original_el.text(strip=True))
                if preco_original_el else None
            )

            link_el = card.css_first("a[href]")
            url = link_el.attributes.get("href", "") if link_el else ""

            img_el = card.css_first("img[src]")
            img_url = img_el.attributes.get("src") if img_el else None

            produtos.append(ProdutoScraped(
                nome=nome,
                tipo=self._inferir_tipo(nome),
                marca=self._extrair_marca(nome),
                volume_ml=self._extrair_volume(nome),
                valor=valor,
                valor_original=valor_original,
                url_oferta=url if url.startswith("http") else f"{self.url_base}{url}",
                imagem_url=img_url,
                em_promocao=valor_original is not None and valor_original > valor,
            ))

        return produtos

    @staticmethod
    def _parse_preco(texto: str) -> float | None:
        """Converte 'R$ 12,90' para 12.90."""
        limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(limpo)
        except ValueError:
            return None

    @staticmethod
    def _inferir_tipo(nome: str) -> str:
        """Infere tipo da bebida pelo nome."""
        nome_lower = nome.lower()
        mapa = {
            "cerveja": ["cerveja", "lager", "pilsen", "ipa", "ale", "stout", "weiss"],
            "vinho": ["vinho", "wine", "cabernet", "merlot", "chardonnay"],
            "destilado": ["vodka", "whisky", "rum", "gin", "tequila", "cachaça"],
        }
        for tipo, keywords in mapa.items():
            if any(kw in nome_lower for kw in keywords):
                return tipo
        return "outros"

    @staticmethod
    def _extrair_marca(nome: str) -> str | None:
        """Extrai marca conhecida do nome."""
        marcas = [
            "Skol", "Brahma", "Antarctica", "Heineken", "Budweiser",
            "Stella Artois", "Corona", "Absolut", "Smirnoff",
        ]
        nome_lower = nome.lower()
        for marca in marcas:
            if marca.lower() in nome_lower:
                return marca
        return None

    @staticmethod
    def _extrair_volume(nome: str) -> int | None:
        """Extrai volume em ml do nome do produto."""
        import re
        match = re.search(r"(\d+)\s*ml", nome, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*l(?:itro)?", nome, re.IGNORECASE)
        if match:
            return int(float(match.group(1).replace(",", ".")) * 1000)
        return None
