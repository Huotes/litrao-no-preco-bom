"""Spider base com lógica comum de scraping.

Princípios: DRY (helpers reutilizáveis), KISS (interface simples).
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


@dataclass
class ProdutoScraped:
    """Dados extraídos de um produto."""

    nome: str
    tipo: str
    marca: str | None
    volume_ml: int | None
    valor: float
    valor_original: float | None
    url_oferta: str
    imagem_url: str | None
    em_promocao: bool = False
    subtipo: str | None = None
    url_redirecionamento: str | None = None
    artesanal: bool = False
    palavras_chave: str | None = None
    descricao: str | None = None


class BaseSpider(ABC):
    """Classe base para spiders de lojas.

    Subclasses devem definir nome_loja, url_base e implementar scrape().
    """

    nome_loja: str = ""
    url_base: str = ""
    tipo_fonte: str = "scraper"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            headers=HEADERS, timeout=30, follow_redirects=True,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def fetch(self, url: str) -> str:
        """Faz requisição HTTP e retorna o corpo."""
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text

    async def fetch_json(self, url: str, params: dict | None = None) -> dict:
        """Faz requisição HTTP e retorna JSON."""
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    async def scrape(self) -> list[ProdutoScraped]:
        """Extrai produtos da loja. Implementar em cada spider."""

    async def executar(self) -> list[ProdutoScraped]:
        """Executa o scraping com tratamento de erro."""
        try:
            produtos = await self.scrape()
            logger.info("%s: %d produtos coletados", self.nome_loja, len(produtos))
            return produtos
        except Exception:
            logger.exception("Erro ao scrape de %s", self.nome_loja)
            return []

    # --- Helpers estáticos (DRY) ---

    @staticmethod
    def parse_preco(texto: str) -> float | None:
        """Converte 'R$ 12,90' para 12.90."""
        limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(limpo)
        except ValueError:
            return None

    @staticmethod
    def inferir_tipo(nome: str) -> str:
        """Infere tipo da bebida pelo nome."""
        nome_lower = nome.lower()
        mapa = {
            "cerveja": [
                "cerveja", "lager", "pilsen", "ipa", "ale", "stout",
                "weiss", "wheat", "porter", "bock", "amber",
            ],
            "vinho": [
                "vinho", "wine", "cabernet", "merlot", "chardonnay",
                "espumante", "prosecco", "rosé",
            ],
            "destilado": [
                "vodka", "whisky", "whiskey", "rum", "gin", "tequila",
                "cachaça", "cognac", "brandy", "bitter", "campari",
            ],
            "drink_pronto": [
                "ice", "beats", "smirnoff ice", "drink pronto", "ready",
            ],
        }
        for tipo, keywords in mapa.items():
            if any(kw in nome_lower for kw in keywords):
                return tipo
        return "outros"

    @staticmethod
    def inferir_subtipo(nome: str, tipo: str) -> str | None:
        """Infere subtipo da bebida pelo nome e tipo."""
        nome_lower = nome.lower()
        subtipos = {
            "cerveja": {
                "IPA": ["ipa"],
                "Pilsen": ["pilsen", "pilsner"],
                "Lager": ["lager"],
                "Stout": ["stout"],
                "Wheat Ale": ["wheat", "weiss", "trigo"],
                "Porter": ["porter"],
            },
            "vinho": {
                "Tinto": ["tinto", "cabernet", "merlot", "malbec"],
                "Branco": ["branco", "chardonnay", "sauvignon"],
                "Espumante": ["espumante", "prosecco", "brut"],
                "Rosé": ["rosé", "rose"],
            },
            "destilado": {
                "Vodka": ["vodka"],
                "Whisky": ["whisky", "whiskey", "bourbon"],
                "Gin": ["gin"],
                "Tequila": ["tequila"],
                "Cachaça": ["cachaça", "cachaca"],
                "Rum": ["rum"],
            },
        }
        for subtipo, keywords in subtipos.get(tipo, {}).items():
            if any(kw in nome_lower for kw in keywords):
                return subtipo
        return None

    @staticmethod
    def extrair_marca(nome: str) -> str | None:
        """Extrai marca conhecida do nome."""
        marcas = [
            "Skol", "Brahma", "Antarctica", "Heineken", "Budweiser",
            "Stella Artois", "Corona", "Absolut", "Smirnoff", "Beats",
            "Colorado", "Wäls", "Bodebrown", "Jack Daniel's", "Tanqueray",
            "Campari", "José Cuervo", "Chandon", "Miolo", "51",
            "Santa Helena", "Casillero del Diablo",
        ]
        nome_lower = nome.lower()
        for marca in marcas:
            if marca.lower() in nome_lower:
                return marca
        return None

    @staticmethod
    def extrair_volume(nome: str) -> int | None:
        """Extrai volume em ml do nome do produto."""
        match = re.search(r"(\d+)\s*ml", nome, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*l(?:itro)?", nome, re.IGNORECASE)
        if match:
            return int(float(match.group(1).replace(",", ".")) * 1000)
        return None
