"""Script para popular o banco com dados reais de lojas e produtos.

Princípios: DRY, idempotente, dados realistas.
"""

import asyncio
import random
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models.produto import Loja, Preco, Produto


# ---------------------------------------------------------------------------
# Lojas reais com tipo_fonte e ícone
# ---------------------------------------------------------------------------

LOJAS = [
    {
        "nome": "Mercado Livre",
        "url_base": "https://mercadolivre.com.br",
        "tipo_fonte": "marketplace",
        "icone": "🟡",
    },
    {
        "nome": "Shopee",
        "url_base": "https://shopee.com.br",
        "tipo_fonte": "marketplace",
        "icone": "🟠",
    },
    {
        "nome": "Atacadão",
        "url_base": "https://atacadao.com.br",
        "tipo_fonte": "scraper",
        "icone": "🔵",
    },
    {
        "nome": "Walmart",
        "url_base": "https://walmart.com.br",
        "tipo_fonte": "scraper",
        "icone": "🔷",
    },
    {
        "nome": "Max Atacadista",
        "url_base": "https://maxatacadista.com.br",
        "tipo_fonte": "scraper",
        "icone": "🟢",
    },
    {
        "nome": "Food To Save",
        "url_base": "https://foodtosave.com.br",
        "tipo_fonte": "api",
        "icone": "🌱",
    },
    {
        "nome": "Pão de Açúcar",
        "url_base": "https://paodeacucar.com",
        "tipo_fonte": "scraper",
        "icone": "🟤",
    },
    {
        "nome": "Carrefour",
        "url_base": "https://carrefour.com.br",
        "tipo_fonte": "scraper",
        "icone": "🔴",
    },
    {
        "nome": "Assaí Atacadista",
        "url_base": "https://assai.com.br",
        "tipo_fonte": "scraper",
        "icone": "🟡",
    },
    {
        "nome": "Empório da Cerveja",
        "url_base": "https://emporiodacerveja.com.br",
        "tipo_fonte": "scraper",
        "icone": "🍺",
    },
]

# ---------------------------------------------------------------------------
# Produtos com dados completos (artesanal, palavras_chave, descrição)
# ---------------------------------------------------------------------------

PRODUTOS = [
    # --- Cervejas industriais ---
    {
        "nome": "Skol Pilsen Lata 350ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Skol",
        "volume_ml": 350, "teor": 4.7, "base": 3.49,
        "palavras_chave": "skol pilsen lata gelada barata",
        "descricao": "Cerveja Skol Pilsen, a cerveja que desce redondo.",
    },
    {
        "nome": "Brahma Duplo Malte 600ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Brahma",
        "volume_ml": 600, "teor": 4.7, "base": 6.99,
        "palavras_chave": "brahma duplo malte litrão garrafa",
        "descricao": "Brahma Duplo Malte, sabor encorpado e marcante.",
    },
    {
        "nome": "Heineken Long Neck 330ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Heineken",
        "volume_ml": 330, "teor": 5.0, "base": 5.29,
        "palavras_chave": "heineken long neck premium importada",
    },
    {
        "nome": "Corona Extra 355ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Corona",
        "volume_ml": 355, "teor": 4.5, "base": 7.49,
        "palavras_chave": "corona extra limão mexicana",
    },
    {
        "nome": "Budweiser Lata 473ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Budweiser",
        "volume_ml": 473, "teor": 5.0, "base": 4.29,
        "palavras_chave": "budweiser lata latão americana",
    },
    {
        "nome": "Antarctica Original 600ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Antarctica",
        "volume_ml": 600, "teor": 5.0, "base": 5.49,
        "palavras_chave": "antarctica original litrão garrafa",
    },
    {
        "nome": "Stella Artois 275ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Stella Artois",
        "volume_ml": 275, "teor": 5.0, "base": 4.99,
        "palavras_chave": "stella artois premium belga",
    },
    {
        "nome": "IPA Lagunitas 355ml",
        "tipo": "cerveja", "subtipo": "IPA", "marca": "Lagunitas",
        "volume_ml": 355, "teor": 6.2, "base": 12.90,
        "palavras_chave": "lagunitas ipa artesanal craft",
    },
    # --- Cervejas artesanais ---
    {
        "nome": "Colorado Appia 600ml",
        "tipo": "cerveja", "subtipo": "Wheat Ale", "marca": "Colorado",
        "volume_ml": 600, "teor": 5.5, "base": 18.90, "artesanal": True,
        "palavras_chave": "colorado appia trigo mel artesanal craft",
        "descricao": "Cerveja de trigo com mel de laranjeira. Artesanal brasileira.",
    },
    {
        "nome": "Wäls Session Citra IPA 600ml",
        "tipo": "cerveja", "subtipo": "Session IPA", "marca": "Wäls",
        "volume_ml": 600, "teor": 4.5, "base": 22.90, "artesanal": True,
        "palavras_chave": "wals session citra ipa artesanal mineira craft",
        "descricao": "Session IPA com lúpulo Citra. Cervejaria artesanal de MG.",
    },
    {
        "nome": "Bodebrown Cacau IPA 330ml",
        "tipo": "cerveja", "subtipo": "IPA", "marca": "Bodebrown",
        "volume_ml": 330, "teor": 6.0, "base": 19.90, "artesanal": True,
        "palavras_chave": "bodebrown cacau ipa curitiba artesanal craft",
    },
    # --- Vinhos ---
    {
        "nome": "Vinho Casillero del Diablo Cabernet 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Casillero del Diablo",
        "volume_ml": 750, "teor": 13.5, "base": 39.90,
        "palavras_chave": "casillero diablo cabernet chileno tinto",
    },
    {
        "nome": "Vinho Santa Helena Reservado Merlot 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Santa Helena",
        "volume_ml": 750, "teor": 13.0, "base": 29.90,
        "palavras_chave": "santa helena reservado merlot chileno",
    },
    {
        "nome": "Vinho Miolo Seleção Chardonnay 750ml",
        "tipo": "vinho", "subtipo": "Branco", "marca": "Miolo",
        "volume_ml": 750, "teor": 12.5, "base": 34.50,
        "palavras_chave": "miolo seleção chardonnay branco brasileiro",
    },
    {
        "nome": "Espumante Chandon Brut 750ml",
        "tipo": "vinho", "subtipo": "Espumante", "marca": "Chandon",
        "volume_ml": 750, "teor": 12.0, "base": 69.90,
        "palavras_chave": "chandon brut espumante festa celebração",
    },
    # --- Destilados ---
    {
        "nome": "Absolut Vodka Original 750ml",
        "tipo": "destilado", "subtipo": "Vodka", "marca": "Absolut",
        "volume_ml": 750, "teor": 40.0, "base": 69.90,
        "palavras_chave": "absolut vodka sueca original",
    },
    {
        "nome": "Jack Daniel's Tennessee 1L",
        "tipo": "destilado", "subtipo": "Whisky", "marca": "Jack Daniel's",
        "volume_ml": 1000, "teor": 40.0, "base": 159.90,
        "palavras_chave": "jack daniels whisky tennessee americano",
    },
    {
        "nome": "Gin Tanqueray London Dry 750ml",
        "tipo": "destilado", "subtipo": "Gin", "marca": "Tanqueray",
        "volume_ml": 750, "teor": 43.1, "base": 99.90,
        "palavras_chave": "tanqueray gin london dry gintonico",
    },
    {
        "nome": "Cachaça 51 965ml",
        "tipo": "destilado", "subtipo": "Cachaça", "marca": "51",
        "volume_ml": 965, "teor": 40.0, "base": 12.90,
        "palavras_chave": "51 cachaça caipirinha brasileira",
    },
    {
        "nome": "Tequila José Cuervo Ouro 750ml",
        "tipo": "destilado", "subtipo": "Tequila", "marca": "José Cuervo",
        "volume_ml": 750, "teor": 38.0, "base": 89.90,
        "palavras_chave": "jose cuervo tequila ouro mexicana",
    },
    {
        "nome": "Campari Bitter 998ml",
        "tipo": "destilado", "subtipo": "Bitter", "marca": "Campari",
        "volume_ml": 998, "teor": 25.0, "base": 49.90,
        "palavras_chave": "campari bitter negroni aperol drink",
    },
    # --- Destilados artesanais ---
    {
        "nome": "Cachaça Weber Haus Prata 700ml",
        "tipo": "destilado", "subtipo": "Cachaça", "marca": "Weber Haus",
        "volume_ml": 700, "teor": 40.0, "base": 59.90, "artesanal": True,
        "palavras_chave": "weber haus cachaça prata artesanal gaúcha",
        "descricao": "Cachaça artesanal gaúcha envelhecida em dornas de inox.",
    },
    # --- Drinks prontos ---
    {
        "nome": "Smirnoff Ice Long Neck 275ml",
        "tipo": "drink_pronto", "subtipo": "Ice", "marca": "Smirnoff",
        "volume_ml": 275, "teor": 5.0, "base": 5.99,
        "palavras_chave": "smirnoff ice limão vodka pronto",
    },
    {
        "nome": "Beats GT 313ml Lata",
        "tipo": "drink_pronto", "subtipo": "Misto", "marca": "Beats",
        "volume_ml": 313, "teor": 7.9, "base": 4.49,
        "palavras_chave": "beats gt gin tonica lata pronto",
    },
    # --- Food To Save (lootbox surpresa) ---
    {
        "nome": "Sacola Surpresa Bebidas - Food To Save",
        "tipo": "outros", "subtipo": "Lootbox", "marca": "Food To Save",
        "volume_ml": None, "teor": None, "base": 14.99,
        "palavras_chave": "food to save sacola surpresa lootbox bebida",
        "descricao": (
            "Sacola surpresa com bebidas alcoólicas próximas do vencimento. "
            "Conteúdo variado: cervejas, vinhos ou destilados. Economia de até 70%."
        ),
    },
]


def _url_redir(loja_url: str, oferta_url: str) -> str:
    """Gera URL de redirecionamento com rastreamento."""
    return f"/redir?to={oferta_url}&ref=litrao"


async def seed() -> None:
    """Popula banco com dados reais. Idempotente."""
    async with async_session() as db:
        result = await db.execute(select(Produto).limit(1))
        if result.scalar_one_or_none():
            print("Banco já possui dados, pulando seed.")
            return

        # Criar lojas
        lojas_db = []
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
                artesanal=item.get("artesanal", False),
                palavras_chave=item.get("palavras_chave"),
            )
            db.add(produto)
            await db.flush()

            # 3-6 preços por produto em lojas aleatórias
            base = item["base"]
            n_lojas = random.randint(3, min(6, len(lojas_db)))
            lojas_sample = random.sample(lojas_db, k=n_lojas)

            for i, loja in enumerate(lojas_sample):
                variacao = round(base * random.uniform(0.90, 1.30), 2)
                valor = round(base if i == 0 else variacao, 2)
                em_promo = i == 0 and random.random() > 0.4
                valor_orig = round(valor * 1.35, 2) if em_promo else None

                url_oferta = f"{loja.url_base}/produto/{produto.id}"
                preco = Preco(
                    produto_id=produto.id,
                    loja_id=loja.id,
                    valor=Decimal(str(valor)),
                    valor_original=(
                        Decimal(str(valor_orig)) if valor_orig else None
                    ),
                    url_oferta=url_oferta,
                    url_redirecionamento=_url_redir(loja.url_base, url_oferta),
                    em_promocao=em_promo,
                )
                db.add(preco)

        await db.commit()
        print(
            f"Seed concluído: {len(PRODUTOS)} produtos, {len(LOJAS)} lojas."
        )


if __name__ == "__main__":
    asyncio.run(seed())
