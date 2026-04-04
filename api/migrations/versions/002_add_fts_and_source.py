"""Adiciona Full Text Search, source e campos extras.

Revision ID: 002
Revises: 001
Create Date: 2026-04-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")

    # Novos campos em produtos
    op.add_column("produtos", sa.Column("artesanal", sa.Boolean(), server_default=sa.text("false")))
    op.add_column("produtos", sa.Column("palavras_chave", sa.Text(), nullable=True))

    # Full Text Search — coluna gerada
    op.execute("""
        ALTER TABLE produtos
        ADD COLUMN busca_vetor tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('portuguese', unaccent(coalesce(nome, ''))), 'A') ||
            setweight(to_tsvector('portuguese', unaccent(coalesce(marca, ''))), 'B') ||
            setweight(to_tsvector('portuguese', unaccent(coalesce(subtipo, ''))), 'C')
        ) STORED
    """)
    op.execute("CREATE INDEX ix_produtos_busca_gin ON produtos USING GIN (busca_vetor)")

    # Novos campos em lojas
    op.add_column("lojas", sa.Column("tipo_fonte", sa.String(50), server_default=sa.text("'scraper'")))
    op.add_column("lojas", sa.Column("icone", sa.String(10), nullable=True))

    # Novo campo em precos
    op.add_column("precos", sa.Column("url_redirecionamento", sa.String(1500), nullable=True))

    # Índice parcial para artesanais
    op.execute("CREATE INDEX ix_produtos_artesanal ON produtos (artesanal) WHERE artesanal = true")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_produtos_artesanal")
    op.drop_column("precos", "url_redirecionamento")
    op.drop_column("lojas", "icone")
    op.drop_column("lojas", "tipo_fonte")
    op.execute("DROP INDEX IF EXISTS ix_produtos_busca_gin")
    op.execute("ALTER TABLE produtos DROP COLUMN IF EXISTS busca_vetor")
    op.drop_column("produtos", "palavras_chave")
    op.drop_column("produtos", "artesanal")
