"use client";

import { Suspense, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { ProductCard } from "@/components/ProductCard";
import { SearchFilters } from "@/components/SearchFilters";
import { PriceSlider } from "@/components/PriceSlider";
import { MOCK_PRODUTOS } from "@/lib/mock-data";
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

  const [params, setParams] = useState<BuscaParams>({
    q: searchParams.get("q") ?? undefined,
    tipo: (searchParams.get("tipo") as TipoBebida) ?? undefined,
    em_promocao: searchParams.get("em_promocao") === "true" || undefined,
    ordenar_por: "menor_preco",
    pagina: 1,
    por_pagina: 20,
  });

  const [priceRange, setPriceRange] = useState<[number, number]>([0, 200]);

  // Client-side filtering on mock data
  const filtered = useMemo(() => {
    let items = [...MOCK_PRODUTOS];

    if (params.q) {
      const q = params.q.toLowerCase();
      items = items.filter(
        (p) => p.nome.toLowerCase().includes(q) || p.marca?.toLowerCase().includes(q)
      );
    }
    if (params.tipo) {
      items = items.filter((p) => p.tipo === params.tipo);
    }
    if (priceRange[0] > 0 || priceRange[1] < 200) {
      items = items.filter(
        (p) => p.menor_preco && p.menor_preco >= priceRange[0] && p.menor_preco <= priceRange[1]
      );
    }

    // Sort
    items.sort((a, b) => (a.menor_preco ?? 999) - (b.menor_preco ?? 999));

    return items;
  }, [params.q, params.tipo, priceRange]);

  return (
    <div className="space-y-5 pt-4">
      <h1 className="text-xl font-bold text-gray-800">Buscar</h1>

      <SearchFilters params={params} onChange={setParams} />

      {/* Price slider */}
      <div className="card p-4">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Faixa de preço</p>
        <PriceSlider value={priceRange} onChange={setPriceRange} />
      </div>

      {/* Results */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          {filtered.length} resultado{filtered.length !== 1 ? "s" : ""}
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

      {filtered.length > 0 ? (
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2">
          {filtered.map((p) => (
            <ProductCard key={p.id} produto={p} />
          ))}
        </div>
      ) : (
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
      )}
    </div>
  );
}
