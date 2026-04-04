"use client";

import { useState } from "react";
import { REGIOES } from "@/lib/mock-data";

interface RegionSelectorProps {
  onSelect?: (estado: string, cidade: string) => void;
}

export function RegionSelector({ onSelect }: RegionSelectorProps) {
  const [open, setOpen] = useState(false);
  const [estado, setEstado] = useState<string | null>(null);
  const [cidade, setCidade] = useState<string>("São Paulo");
  const [sigla, setSigla] = useState("SP");

  const cidadesDoEstado = REGIOES.find((r) => r.sigla === (estado ?? sigla))?.cidades ?? [];

  function selecionarEstado(s: string) {
    const regiao = REGIOES.find((r) => r.sigla === s);
    if (!regiao) return;
    setEstado(s);
    setSigla(s);
    setCidade(regiao.cidades[0]);
    onSelect?.(regiao.estado, regiao.cidades[0]);
  }

  function selecionarCidade(c: string) {
    setCidade(c);
    setOpen(false);
    const regiao = REGIOES.find((r) => r.sigla === sigla);
    if (regiao) onSelect?.(regiao.estado, c);
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-sm font-medium text-brand-teal hover:text-brand-teal-dark transition-colors"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
        <span>{cidade}, {sigla}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute top-8 left-0 z-50 w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-4 space-y-3">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</p>
            <div className="flex flex-wrap gap-1.5">
              {REGIOES.map((r) => (
                <button
                  key={r.sigla}
                  onClick={() => selecionarEstado(r.sigla)}
                  className={`chip ${r.sigla === sigla ? "chip-active" : "chip-inactive"}`}
                >
                  {r.sigla}
                </button>
              ))}
            </div>

            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide pt-1">Cidade</p>
            <div className="flex flex-col gap-1 max-h-36 overflow-y-auto">
              {cidadesDoEstado.map((c) => (
                <button
                  key={c}
                  onClick={() => selecionarCidade(c)}
                  className={`text-left text-sm px-3 py-1.5 rounded-lg transition-colors ${
                    c === cidade
                      ? "bg-brand-teal/10 text-brand-teal font-medium"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
