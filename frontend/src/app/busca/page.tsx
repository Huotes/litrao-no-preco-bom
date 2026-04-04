"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { ProductCard } from "@/components/ProductCard";
import { SearchFilters } from "@/components/SearchFilters";
import { PriceSlider } from "@/components/PriceSlider";
import { useBusca } from "@/hooks/useBusca";
import type { BuscaParams, TipoBebida } from "@/types/produto";

export default function BuscaPage() {
  return (
    <Suspense fallback={<div className="py-16 text-center text-gray-400">Carregando...</div>}>
      <BuscaContent />
    </Suspense>
  );
}

function BuscaContent() {
  const searchParams = useSearchParams();
  const { data, loading, error, buscar } = useBusca();

  const [params, setParams] = useState<BuscaParams>({
    q: searchParams.get("q") ?? undefined,
    tipo: (searchParams.get("tipo") as TipoBebida) ?? undefined,
    em_promocao: searchParams.get("em_promocao") === "true" || undefined,
    ordenar_por: "menor_preco",
    pagina: 1,
    por_pagina: 20,
  });

  const [priceRange, setPriceRange] = useState<[number, number]>([0, 200]);

  useEffect(() => {
    const fullParams: BuscaParams = {
      ...params,
      preco_min: priceRange[0] > 0 ? priceRange[0] : undefined,
      preco_max: priceRange[1] < 200 ? priceRange[1] : undefined,
    };
    buscar(fullParams);
  }, [params, priceRange, buscar]);

  const items = data?.items ?? [];

  return (
    <div className="space-y-5 pt-4">
      <h1 className="text-xl font-bold text-gray-800">Buscar</h1>

      <SearchFilters params={params} onChange={setParams} />

      {/* Price slider */}
      <div className="card p-4">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Faixa de preço</p>
        <PriceSlider value={priceRange} onChange={setPriceRange} />
      </div>

      {/* Results header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          {loading ? "Buscando..." : `${data?.total ?? 0} resultado${(data?.total ?? 0) !== 1 ? "s" : ""}`}
        </p>
        <select
          value={params.ordenar_por}
          onChange={(e) => setParams((p) => ({ ...p, ordenar_por: e.target.value }))}
          className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 bg-white"
        >
          <option value="menor_preco">Menor preço</option>
          <option value="maior_preco">Maior preço</option>
          <option value="nome">Nome A-Z</option>
        </select>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">{error}</div>
      )}

      {items.length > 0 ? (
        <>
          <div className="grid gap-3 grid-cols-1 sm:grid-cols-2">
            {items.map((p) => (
              <ProductCard key={p.id} produto={p} />
            ))}
          </div>

          {data && data.paginas > 1 && (
            <div className="flex justify-center gap-2 pt-2">
              <button
                disabled={params.pagina === 1}
                onClick={() => setParams((p) => ({ ...p, pagina: (p.pagina ?? 1) - 1 }))}
                className="btn-outline text-xs px-4 py-2 disabled:opacity-40"
              >
                Anterior
              </button>
              <span className="px-3 py-2 text-xs text-gray-500">
                {data.pagina} / {data.paginas}
              </span>
              <button
                disabled={data.pagina >= data.paginas}
                onClick={() => setParams((p) => ({ ...p, pagina: (p.pagina ?? 1) + 1 }))}
                className="btn-outline text-xs px-4 py-2 disabled:opacity-40"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      ) : !loading ? (
        <div className="py-16 text-center">
          <p className="text-4xl mb-3">🔍</p>
          <p className="text-gray-500 text-sm">Nenhum produto encontrado com esses filtros.</p>
          <button
            onClick={() => { setParams({ pagina: 1, por_pagina: 20, ordenar_por: "menor_preco" }); setPriceRange([0, 200]); }}
            className="btn-outline text-sm mt-4"
          >
            Limpar filtros
          </button>
        </div>
      ) : null}
    </div>
  );
}
