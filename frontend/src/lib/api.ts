import type { BuscaParams, PaginacaoResponse, ProdutoDetalhe } from "@/types/produto";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetcher<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, value);
      }
    });
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    throw new ApiError(response.status, `Erro ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function toStringParams(params: BuscaParams): Record<string, string> {
  const result: Record<string, string> = {};

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      result[key] = String(value);
    }
  });

  return result;
}

export async function buscarProdutos(params: BuscaParams): Promise<PaginacaoResponse> {
  return fetcher<PaginacaoResponse>("/produtos/", toStringParams(params));
}

export async function obterProduto(id: number): Promise<ProdutoDetalhe> {
  return fetcher<ProdutoDetalhe>(`/produtos/${id}`);
}

export async function listarTipos(): Promise<string[]> {
  return fetcher<string[]>("/produtos/tipos/");
}
