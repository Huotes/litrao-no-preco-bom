"""Schemas Pydantic para serialização e validação."""

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

class LojaBase(BaseModel):
    nome: str
    url_base: str
    logo_url: str | None = None


class LojaOut(LojaBase):
    id: int

    model_config = {"from_attributes": True}


# --- Produto ---

class ProdutoBase(BaseModel):
    nome: str = Field(max_length=300)
    tipo: TipoBebida
    subtipo: str | None = None
    marca: str | None = None
    volume_ml: int | None = None
    teor_alcoolico: float | None = None
    imagem_url: str | None = None


class ProdutoOut(ProdutoBase):
    id: int
    menor_preco: float | None = None
    loja_menor_preco: str | None = None

    model_config = {"from_attributes": True}


class ProdutoDetalhe(ProdutoOut):
    descricao: str | None = None
    precos: list["PrecoOut"] = []


# --- Preço ---

class PrecoOut(BaseModel):
    id: int
    valor: float
    valor_original: float | None = None
    url_oferta: str
    em_promocao: bool
    coletado_em: datetime
    loja: LojaOut

    model_config = {"from_attributes": True}


# --- Busca/Filtros ---

class BuscaParams(BaseModel):
    q: str | None = None
    tipo: TipoBebida | None = None
    subtipo: str | None = None
    marca: str | None = None
    preco_min: float | None = Field(None, ge=0)
    preco_max: float | None = Field(None, ge=0)
    em_promocao: bool | None = None
    ordenar_por: OrdenarPor = OrdenarPor.MENOR_PRECO
    pagina: int = Field(1, ge=1)
    por_pagina: int = Field(20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_faixa_preco(self) -> Self:
        if (
            self.preco_min is not None
            and self.preco_max is not None
            and self.preco_min > self.preco_max
        ):
            msg = "preco_min não pode ser maior que preco_max"
            raise ValueError(msg)
        return self


class PaginacaoOut(BaseModel):
    items: list[ProdutoOut]
    total: int
    pagina: int
    paginas: int
