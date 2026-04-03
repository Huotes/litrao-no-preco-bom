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
            valor = self.parse_preco(preco_el.text(strip=True))
            if not valor:
                continue

            preco_original_el = card.css_first(".product-original-price")
            valor_original = (
                self.parse_preco(preco_original_el.text(strip=True))
                if preco_original_el else None
            )

            link_el = card.css_first("a[href]")
            url = link_el.attributes.get("href", "") if link_el else ""

            img_el = card.css_first("img[src]")
            img_url = img_el.attributes.get("src") if img_el else None

            produtos.append(ProdutoScraped(
                nome=nome,
                tipo=self.inferir_tipo(nome),
                marca=self.extrair_marca(nome),
                volume_ml=self.extrair_volume(nome),
                valor=valor,
                valor_original=valor_original,
                url_oferta=url if url.startswith("http") else f"{self.url_base}{url}",
                imagem_url=img_url,
                em_promocao=valor_original is not None and valor_original > valor,
            ))

        return produtos
