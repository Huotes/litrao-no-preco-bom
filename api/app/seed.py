"""Seed: cria lojas e popula produtos reais via API pública do Mercado Livre.

Zero dados fictícios. Todos os preços, imagens e URLs são reais.
A API do ML (api.mercadolibre.com) é pública e não requer autenticação.
"""

import asyncio
import logging
import re
import sys
from decimal import Decimal
import httpx
from sqlalchemy import select

from app.core.database import async_session
from app.models.produto import Loja, Preco, Produto

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


# ---------------------------------------------------------------------------
# Lojas com URLs reais de busca
# ---------------------------------------------------------------------------

def _logo(domain: str) -> str:
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


LOJAS = [
    {"nome": "Mercado Livre", "url_base": "https://www.mercadolivre.com.br",
     "tipo_fonte": "marketplace", "icone": _logo("mercadolivre.com.br")},
    {"nome": "Shopee", "url_base": "https://shopee.com.br",
     "tipo_fonte": "marketplace", "icone": _logo("shopee.com.br")},
    {"nome": "Carrefour", "url_base": "https://www.carrefour.com.br",
     "tipo_fonte": "scraper", "icone": _logo("carrefour.com.br")},
    {"nome": "Pão de Açúcar", "url_base": "https://www.paodeacucar.com",
     "tipo_fonte": "scraper", "icone": _logo("paodeacucar.com")},
    {"nome": "Amazon", "url_base": "https://www.amazon.com.br",
     "tipo_fonte": "marketplace", "icone": _logo("amazon.com.br")},
    {"nome": "Magazine Luiza", "url_base": "https://www.magazineluiza.com.br",
     "tipo_fonte": "marketplace", "icone": _logo("magazineluiza.com.br")},
    {"nome": "Americanas", "url_base": "https://www.americanas.com.br",
     "tipo_fonte": "marketplace", "icone": _logo("americanas.com.br")},
]


# ---------------------------------------------------------------------------
# Termos de busca para popular o catálogo via ML API
# ---------------------------------------------------------------------------

TERMOS_BUSCA = [
    "cerveja lata 350ml",
    "cerveja long neck",
    "cerveja artesanal 600ml",
    "cerveja ipa lata",
    "vinho tinto 750ml",
    "vinho branco 750ml",
    "espumante brut 750ml",
    "vodka 750ml",
    "whisky 1 litro",
    "gin london dry 750ml",
    "cachaça 1 litro",
    "tequila 750ml",
    "drink pronto ice lata",
    "campari 998ml",
]

ML_API = "https://api.mercadolibre.com/sites/MLB/search"


# ---------------------------------------------------------------------------
# Helpers para classificar produtos da ML API
# ---------------------------------------------------------------------------

def _inferir_tipo(nome: str) -> str:
    """Infere tipo da bebida pelo nome."""
    n = nome.lower()
    mapa = {
        "cerveja": [
            "cerveja", "lager", "pilsen", "ipa", "ale", "stout",
            "weiss", "wheat", "porter", "bock", "amber", "beer",
        ],
        "vinho": [
            "vinho", "wine", "cabernet", "merlot", "chardonnay",
            "espumante", "prosecco", "rosé", "champagne",
        ],
        "destilado": [
            "vodka", "whisky", "whiskey", "rum", "gin", "tequila",
            "cachaça", "cachaca", "cognac", "brandy", "bitter",
            "campari", "aperol", "licor",
        ],
        "drink_pronto": [
            "ice", "beats", "smirnoff ice", "drink pronto",
            "ready to drink", "rtd",
        ],
    }
    for tipo, kws in mapa.items():
        if any(kw in n for kw in kws):
            return tipo
    return "outros"


def _inferir_subtipo(nome: str, tipo: str) -> str | None:
    """Infere subtipo pelo nome."""
    n = nome.lower()
    subtipos = {
        "cerveja": {
            "IPA": ["ipa"], "Pilsen": ["pilsen", "pilsner"],
            "Lager": ["lager"], "Stout": ["stout"],
            "Wheat Ale": ["wheat", "weiss", "trigo"],
        },
        "vinho": {
            "Tinto": ["tinto", "cabernet", "merlot", "malbec", "carmenere"],
            "Branco": ["branco", "chardonnay", "sauvignon blanc"],
            "Espumante": ["espumante", "prosecco", "brut", "champagne"],
            "Rosé": ["rosé", "rose"],
        },
        "destilado": {
            "Vodka": ["vodka"], "Whisky": ["whisky", "whiskey", "bourbon"],
            "Gin": ["gin"], "Tequila": ["tequila"],
            "Cachaça": ["cachaça", "cachaca"], "Rum": ["rum"],
            "Bitter": ["bitter", "campari", "aperol"],
        },
    }
    for sub, kws in subtipos.get(tipo, {}).items():
        if any(kw in n for kw in kws):
            return sub
    return None


def _extrair_marca(nome: str) -> str | None:
    """Extrai marca conhecida do nome."""
    marcas = [
        "Skol", "Brahma", "Antarctica", "Heineken", "Budweiser",
        "Stella Artois", "Corona", "Absolut", "Smirnoff", "Beats",
        "Colorado", "Wäls", "Jack Daniel's", "Tanqueray", "Beefeater",
        "Campari", "José Cuervo", "Chandon", "Miolo", "51",
        "Santa Helena", "Casillero del Diablo", "Lagunitas", "Patagonia",
        "Original", "Bohemia", "Amstel", "Petra", "Baden Baden",
        "Eisenbahn", "Devassa", "Itaipava", "Kaiser", "Crystal",
    ]
    n = nome.lower()
    for marca in marcas:
        if marca.lower() in n:
            return marca
    return None


def _extrair_volume(nome: str) -> int | None:
    """Extrai volume em ml do nome."""
    m = re.search(r"(\d+)\s*ml", nome, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*l(?:itro)?s?\b", nome, re.IGNORECASE)
    if m:
        return int(float(m.group(1).replace(",", ".")) * 1000)
    return None


# ---------------------------------------------------------------------------
# Busca real na API do Mercado Livre
# ---------------------------------------------------------------------------

async def _buscar_ml(client: httpx.AsyncClient, termo: str) -> list[dict]:
    """Busca um termo na ML API e retorna items parseados."""
    items = []
    try:
        resp = await client.get(
            ML_API,
            params={"q": termo, "limit": "20", "sort": "relevance"},
            timeout=15,
        )
        logger.info(
            "ML API [%s]: status=%d, url=%s",
            termo, resp.status_code, str(resp.url),
        )
        if resp.status_code != 200:
            logger.warning("ML API retornou %d para '%s'", resp.status_code, termo)
            return []

        data = resp.json()
        for item in data.get("results", []):
            nome = item.get("title", "")
            preco = item.get("price")
            if not nome or not preco or preco <= 0:
                continue

            tipo = _inferir_tipo(nome)
            if tipo == "outros":
                continue

            thumbnail = item.get("thumbnail", "")
            img = ""
            if thumbnail:
                img = thumbnail.replace("-I.jpg", "-O.jpg").replace(
                    "-I.webp", "-O.webp"
                )

            original = item.get("original_price")
            em_promo = bool(original and original > preco)

            items.append({
                "nome": nome,
                "tipo": tipo,
                "subtipo": _inferir_subtipo(nome, tipo),
                "marca": _extrair_marca(nome),
                "volume_ml": _extrair_volume(nome),
                "valor": float(preco),
                "valor_original": float(original) if original else None,
                "imagem_url": img,
                "permalink": item.get("permalink", ""),
                "em_promocao": em_promo,
            })
    except httpx.ConnectError as exc:
        logger.error("ML API ConnectError [%s]: %s", termo, exc)
    except httpx.TimeoutException:
        logger.error("ML API Timeout [%s]", termo)
    except Exception as exc:
        logger.error("ML API erro [%s]: %s", termo, exc)

    return items


async def _coletar_produtos_ml() -> list[dict]:
    """Coleta produtos reais de todos os termos de busca."""
    todos: list[dict] = []
    vistos: set[str] = set()

    async with httpx.AsyncClient(
        headers={"User-Agent": "LitraoBot/1.0"},
        follow_redirects=True,
    ) as client:
        for termo in TERMOS_BUSCA:
            items = await _buscar_ml(client, termo)
            for item in items:
                chave = item["nome"].lower().strip()
                if chave not in vistos:
                    vistos.add(chave)
                    todos.append(item)

    logger.info("Total de produtos unicos coletados do ML: %d", len(todos))
    return todos


# ---------------------------------------------------------------------------
# Seed principal
# ---------------------------------------------------------------------------

async def seed() -> None:
    """Popula banco com dados REAIS. Idempotente."""
    async with async_session() as db:
        result = await db.execute(select(Produto).limit(1))
        if result.scalar_one_or_none():
            print("Banco ja possui dados, pulando seed.", flush=True)
            return

        # 1. Criar lojas
        print("Criando lojas...", flush=True)
        lojas_db: dict[str, Loja] = {}

        for loja_data in LOJAS:
            loja = Loja(
                nome=loja_data["nome"],
                url_base=loja_data["url_base"],
                tipo_fonte=loja_data.get("tipo_fonte", "scraper"),
                icone=loja_data.get("icone"),
            )
            db.add(loja)
            lojas_db[loja_data["nome"]] = loja

        await db.flush()
        print(f"  {len(LOJAS)} lojas criadas.", flush=True)

        # 2. Buscar produtos REAIS na API do ML
        print("Buscando produtos reais na API do Mercado Livre...", flush=True)
        produtos_ml = await _coletar_produtos_ml()

        if not produtos_ml:
            print(
                "AVISO: Nenhum produto coletado da ML API. "
                "Verifique conectividade do container.",
                flush=True,
            )
            await db.commit()
            return

        # 3. Salvar produtos com preço REAL (apenas ML)
        print(f"Salvando {len(produtos_ml)} produtos...", flush=True)
        loja_ml = lojas_db["Mercado Livre"]

        for item in produtos_ml:
            produto = Produto(
                nome=item["nome"],
                tipo=item["tipo"],
                subtipo=item.get("subtipo"),
                marca=item.get("marca"),
                volume_ml=item.get("volume_ml"),
                imagem_url=item.get("imagem_url"),
                artesanal=False,
            )
            db.add(produto)
            await db.flush()

            # Preço REAL do ML com permalink real
            preco_ml = Preco(
                produto_id=produto.id,
                loja_id=loja_ml.id,
                valor=Decimal(str(item["valor"])),
                valor_original=(
                    Decimal(str(item["valor_original"]))
                    if item.get("valor_original")
                    else None
                ),
                url_oferta=item["permalink"],
                url_redirecionamento=item["permalink"],
                em_promocao=item.get("em_promocao", False),
            )
            db.add(preco_ml)

        await db.commit()
        print(
            f"Seed concluido: {len(produtos_ml)} produtos reais do ML, "
            f"{len(LOJAS)} lojas.",
            flush=True,
        )


if __name__ == "__main__":
    asyncio.run(seed())
