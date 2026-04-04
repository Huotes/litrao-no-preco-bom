"""Schemas Pydantic para serialização e validação.

Segue princípio DRY: schemas base reutilizados por herança.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.models.produto import TipoBebida


class OrdenarPor(str, PyEnum):
    """Opções válidas de ordenação."""

    MENOR_PRECO = "menor_preco"
    MAIOR_PRECO = "maior_preco"
    NOME = "nome"


# --- Loja ---


class LojaOut(BaseModel):
    """Dados públicos de uma loja."""

    id: int
    nome: str
    url_base: str
    logo_url: str | None = None
    tipo_fonte: str = "scraper"
    icone: str | None = None

    model_config = {"from_attributes": True}


# --- Produto ---


class ProdutoOut(BaseModel):
    """Produto na listagem com menor preço agregado."""

    id: int
    nome: str
    tipo: TipoBebida
    subtipo: str | None = None
    marca: str | None = None
    volume_ml: int | None = None
    teor_alcoolico: float | None = None
    imagem_url: str | None = None
    artesanal: bool = False
    menor_preco: float | None = None
    loja_menor_preco: str | None = None
    url_oferta: str | None = None
    url_redirecionamento: str | None = None
    loja_icone: str | None = None

    model_config = {"from_attributes": True}


class ProdutoDetalhe(ProdutoOut):
    """Produto com lista de preços completa."""

    descricao: str | None = None
    palavras_chave: str | None = None
    precos: list["PrecoOut"] = []


# --- Preço ---


class PrecoOut(BaseModel):
    """Preço de um produto em uma loja."""

    id: int
    valor: float
    valor_original: float | None = None
    url_oferta: str
    url_redirecionamento: str | None = None
    em_promocao: bool
    coletado_em: datetime
    loja: LojaOut

    model_config = {"from_attributes": True}


# --- Busca/Filtros ---


class BuscaParams(BaseModel):
    """Parâmetros de busca com validação automática."""

    q: str | None = None
    tipo: TipoBebida | None = None
    subtipo: str | None = None
    marca: str | None = None
    preco_min: float | None = Field(None, ge=0)
    preco_max: float | None = Field(None, ge=0)
    em_promocao: bool | None = None
    artesanal: bool | None = None
    ordenar_por: OrdenarPor = OrdenarPor.MENOR_PRECO
    pagina: int = Field(1, ge=1)
    por_pagina: int = Field(20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_faixa_preco(self) -> Self:
        """Garante que preco_min <= preco_max."""
        if (
            self.preco_min is not None
            and self.preco_max is not None
            and self.preco_min > self.preco_max
        ):
            msg = "preco_min não pode ser maior que preco_max"
            raise ValueError(msg)
        return self


class PaginacaoOut(BaseModel):
    """Resposta paginada."""

    items: list[ProdutoOut]
    total: int
    pagina: int
    paginas: int
