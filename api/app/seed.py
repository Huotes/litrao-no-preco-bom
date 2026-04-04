"""Script para popular o banco com dados iniciais.

Usa dados realistas com URLs que apontam para buscas reais nas lojas.
Princípios: DRY, idempotente, sem mocks — URLs de busca reais.
"""

import asyncio
import random
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models.produto import Loja, Preco, Produto


# ---------------------------------------------------------------------------
# Lojas — logo via Google Favicon API (S2) ou favicon.ico direto
# ---------------------------------------------------------------------------

def _logo(domain: str) -> str:
    """Gera URL de logo via Google Favicon service."""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


LOJAS = [
    {
        "nome": "Mercado Livre",
        "url_base": "https://www.mercadolivre.com.br",
        "tipo_fonte": "marketplace",
        "icone": _logo("mercadolivre.com.br"),
        "busca_tpl": "https://www.mercadolivre.com.br/jm/search?as_word={q}",
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
    },
    {
        "nome": "Pão de Açúcar",
        "url_base": "https://www.paodeacucar.com",
        "tipo_fonte": "scraper",
        "icone": _logo("paodeacucar.com"),
        "busca_tpl": "https://www.paodeacucar.com/busca?terms={q}",
    },
    {
        "nome": "Atacadão",
        "url_base": "https://www.atacadao.com.br",
        "tipo_fonte": "scraper",
        "icone": _logo("atacadao.com.br"),
        "busca_tpl": "https://www.atacadao.com.br/busca?q={q}",
    },
    {
        "nome": "Assaí Atacadista",
        "url_base": "https://www.assai.com.br",
        "tipo_fonte": "scraper",
        "icone": _logo("assai.com.br"),
        "busca_tpl": "https://www.assai.com.br/busca?q={q}",
    },
    {
        "nome": "Food To Save",
        "url_base": "https://foodtosave.com.br",
        "tipo_fonte": "api",
        "icone": _logo("foodtosave.com.br"),
        "busca_tpl": "https://foodtosave.com.br/sacolas",
    },
    {
        "nome": "Empório da Cerveja",
        "url_base": "https://www.emporiodacerveja.com.br",
        "tipo_fonte": "scraper",
        "icone": _logo("emporiodacerveja.com.br"),
        "busca_tpl": "https://www.emporiodacerveja.com.br/busca?q={q}",
    },
]

# ---------------------------------------------------------------------------
# Produtos com imagens reais (URLs de busca do Mercado Livre que existem)
# ---------------------------------------------------------------------------

PRODUTOS = [
    # --- Cervejas industriais ---
    {
        "nome": "Skol Pilsen Lata 350ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Skol",
        "volume_ml": 350, "teor": 4.7, "base": 3.49,
        "palavras_chave": "skol pilsen lata gelada barata",
        "descricao": "Cerveja Skol Pilsen, a cerveja que desce redondo.",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_959553-MLU75561959498_042024-F.webp",
    },
    {
        "nome": "Brahma Duplo Malte 600ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Brahma",
        "volume_ml": 600, "teor": 4.7, "base": 6.99,
        "palavras_chave": "brahma duplo malte litrão garrafa",
        "descricao": "Brahma Duplo Malte, sabor encorpado e marcante.",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_901742-MLU72554072588_112023-F.webp",
    },
    {
        "nome": "Heineken Long Neck 330ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Heineken",
        "volume_ml": 330, "teor": 5.0, "base": 5.29,
        "palavras_chave": "heineken long neck premium importada",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_662498-MLU74289157122_012024-F.webp",
    },
    {
        "nome": "Corona Extra 355ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Corona",
        "volume_ml": 355, "teor": 4.5, "base": 7.49,
        "palavras_chave": "corona extra limão mexicana",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_631136-MLU72577023096_112023-F.webp",
    },
    {
        "nome": "Budweiser Lata 473ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Budweiser",
        "volume_ml": 473, "teor": 5.0, "base": 4.29,
        "palavras_chave": "budweiser lata latão americana",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_764819-MLU72561073478_112023-F.webp",
    },
    {
        "nome": "Antarctica Original 600ml",
        "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Antarctica",
        "volume_ml": 600, "teor": 5.0, "base": 5.49,
        "palavras_chave": "antarctica original litrão garrafa",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_720613-MLU72577277714_112023-F.webp",
    },
    {
        "nome": "Stella Artois 275ml",
        "tipo": "cerveja", "subtipo": "Lager", "marca": "Stella Artois",
        "volume_ml": 275, "teor": 5.0, "base": 4.99,
        "palavras_chave": "stella artois premium belga",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_679914-MLU72596367862_112023-F.webp",
    },
    {
        "nome": "IPA Lagunitas 355ml",
        "tipo": "cerveja", "subtipo": "IPA", "marca": "Lagunitas",
        "volume_ml": 355, "teor": 6.2, "base": 12.90,
        "palavras_chave": "lagunitas ipa craft lupulo",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_838510-MLU72596379494_112023-F.webp",
    },
    # --- Cervejas artesanais ---
    {
        "nome": "Colorado Appia 600ml",
        "tipo": "cerveja", "subtipo": "Wheat Ale", "marca": "Colorado",
        "volume_ml": 600, "teor": 5.5, "base": 18.90, "artesanal": True,
        "palavras_chave": "colorado appia trigo mel artesanal craft",
        "descricao": "Cerveja de trigo com mel de laranjeira. Artesanal brasileira.",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_625911-MLU74267149834_012024-F.webp",
    },
    {
        "nome": "Wäls Session Citra IPA 600ml",
        "tipo": "cerveja", "subtipo": "Session IPA", "marca": "Wäls",
        "volume_ml": 600, "teor": 4.5, "base": 22.90, "artesanal": True,
        "palavras_chave": "wals session citra ipa artesanal mineira craft",
        "descricao": "Session IPA com lúpulo Citra. Cervejaria artesanal de MG.",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_823099-MLU74789282244_022024-F.webp",
    },
    {
        "nome": "Bodebrown Cacau IPA 330ml",
        "tipo": "cerveja", "subtipo": "IPA", "marca": "Bodebrown",
        "volume_ml": 330, "teor": 6.0, "base": 19.90, "artesanal": True,
        "palavras_chave": "bodebrown cacau ipa curitiba artesanal craft",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_691025-MLU75032073484_032024-F.webp",
    },
    # --- Vinhos ---
    {
        "nome": "Vinho Casillero del Diablo Cabernet 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Casillero del Diablo",
        "volume_ml": 750, "teor": 13.5, "base": 39.90,
        "palavras_chave": "casillero diablo cabernet chileno tinto",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_613139-MLU72546803260_112023-F.webp",
    },
    {
        "nome": "Vinho Santa Helena Reservado Merlot 750ml",
        "tipo": "vinho", "subtipo": "Tinto", "marca": "Santa Helena",
        "volume_ml": 750, "teor": 13.0, "base": 29.90,
        "palavras_chave": "santa helena reservado merlot chileno",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_889614-MLU72584893096_112023-F.webp",
    },
    {
        "nome": "Vinho Miolo Seleção Chardonnay 750ml",
        "tipo": "vinho", "subtipo": "Branco", "marca": "Miolo",
        "volume_ml": 750, "teor": 12.5, "base": 34.50,
        "palavras_chave": "miolo seleção chardonnay branco brasileiro",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_688706-MLU72534994370_112023-F.webp",
    },
    {
        "nome": "Espumante Chandon Brut 750ml",
        "tipo": "vinho", "subtipo": "Espumante", "marca": "Chandon",
        "volume_ml": 750, "teor": 12.0, "base": 69.90,
        "palavras_chave": "chandon brut espumante festa celebração",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_948925-MLU72544818382_112023-F.webp",
    },
    # --- Destilados ---
    {
        "nome": "Absolut Vodka Original 750ml",
        "tipo": "destilado", "subtipo": "Vodka", "marca": "Absolut",
        "volume_ml": 750, "teor": 40.0, "base": 69.90,
        "palavras_chave": "absolut vodka sueca original",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_935764-MLU72577318440_112023-F.webp",
    },
    {
        "nome": "Jack Daniel's Tennessee 1L",
        "tipo": "destilado", "subtipo": "Whisky", "marca": "Jack Daniel's",
        "volume_ml": 1000, "teor": 40.0, "base": 159.90,
        "palavras_chave": "jack daniels whisky tennessee americano",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_772541-MLU72577284068_112023-F.webp",
    },
    {
        "nome": "Gin Tanqueray London Dry 750ml",
        "tipo": "destilado", "subtipo": "Gin", "marca": "Tanqueray",
        "volume_ml": 750, "teor": 43.1, "base": 99.90,
        "palavras_chave": "tanqueray gin london dry gintonico",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_678022-MLU72577236382_112023-F.webp",
    },
    {
        "nome": "Cachaça 51 965ml",
        "tipo": "destilado", "subtipo": "Cachaça", "marca": "51",
        "volume_ml": 965, "teor": 40.0, "base": 12.90,
        "palavras_chave": "51 cachaça caipirinha brasileira",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_804422-MLU72577289720_112023-F.webp",
    },
    {
        "nome": "Tequila José Cuervo Ouro 750ml",
        "tipo": "destilado", "subtipo": "Tequila", "marca": "José Cuervo",
        "volume_ml": 750, "teor": 38.0, "base": 89.90,
        "palavras_chave": "jose cuervo tequila ouro mexicana",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_715103-MLU72577298366_112023-F.webp",
    },
    {
        "nome": "Campari Bitter 998ml",
        "tipo": "destilado", "subtipo": "Bitter", "marca": "Campari",
        "volume_ml": 998, "teor": 25.0, "base": 49.90,
        "palavras_chave": "campari bitter negroni aperol drink",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_693553-MLU72577277244_112023-F.webp",
    },
    # --- Destilados artesanais ---
    {
        "nome": "Cachaça Weber Haus Prata 700ml",
        "tipo": "destilado", "subtipo": "Cachaça", "marca": "Weber Haus",
        "volume_ml": 700, "teor": 40.0, "base": 59.90, "artesanal": True,
        "palavras_chave": "weber haus cachaça prata artesanal gaúcha",
        "descricao": "Cachaça artesanal gaúcha envelhecida em dornas de inox.",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_892788-MLU74783202256_022024-F.webp",
    },
    # --- Drinks prontos ---
    {
        "nome": "Smirnoff Ice Long Neck 275ml",
        "tipo": "drink_pronto", "subtipo": "Ice", "marca": "Smirnoff",
        "volume_ml": 275, "teor": 5.0, "base": 5.99,
        "palavras_chave": "smirnoff ice limão vodka pronto",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_734048-MLU72596400096_112023-F.webp",
    },
    {
        "nome": "Beats GT 313ml Lata",
        "tipo": "drink_pronto", "subtipo": "Misto", "marca": "Beats",
        "volume_ml": 313, "teor": 7.9, "base": 4.49,
        "palavras_chave": "beats gt gin tonica lata pronto",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_919831-MLU72596380434_112023-F.webp",
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
        "imagem_url": "https://www.google.com/s2/favicons?domain=foodtosave.com.br&sz=128",
    },
]


def _url_busca(loja_data: dict, produto_nome: str) -> str:
    """Gera URL de busca real na loja para o produto."""
    from urllib.parse import quote_plus
    tpl = loja_data.get("busca_tpl", f"{loja_data['url_base']}/busca?q={{q}}")
    return tpl.format(q=quote_plus(produto_nome))


async def seed() -> None:
    """Popula banco com dados iniciais. Idempotente."""
    async with async_session() as db:
        result = await db.execute(select(Produto).limit(1))
        if result.scalar_one_or_none():
            print("Banco já possui dados, pulando seed.")
            return

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

        # Mapear loja.id -> loja_data para gerar URLs de busca
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
                imagem_url=item.get("imagem_url"),
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

                # URL real de busca na loja (não 404)
                loja_data = lojas_data_map[loja.id]
                url_busca = _url_busca(loja_data, item["nome"])

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
        print(
            f"Seed concluído: {len(PRODUTOS)} produtos, {len(LOJAS)} lojas."
        )


if __name__ == "__main__":
    asyncio.run(seed())
