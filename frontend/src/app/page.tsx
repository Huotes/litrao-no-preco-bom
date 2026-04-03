"use client";

import { useEffect, useState } from "react";

import { ProductCard } from "@/components/ProductCard";
import { SearchFilters } from "@/components/SearchFilters";
import { useBusca } from "@/hooks/useBusca";
import type { BuscaParams } from "@/types/produto";

const INITIAL_PARAMS: BuscaParams = {
  pagina: 1,
  por_pagina: 20,
  ordenar_por: "menor_preco",
};

export default function HomePage() {
  const [params, setParams] = useState<BuscaParams>(INITIAL_PARAMS);
  const { data, loading, error, buscar } = useBusca();

  useEffect(() => {
    buscar(params);
  }, [params, buscar]);

  return (
    <div className="space-y-6">
      <section className="text-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          Encontre a melhor bebida pelo menor preço
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Comparamos preços de diversas lojas para você economizar
        </p>
      </section>

      <SearchFilters params={params} onChange={setParams} />

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}

      {loading && (
        <div className="py-8 text-center text-gray-400">Buscando...</div>
      )}

      {data && !loading && (
        <>
          <p className="text-sm text-gray-500">
            {data.total} resultado{data.total !== 1 ? "s" : ""} encontrado
            {data.total !== 1 ? "s" : ""}
          </p>

          <div className="grid gap-3 sm:grid-cols-2">
            {data.items.map((produto) => (
              <ProductCard key={produto.id} produto={produto} />
            ))}
          </div>

          {data.paginas > 1 && (
            <div className="flex justify-center gap-2">
              <button
                disabled={params.pagina === 1}
                onClick={() => setParams((p) => ({ ...p, pagina: (p.pagina ?? 1) - 1 }))}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-40 dark:border-gray-700"
              >
                Anterior
              </button>
              <span className="px-3 py-1 text-sm text-gray-500">
                {data.pagina} / {data.paginas}
              </span>
              <button
                disabled={data.pagina >= data.paginas}
                onClick={() => setParams((p) => ({ ...p, pagina: (p.pagina ?? 1) + 1 }))}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-40 dark:border-gray-700"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}

      {data && data.items.length === 0 && !loading && (
        <div className="py-12 text-center text-gray-400">
          Nenhum produto encontrado com esses filtros.
        </div>
      )}
    </div>
  );
}
