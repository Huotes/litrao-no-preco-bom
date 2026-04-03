"""Cria tabelas lojas, produtos e precos.

Revision ID: 001
Revises:
Create Date: 2026-04-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Lojas
    op.create_table(
        "lojas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("url_base", sa.String(500), nullable=False, unique=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("ativa", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Produtos
    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(300), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("subtipo", sa.String(100), nullable=True),
        sa.Column("marca", sa.String(200), nullable=True),
        sa.Column("volume_ml", sa.Integer(), nullable=True),
        sa.Column("teor_alcoolico", sa.Numeric(4, 1), nullable=True),
        sa.Column("imagem_url", sa.String(500), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_produtos_nome", "produtos", ["nome"])
    op.create_index("ix_produtos_tipo", "produtos", ["tipo"])
    op.create_index("ix_produtos_marca", "produtos", ["marca"])
    op.create_index("ix_produtos_tipo_marca", "produtos", ["tipo", "marca"])

    # Preços
    op.create_table(
        "precos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("produto_id", sa.Integer(), sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("loja_id", sa.Integer(), sa.ForeignKey("lojas.id"), nullable=False),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("valor_original", sa.Numeric(10, 2), nullable=True),
        sa.Column("url_oferta", sa.String(1000), nullable=False),
        sa.Column("em_promocao", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("coletado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_precos_produto_valor", "precos", ["produto_id", "valor"])
    op.create_index("ix_precos_coletado", "precos", ["coletado_em"])


def downgrade() -> None:
    op.drop_table("precos")
    op.drop_table("produtos")
    op.drop_table("lojas")
