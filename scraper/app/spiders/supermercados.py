"""Spiders para redes de supermercados — Atacadão, Walmart, Max.

Usam scraping HTML com selectolax.
Princípios: DRY (classe base compartilhada), KISS (seletores diretos).
"""

import logging

from selectolax.parser import HTMLParser

from app.spiders.base import BaseSpider, ProdutoScraped

logger = logging.getLogger(__name__)


class SupermercadoSpider(BaseSpider):
    """Base para spiders de supermercados com HTML scraping.

    Subclasses definem seletores CSS e URLs.
    """

    # Seletores CSS — sobrescrever nas subclasses
    seletor_card: str = ".product-card"
    seletor_nome: str = ".product-name"
    seletor_preco: str = ".product-price"
    seletor_preco_original: str = ".product-original-price"
    seletor_link: str = "a[href]"
    seletor_imagem: str = "img[src]"

    # URLs de listagem de bebidas
    urls_bebidas: list[str] = []

    async def scrape(self) -> list[ProdutoScraped]:
        """Coleta produtos de todas as URLs de bebidas."""
        todos: list[ProdutoScraped] = []
        for url in self.urls_bebidas:
            produtos = await self._scrape_pagina(url)
            todos.extend(produtos)
        return todos

    async def _scrape_pagina(self, url: str) -> list[ProdutoScraped]:
        """Extrai produtos de uma página."""
        try:
            html = await self.fetch(url)
        except Exception:
            logger.warning("%s: erro ao acessar %s", self.nome_loja, url)
            return []

        tree = HTMLParser(html)
        produtos = []

        for card in tree.css(self.seletor_card):
            produto = self._parse_card(card, url)
            if produto:
                produtos.append(produto)

        return produtos

    def _parse_card(self, card, base_url: str) -> ProdutoScraped | None:
        """Converte card HTML em ProdutoScraped."""
        nome_el = card.css_first(self.seletor_nome)
        preco_el = card.css_first(self.seletor_preco)
        if not nome_el or not preco_el:
            return None

        nome = nome_el.text(strip=True)
        valor = self.parse_preco(preco_el.text(strip=True))
        if not valor:
            return None

        preco_orig_el = card.css_first(self.seletor_preco_original)
        valor_original = (
            self.parse_preco(preco_orig_el.text(strip=True))
            if preco_orig_el else None
        )

        link_el = card.css_first(self.seletor_link)
        href = link_el.attributes.get("href", "") if link_el else ""
        url_oferta = href if href.startswith("http") else f"{self.url_base}{href}"

        img_el = card.css_first(self.seletor_imagem)
        img_url = img_el.attributes.get("src") if img_el else None

        tipo = self.inferir_tipo(nome)

        return ProdutoScraped(
            nome=nome,
            tipo=tipo,
            subtipo=self.inferir_subtipo(nome, tipo),
            marca=self.extrair_marca(nome),
            volume_ml=self.extrair_volume(nome),
            valor=valor,
            valor_original=valor_original,
            url_oferta=url_oferta,
            url_redirecionamento=url_oferta,
            imagem_url=img_url,
            em_promocao=valor_original is not None and valor_original > valor,
        )


class AtacadaoSpider(SupermercadoSpider):
    """Spider para Atacadão."""

    nome_loja = "Atacadão"
    url_base = "https://www.atacadao.com.br"
    tipo_fonte = "scraper"
    urls_bebidas = [
        "https://www.atacadao.com.br/bebidas-alcoolicas/cervejas",
        "https://www.atacadao.com.br/bebidas-alcoolicas/vinhos",
        "https://www.atacadao.com.br/bebidas-alcoolicas/destilados",
    ]
    seletor_card = "[data-testid='product-card'], .product-card"
    seletor_nome = "[data-testid='product-title'], .product-name"
    seletor_preco = "[data-testid='product-price'], .product-price"


class WalmartSpider(SupermercadoSpider):
    """Spider para Walmart Brasil."""

    nome_loja = "Walmart"
    url_base = "https://www.walmart.com.br"
    tipo_fonte = "scraper"
    urls_bebidas = [
        "https://www.walmart.com.br/bebidas/cervejas",
        "https://www.walmart.com.br/bebidas/vinhos",
        "https://www.walmart.com.br/bebidas/destilados",
    ]


class MaxAtacadistaSpider(SupermercadoSpider):
    """Spider para Max Atacadista."""

    nome_loja = "Max Atacadista"
    url_base = "https://www.maxatacadista.com.br"
    tipo_fonte = "scraper"
    urls_bebidas = [
        "https://www.maxatacadista.com.br/bebidas",
    ]
