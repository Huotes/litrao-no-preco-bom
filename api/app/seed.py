"""Script para popular o banco com dados de exemplo."""

import asyncio
import random
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session, engine, Base
from app.models.produto import Loja, Preco, Produto


LOJAS = [
    ("Pão de Açúcar", "https://paodeacucar.com"),
    ("Carrefour", "https://carrefour.com.br"),
    ("Extra", "https://extra.com.br"),
    ("Assaí", "https://assai.com.br"),
    ("Atacadão", "https://atacadao.com.br"),
    ("Empório da Cerveja", "https://emporiodacerveja.com.br"),
]

PRODUTOS = [
    {"nome": "Skol Pilsen Lata 350ml", "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Skol", "volume_ml": 350, "teor": 4.7, "base": 3.49},
    {"nome": "Brahma Duplo Malte 600ml", "tipo": "cerveja", "subtipo": "Lager", "marca": "Brahma", "volume_ml": 600, "teor": 4.7, "base": 6.99},
    {"nome": "Heineken Long Neck 330ml", "tipo": "cerveja", "subtipo": "Lager", "marca": "Heineken", "volume_ml": 330, "teor": 5.0, "base": 5.29},
    {"nome": "Corona Extra 355ml", "tipo": "cerveja", "subtipo": "Lager", "marca": "Corona", "volume_ml": 355, "teor": 4.5, "base": 7.49},
    {"nome": "Budweiser Lata 473ml", "tipo": "cerveja", "subtipo": "Lager", "marca": "Budweiser", "volume_ml": 473, "teor": 5.0, "base": 4.29},
    {"nome": "Antarctica Original 600ml", "tipo": "cerveja", "subtipo": "Pilsen", "marca": "Antarctica", "volume_ml": 600, "teor": 5.0, "base": 5.49},
    {"nome": "Stella Artois 275ml", "tipo": "cerveja", "subtipo": "Lager", "marca": "Stella Artois", "volume_ml": 275, "teor": 5.0, "base": 4.99},
    {"nome": "IPA Lagunitas 355ml", "tipo": "cerveja", "subtipo": "IPA", "marca": "Lagunitas", "volume_ml": 355, "teor": 6.2, "base": 12.90},
    {"nome": "Vinho Casillero del Diablo Cabernet 750ml", "tipo": "vinho", "subtipo": "Tinto", "marca": "Casillero del Diablo", "volume_ml": 750, "teor": 13.5, "base": 39.90},
    {"nome": "Vinho Santa Helena Reservado Merlot 750ml", "tipo": "vinho", "subtipo": "Tinto", "marca": "Santa Helena", "volume_ml": 750, "teor": 13.0, "base": 29.90},
    {"nome": "Vinho Miolo Seleção Chardonnay 750ml", "tipo": "vinho", "subtipo": "Branco", "marca": "Miolo", "volume_ml": 750, "teor": 12.5, "base": 34.50},
    {"nome": "Espumante Chandon Brut 750ml", "tipo": "vinho", "subtipo": "Espumante", "marca": "Chandon", "volume_ml": 750, "teor": 12.0, "base": 69.90},
    {"nome": "Absolut Vodka Original 750ml", "tipo": "destilado", "subtipo": "Vodka", "marca": "Absolut", "volume_ml": 750, "teor": 40.0, "base": 69.90},
    {"nome": "Smirnoff Ice Long Neck 275ml", "tipo": "drink_pronto", "subtipo": "Ice", "marca": "Smirnoff", "volume_ml": 275, "teor": 5.0, "base": 5.99},
    {"nome": "Jack Daniel's Tennessee 1L", "tipo": "destilado", "subtipo": "Whisky", "marca": "Jack Daniel's", "volume_ml": 1000, "teor": 40.0, "base": 159.90},
    {"nome": "Gin Tanqueray London Dry 750ml", "tipo": "destilado", "subtipo": "Gin", "marca": "Tanqueray", "volume_ml": 750, "teor": 43.1, "base": 99.90},
    {"nome": "Cachaça 51 965ml", "tipo": "destilado", "subtipo": "Cachaça", "marca": "51", "volume_ml": 965, "teor": 40.0, "base": 12.90},
    {"nome": "Tequila José Cuervo Ouro 750ml", "tipo": "destilado", "subtipo": "Tequila", "marca": "José Cuervo", "volume_ml": 750, "teor": 38.0, "base": 89.90},
    {"nome": "Campari Bitter 998ml", "tipo": "destilado", "subtipo": "Bitter", "marca": "Campari", "volume_ml": 998, "teor": 25.0, "base": 49.90},
    {"nome": "Beats GT 313ml Lata", "tipo": "drink_pronto", "subtipo": "Misto", "marca": "Beats", "volume_ml": 313, "teor": 7.9, "base": 4.49},
]


async def seed():
    """Popula banco com dados de exemplo."""
    async with async_session() as db:
        # Verifica se já tem dados
        result = await db.execute(select(Produto).limit(1))
        if result.scalar_one_or_none():
            print("Banco já possui dados, pulando seed.")
            return

        # Criar lojas
        lojas_db = []
        for nome, url in LOJAS:
            loja = Loja(nome=nome, url_base=url)
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
                teor_alcoolico=Decimal(str(item["teor"])) if item.get("teor") else None,
            )
            db.add(produto)
            await db.flush()

            # Gerar 3-5 preços por produto em lojas aleatórias
            base = item["base"]
            lojas_sample = random.sample(lojas_db, k=random.randint(3, min(5, len(lojas_db))))
            for i, loja in enumerate(lojas_sample):
                variacao = round(base * random.uniform(0.95, 1.25), 2)
                em_promo = i == 0 and random.random() > 0.5
                valor_orig = round(variacao * 1.3, 2) if em_promo else None

                preco = Preco(
                    produto_id=produto.id,
                    loja_id=loja.id,
                    valor=Decimal(str(round(base if i == 0 else variacao, 2))),
                    valor_original=Decimal(str(valor_orig)) if valor_orig else None,
                    url_oferta=f"{loja.url_base}/produto/{produto.id}",
                    em_promocao=em_promo,
                )
                db.add(preco)

        await db.commit()
        print(f"Seed concluído: {len(PRODUTOS)} produtos, {len(LOJAS)} lojas.")


if __name__ == "__main__":
    asyncio.run(seed())
