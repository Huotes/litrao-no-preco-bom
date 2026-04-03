"use client";

import { TIPO_LABELS } from "@/lib/format";
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
    <div className="flex flex-col gap-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <input
        type="text"
        placeholder="Buscar bebida..."
        value={params.q ?? ""}
        onChange={(e) => update({ q: e.target.value || undefined })}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
      />

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => update({ tipo: undefined })}
          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
            !params.tipo
              ? "bg-amber-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
          }`}
        >
          Todos
        </button>
        {TIPOS.map((tipo) => (
          <button
            key={tipo}
            onClick={() => update({ tipo: params.tipo === tipo ? undefined : tipo })}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              params.tipo === tipo
                ? "bg-amber-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
            }`}
          >
            {TIPO_LABELS[tipo]}
          </button>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="number"
          placeholder="Preço mín"
          value={params.preco_min ?? ""}
          onChange={(e) =>
            update({ preco_min: e.target.value ? Number(e.target.value) : undefined })
          }
          className="w-28 rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
          min={0}
          step={0.5}
        />
        <input
          type="number"
          placeholder="Preço máx"
          value={params.preco_max ?? ""}
          onChange={(e) =>
            update({ preco_max: e.target.value ? Number(e.target.value) : undefined })
          }
          className="w-28 rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
          min={0}
          step={0.5}
        />

        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={params.em_promocao ?? false}
            onChange={(e) =>
              update({ em_promocao: e.target.checked || undefined })
            }
            className="rounded"
          />
          Promoções
        </label>
      </div>
    </div>
  );
}
