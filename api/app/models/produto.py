"""Models do domínio: Produto, Loja e Preço."""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoBebida(str, PyEnum):
    """Categorias de bebidas."""

    CERVEJA = "cerveja"
    VINHO = "vinho"
    DESTILADO = "destilado"
    REFRIGERANTE_ALCOOLICO = "refrigerante_alcoolico"
    DRINK_PRONTO = "drink_pronto"
    OUTROS = "outros"


class Loja(Base):
    """Estabelecimento ou e-commerce que vende bebidas."""

    __tablename__ = "lojas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    url_base: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    ativa: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    precos: Mapped[list["Preco"]] = relationship(back_populates="loja")


class Produto(Base):
    """Bebida cadastrada no sistema."""

    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    tipo: Mapped[TipoBebida] = mapped_column(String(50), nullable=False, index=True)
    subtipo: Mapped[str | None] = mapped_column(String(100))
    marca: Mapped[str | None] = mapped_column(String(200), index=True)
    volume_ml: Mapped[int | None] = mapped_column()
    teor_alcoolico: Mapped[float | None] = mapped_column(Numeric(4, 1))
    imagem_url: Mapped[str | None] = mapped_column(String(500))
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    precos: Mapped[list["Preco"]] = relationship(back_populates="produto")

    __table_args__ = (
        Index("ix_produtos_tipo_marca", "tipo", "marca"),
    )


class Preco(Base):
    """Registro de preço de um produto em uma loja."""

    __tablename__ = "precos"

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    loja_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_original: Mapped[float | None] = mapped_column(Numeric(10, 2))
    url_oferta: Mapped[str] = mapped_column(String(1000), nullable=False)
    em_promocao: Mapped[bool] = mapped_column(default=False)
    coletado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    produto: Mapped[Produto] = relationship(back_populates="precos")
    loja: Mapped[Loja] = relationship(back_populates="precos")

    __table_args__ = (
        Index("ix_precos_produto_valor", "produto_id", "valor"),
        Index("ix_precos_coletado", "coletado_em"),
    )
