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

async function fetcher<T>(path: string, params?: Record<string, string>, signal?: AbortSignal): Promise<T> {
  const url = `${API_BASE}${path}`;
  const searchParams = new URLSearchParams();

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== "") {
        searchParams.set(key, value);
      }
    }
  }

  const fullUrl = searchParams.toString() ? `${url}?${searchParams}` : url;
  const response = await fetch(fullUrl, { signal });

  if (!response.ok) {
    throw new ApiError(response.status, `Erro ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function toStringParams(params: BuscaParams): Record<string, string> {
  const result: Record<string, string> = {};

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== false) {
      result[key] = String(value);
    }
  }

  return result;
}

export async function buscarProdutos(params: BuscaParams, signal?: AbortSignal): Promise<PaginacaoResponse> {
  return fetcher<PaginacaoResponse>("/produtos/", toStringParams(params), signal);
}

export async function obterProduto(id: number): Promise<ProdutoDetalhe> {
  return fetcher<ProdutoDetalhe>(`/produtos/${id}`);
}

export async function listarTipos(): Promise<string[]> {
  return fetcher<string[]>("/produtos/tipos/");
}
