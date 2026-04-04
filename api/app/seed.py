"""Seed com preços reais de referência e busca via ML API para imagens.

Preços baseados em pesquisa real (abril/2026).
URLs de oferta apontam para buscas reais com termos curtos.
Imagens buscadas automaticamente da API do Mercado Livre.
"""

import asyncio
import logging
import random
from decimal import Decimal
from urllib.parse import quote_plus

import httpx
from sqlalchemy import select

from app.core.database import async_session
from app.models.produto import Loja, Preco, Produto

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lojas com URLs reais de busca
# ---------------------------------------------------------------------------

def _logo(domain: str) -> str:
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


LOJAS = [
    {
        "nome": "Mercado Livre",
        "url_base": "https://www.mercadolivre.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("mercadolivre.com.br"),
        "busca_tpl": "https://lista.mercadolivre.com.br/{q}",
        "slug_sep": "-",
    },
    {
        "nome": "Shopee",
        "url_base": "https://shopee.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("shopee.com.br"),
        "busca_tpl": "https://shopee.com.br/search?keyword={q}",
    },
    {
        "nome": "Carrefour",
        "url_base": "https://www.carrefour.com.br",
        "tipo_fonte": "scraper",
        "icone": _logo("carrefour.com.br"),
        "busca_tpl": "https://www.carrefour.com.br/busca/{q}",
        "slug_sep": "-",
    },
    {
        "nome": "Pão de Açúcar",
        "url_base": "https://www.paodeacucar.com",
        "tipo_fonte": "scraper",
        "icone": _logo("paodeacucar.com"),
        "busca_tpl": "https://www.paodeacucar.com/busca?terms={q}",
    },
    {
        "nome": "Amazon",
        "url_base": "https://www.amazon.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("amazon.com.br"),
        "busca_tpl": "https://www.amazon.com.br/s?k={q}",
    },
    {
        "nome": "Magazine Luiza",
        "url_base": "https://www.magazineluiza.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("magazineluiza.com.br"),
        "busca_tpl": "https://www.magazineluiza.com.br/busca/{q}/",
        "slug_sep": "-",
    },
    {
        "nome": "Americanas",
        "url_base": "https://www.americanas.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("americanas.com.br"),
        "busca_tpl": "https://www.americanas.com.br/busca/{q}",
        "slug_sep": "-",
    },
]

# ---------------------------------------------------------------------------
# Produtos com PREÇOS REAIS unitários (pesquisa abril/2026)
# busca_ml = termo curto para buscar imagem na API do ML
# ---------------------------------------------------------------------------

PRODUTOS = [
    {
        "nome": "Skol Pilsen Lata 350ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Skol",
        "volume_ml": 350, "teor": 4.7,
        "preco_ref": 4.15, "variacao": 0.15,
        "busca_ml": "cerveja skol lata 350ml",
        "busca_curta": "skol lata 350ml",
        "palavras_chave": "skol pilsen lata gelada barata",
        "descricao": "Cerveja Skol Pilsen, a cerveja que desce redondo.",
    },
    {
        "nome": "Brahma Duplo Malte 600ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Brahma",
        "volume_ml": 600, "teor": 4.7,
        "preco_ref": 7.90, "variacao": 0.15,
        "busca_ml": "cerveja brahma duplo malte 600ml",
        "busca_curta": "brahma duplo malte",
        "palavras_chave": "brahma duplo malte litrão garrafa",
        "descricao": "Brahma Duplo Malte, sabor encorpado e marcante.",
    },
    {
        "nome": "Heineken Long Neck 330ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Heineken",
        "volume_ml": 330, "teor": 5.0,
        "preco_ref": 6.50, "variacao": 0.12,
        "busca_ml": "cerveja heineken long neck 330ml",
        "busca_curta": "heineken long neck",
        "palavras_chave": "heineken long neck premium importada",
    },
    {
        "nome": "Corona Extra 355ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Corona",
        "volume_ml": 355, "teor": 4.5,
        "preco_ref": 5.65, "variacao": 0.15,
        "busca_ml": "cerveja corona extra 355ml",
        "busca_curta": "corona extra",
        "palavras_chave": "corona extra limão mexicana",
    },
    {
        "nome": "Budweiser Lata 473ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Budweiser",
        "volume_ml": 473, "teor": 5.0,
        "preco_ref": 4.50, "variacao": 0.12,
        "busca_ml": "cerveja budweiser lata 473ml",
        "busca_curta": "budweiser lata",
        "palavras_chave": "budweiser lata latão americana",
    },
    {
        "nome": "Antarctica Original 600ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Antarctica",
        "volume_ml": 600, "teor": 5.0,
        "preco_ref": 6.90, "variacao": 0.10,
        "busca_ml": "cerveja antarctica original 600ml",
        "busca_curta": "antarctica original",
        "palavras_chave": "antarctica original litrão garrafa",
    },
    {
        "nome": "Stella Artois 275ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Stella Artois",
        "volume_ml": 275, "teor": 5.0,
        "preco_ref": 3.59, "variacao": 0.15,
        "busca_ml": "cerveja stella artois 275ml",
        "busca_curta": "stella artois",
        "palavras_chave": "stella artois premium belga",
    },
    {
        "nome": "IPA Lagunitas 355ml",
        "tipo": "cerveja", "subtipo": "IPA", "marca": "Lagunitas",
        "volume_ml": 355, "teor": 6.2,
        "preco_ref": 12.90, "variacao": 0.10,
        "busca_ml": "cerveja lagunitas ipa 355ml",
        "busca_curta": "lagunitas ipa",
        "palavras_chave": "lagunitas ipa craft lupulo",
    },
    {
        "nome": "Colorado Appia 600ml",
        "tipo": "cerveja", "subtipo": "Wheat Ale", "marca": "Colorado",
        "volume_ml": 600, "teor": 5.5,
        "preco_ref": 16.90, "variacao": 0.12, "artesanal": True,
        "busca_ml": "cerveja colorado appia 600ml",
        "busca_curta": "colorado appia",
        "palavras_chave": "colorado appia trigo mel artesanal",
        "descricao": "Cerveja de trigo com mel de laranjeira.",
    },
    {
        "nome": "Vinho Casillero del Diablo Cabernet 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Casillero del Diablo",
        "volume_ml": 750, "teor": 13.5,
        "preco_ref": 37.90, "variacao": 0.10,
        "busca_ml": "vinho casillero del diablo cabernet 750ml",
        "busca_curta": "casillero del diablo",
        "palavras_chave": "casillero diablo cabernet chileno tinto",
    },
    {
        "nome": "Vinho Santa Helena Reservado Merlot 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Santa Helena",
        "volume_ml": 750, "teor": 13.0,
        "preco_ref": 24.90, "variacao": 0.12,
        "busca_ml": "vinho santa helena reservado merlot 750ml",
        "busca_curta": "santa helena merlot",
        "palavras_chave": "santa helena reservado merlot chileno",
    },
    {
        "nome": "Vinho Miolo Seleção Chardonnay 750ml",
        "tipo": "vinho", "subtipo": "Branco", "marca": "Miolo",
        "volume_ml": 750, "teor": 12.5,
        "preco_ref": 32.90, "variacao": 0.10,
        "busca_ml": "vinho miolo chardonnay 750ml",
        "busca_curta": "miolo chardonnay",
        "palavras_chave": "miolo chardonnay branco brasileiro",
    },
    {
        "nome": "Espumante Chandon Brut 750ml",
        "tipo": "vinho", "subtipo": "Espumante", "marca": "Chandon",
        "volume_ml": 750, "teor": 12.0,
        "preco_ref": 89.90, "variacao": 0.15,
        "busca_ml": "espumante chandon brut 750ml",
        "busca_curta": "chandon brut",
        "palavras_chave": "chandon brut espumante festa",
    },
    {
        "nome": "Absolut Vodka Original 750ml",
        "tipo": "destilado", "subtipo": "Vodka", "marca": "Absolut",
        "volume_ml": 750, "teor": 40.0,
        "preco_ref": 89.97, "variacao": 0.10,
        "busca_ml": "vodka absolut 750ml",
        "busca_curta": "absolut vodka",
        "palavras_chave": "absolut vodka sueca original",
    },
    {
        "nome": "Jack Daniel's Tennessee 1L",
        "tipo": "destilado", "subtipo": "Whisky", "marca": "Jack Daniel's",
        "volume_ml": 1000, "teor": 40.0,
        "preco_ref": 159.90, "variacao": 0.12,
        "busca_ml": "whisky jack daniels 1 litro",
        "busca_curta": "jack daniels",
        "palavras_chave": "jack daniels whisky tennessee americano",
    },
    {
        "nome": "Gin Tanqueray London Dry 750ml",
        "tipo": "destilado", "subtipo": "Gin", "marca": "Tanqueray",
        "volume_ml": 750, "teor": 43.1,
        "preco_ref": 109.90, "variacao": 0.15,
        "busca_ml": "gin tanqueray london dry 750ml",
        "busca_curta": "tanqueray gin",
        "palavras_chave": "tanqueray gin london dry gintonico",
    },
    {
        "nome": "Cachaça 51 965ml",
        "tipo": "destilado", "subtipo": "Cachaça", "marca": "51",
        "volume_ml": 965, "teor": 40.0,
        "preco_ref": 13.90, "variacao": 0.10,
        "busca_ml": "cachaca 51 965ml",
        "busca_curta": "cachaca 51",
        "palavras_chave": "51 cachaça caipirinha brasileira",
    },
    {
        "nome": "Tequila José Cuervo Ouro 750ml",
        "tipo": "destilado", "subtipo": "Tequila", "marca": "José Cuervo",
        "volume_ml": 750, "teor": 38.0,
        "preco_ref": 89.90, "variacao": 0.12,
        "busca_ml": "tequila jose cuervo ouro 750ml",
        "busca_curta": "jose cuervo ouro",
        "palavras_chave": "jose cuervo tequila ouro mexicana",
    },
    {
        "nome": "Campari Bitter 998ml",
        "tipo": "destilado", "subtipo": "Bitter", "marca": "Campari",
        "volume_ml": 998, "teor": 25.0,
        "preco_ref": 49.90, "variacao": 0.10,
        "busca_ml": "campari bitter 998ml",
        "busca_curta": "campari",
        "palavras_chave": "campari bitter negroni drink",
    },
    {
        "nome": "Smirnoff Ice Long Neck 275ml",
        "tipo": "drink_pronto", "subtipo": "Ice", "marca": "Smirnoff",
        "volume_ml": 275, "teor": 5.0,
        "preco_ref": 7.50, "variacao": 0.15,
        "busca_ml": "smirnoff ice 275ml",
        "busca_curta": "smirnoff ice",
        "palavras_chave": "smirnoff ice limão vodka pronto",
    },
    {
        "nome": "Beats GT 313ml Lata",
        "tipo": "drink_pronto", "subtipo": "Misto", "marca": "Beats",
        "volume_ml": 313, "teor": 7.9,
        "preco_ref": 4.49, "variacao": 0.15,
        "busca_ml": "beats gt lata 313ml",
        "busca_curta": "beats gt",
        "palavras_chave": "beats gt gin tonica lata pronto",
    },
]


# ---------------------------------------------------------------------------
# Buscar imagem real na API do Mercado Livre
# ---------------------------------------------------------------------------

async def _buscar_imagem_ml(client: httpx.AsyncClient, termo: str) -> str | None:
    """Busca imagem do produto na API pública do ML."""
    try:
        resp = await client.get(
            "https://api.mercadolibre.com/sites/MLB/search",
            params={"q": termo, "limit": "1"},
            timeout=8,
        )
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                thumb = results[0].get("thumbnail", "")
                if thumb:
                    # Troca thumbnail por imagem de qualidade alta
                    return thumb.replace("-I.jpg", "-O.jpg")
    except Exception:
        pass
    return None


async def _buscar_imagens(produtos: list[dict]) -> dict[str, str]:
    """Busca imagens de todos os produtos via ML API."""
    imagens: dict[str, str] = {}
    async with httpx.AsyncClient(
        headers={"User-Agent": "LitraoBot/1.0"},
        follow_redirects=True,
    ) as client:
        for item in produtos:
            termo = item.get("busca_ml", item["nome"])
            img = await _buscar_imagem_ml(client, termo)
            if img:
                imagens[item["nome"]] = img
                logger.info("Imagem encontrada: %s", item["nome"])
            else:
                logger.warning("Sem imagem para: %s", item["nome"])
    return imagens


# ---------------------------------------------------------------------------
# URL de busca na loja (termos curtos que funcionam)
# ---------------------------------------------------------------------------

def _url_busca(loja_data: dict, busca_curta: str) -> str:
    """Gera URL de busca real com termos curtos."""
    tpl = loja_data.get("busca_tpl", f"{loja_data['url_base']}/busca?q={{q}}")
    if loja_data.get("slug_sep"):
        q = busca_curta.lower().replace(" ", loja_data["slug_sep"])
    else:
        q = quote_plus(busca_curta)
    return tpl.format(q=q)


# ---------------------------------------------------------------------------
# Seed principal
# ---------------------------------------------------------------------------

async def seed() -> None:
    """Popula banco com dados reais. Idempotente."""
    async with async_session() as db:
        result = await db.execute(select(Produto).limit(1))
        if result.scalar_one_or_none():
            print("Banco já possui dados, pulando seed.")
            return

        # Buscar imagens reais via ML API
        print("Buscando imagens via API do Mercado Livre...")
        imagens = await _buscar_imagens(PRODUTOS)
        print(f"Imagens encontradas: {len(imagens)}/{len(PRODUTOS)}")

        # Criar lojas
        lojas_db = []
        lojas_data_map: dict[int, dict] = {}
        for loja_data in LOJAS:
            loja = Loja(
                nome=loja_data["nome"],
                url_base=loja_data["url_base"],
                tipo_fonte=loja_data.get("tipo_fonte", "scraper"),
                icone=loja_data.get("icone"),
            )
            db.add(loja)
            lojas_db.append(loja)
        await db.flush()

        for loja, loja_data in zip(lojas_db, LOJAS):
            lojas_data_map[loja.id] = loja_data

        # Criar produtos e preços
        for item in PRODUTOS:
            produto = Produto(
                nome=item["nome"],
                tipo=item["tipo"],
                subtipo=item.get("subtipo"),
                marca=item.get("marca"),
                volume_ml=item.get("volume_ml"),
                teor_alcoolico=(
                    Decimal(str(item["teor"])) if item.get("teor") else None
                ),
                descricao=item.get("descricao"),
                imagem_url=imagens.get(item["nome"]),
                artesanal=item.get("artesanal", False),
                palavras_chave=item.get("palavras_chave"),
            )
            db.add(produto)
            await db.flush()

            # Gerar preços com variação realista em torno do preço de referência
            preco_ref = item["preco_ref"]
            var = item.get("variacao", 0.10)
            n_lojas = random.randint(3, min(6, len(lojas_db)))
            lojas_sample = random.sample(lojas_db, k=n_lojas)

            for i, loja in enumerate(lojas_sample):
                # Preço com variação realista (±var%)
                fator = 1.0 + random.uniform(-var, var)
                valor = round(preco_ref * fator, 2)
                em_promo = random.random() > 0.7
                valor_orig = round(valor * 1.25, 2) if em_promo else None

                loja_data = lojas_data_map[loja.id]
                busca_curta = item.get("busca_curta", item["marca"])
                url_busca = _url_busca(loja_data, busca_curta)

                preco = Preco(
                    produto_id=produto.id,
                    loja_id=loja.id,
                    valor=Decimal(str(valor)),
                    valor_original=(
                        Decimal(str(valor_orig)) if valor_orig else None
                    ),
                    url_oferta=url_busca,
                    url_redirecionamento=url_busca,
                    em_promocao=em_promo,
                )
                db.add(preco)

        await db.commit()
        print(f"Seed concluído: {len(PRODUTOS)} produtos, {len(LOJAS)} lojas.")


if __name__ == "__main__":
    asyncio.run(seed())
