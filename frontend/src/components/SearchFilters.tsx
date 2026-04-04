"use client";

import { TIPO_LABELS, TIPO_ICONS } from "@/lib/format";
import type { BuscaParams, TipoBebida } from "@/types/produto";

interface SearchFiltersProps {
  params: BuscaParams;
  onChange: (params: BuscaParams) => void;
}

const TIPOS = Object.keys(TIPO_LABELS) as TipoBebida[];

export function SearchFilters({ params, onChange }: SearchFiltersProps) {
  function update(partial: Partial<BuscaParams>) {
    onChange({ ...params, ...partial, pagina: 1 });
  }

  return (
    <div className="space-y-3">
      {/* Search input */}
      <div className="relative">
        <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.35-4.35" />
        </svg>
        <input
          type="text"
          placeholder="Buscar bebida, marca..."
          value={params.q ?? ""}
          onChange={(e) => update({ q: e.target.value || undefined })}
          className="input-field pl-10"
        />
      </div>

      {/* Type chips */}
      <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        <button
          onClick={() => update({ tipo: undefined })}
          className={`chip whitespace-nowrap ${!params.tipo ? "chip-active" : "chip-inactive"}`}
        >
          Todos
        </button>
        {TIPOS.map((tipo) => (
          <button
            key={tipo}
            onClick={() => update({ tipo: params.tipo === tipo ? undefined : tipo })}
            className={`chip whitespace-nowrap ${params.tipo === tipo ? "chip-active" : "chip-inactive"}`}
          >
            <span className="mr-1">{TIPO_ICONS[tipo]}</span>
            {TIPO_LABELS[tipo]}
          </button>
        ))}
      </div>

      {/* Price + Promo row */}
      <div className="flex gap-2 items-center">
        <input
          type="number"
          placeholder="Mín R$"
          value={params.preco_min ?? ""}
          onChange={(e) => update({ preco_min: e.target.value ? Number(e.target.value) : undefined })}
          className="input-field w-24 text-center"
          min={0}
          step={1}
        />
        <span className="text-gray-300">—</span>
        <input
          type="number"
          placeholder="Máx R$"
          value={params.preco_max ?? ""}
          onChange={(e) => update({ preco_max: e.target.value ? Number(e.target.value) : undefined })}
          className="input-field w-24 text-center"
          min={0}
          step={1}
        />
        <button
          onClick={() => update({ em_promocao: params.em_promocao ? undefined : true })}
          className={`chip whitespace-nowrap ${params.em_promocao ? "bg-brand-orange text-white" : "chip-inactive"}`}
        >
          🔥 Promoções
        </button>
        <button
          onClick={() => update({ artesanal: params.artesanal ? undefined : true })}
          className={`chip whitespace-nowrap ${params.artesanal ? "bg-amber-500 text-white" : "chip-inactive"}`}
        >
          🍻 Artesanal
        </button>
      </div>
    </div>
  );
}
