export type TipoBebida =
  | "cerveja"
  | "vinho"
  | "destilado"
  | "refrigerante_alcoolico"
  | "drink_pronto"
  | "outros";

export interface Loja {
  id: number;
  nome: string;
  url_base: string;
  logo_url: string | null;
  tipo_fonte: string;
  icone: string | null;
}

export interface Produto {
  id: number;
  nome: string;
  tipo: TipoBebida;
  subtipo: string | null;
  marca: string | null;
  volume_ml: number | null;
  teor_alcoolico: number | null;
  imagem_url: string | null;
  artesanal: boolean;
  menor_preco: number | null;
  loja_menor_preco: string | null;
  url_oferta: string | null;
  url_redirecionamento: string | null;
  loja_icone: string | null;
}

export interface Preco {
  id: number;
  valor: number;
  valor_original: number | null;
  url_oferta: string;
  url_redirecionamento: string | null;
  em_promocao: boolean;
  coletado_em: string;
  loja: Loja;
}

export interface ProdutoDetalhe extends Produto {
  descricao: string | null;
  palavras_chave: string | null;
  precos: Preco[];
}

export interface PaginacaoResponse {
  items: Produto[];
  total: number;
  pagina: number;
  paginas: number;
}

export interface BuscaParams {
  q?: string;
  tipo?: TipoBebida;
  subtipo?: string;
  marca?: string;
  preco_min?: number;
  preco_max?: number;
  em_promocao?: boolean;
  artesanal?: boolean;
  ordenar_por?: string;
  pagina?: number;
  por_pagina?: number;
}

export interface Regiao {
  estado: string;
  sigla: string;
  cidades: string[];
}
