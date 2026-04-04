"use client";

import { useState } from "react";
import Link from "next/link";
import { RegionSelector } from "@/components/RegionSelector";

const PREFS = [
  { key: "notif_promo", label: "Alertas de promoção", desc: "Receber notificações de ofertas" },
  { key: "notif_preco", label: "Alerta de queda de preço", desc: "Aviso quando um favorito baixar" },
  { key: "dark_mode", label: "Modo escuro", desc: "Tema escuro automático" },
];

export default function PerfilPage() {
  const [prefs, setPrefs] = useState<Record<string, boolean>>({
    notif_promo: true,
    notif_preco: false,
    dark_mode: false,
  });

  function toggle(key: string) {
    setPrefs((p) => ({ ...p, [key]: !p[key] }));
  }

  return (
    <div className="space-y-6 pt-4">
      <h1 className="text-xl font-bold text-gray-800">Perfil</h1>

      {/* Avatar + info */}
      <div className="card p-5 flex items-center gap-4">
        <div className="w-16 h-16 rounded-full gradient-teal flex items-center justify-center text-white text-2xl font-bold">
          H
        </div>
        <div>
          <p className="text-lg font-semibold text-gray-800">Huotes</p>
          <p className="text-sm text-gray-500">aureliodosol@gmail.com</p>
        </div>
      </div>

      {/* Region */}
      <div className="card p-4">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Região de busca</p>
        <RegionSelector />
      </div>

      {/* Preferences */}
      <div className="card p-4 space-y-4">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Preferências</p>
        {PREFS.map((pref) => (
          <div key={pref.key} className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">{pref.label}</p>
              <p className="text-xs text-gray-400">{pref.desc}</p>
            </div>
            <button
              onClick={() => toggle(pref.key)}
              className={`relative w-11 h-6 rounded-full transition-colors ${
                prefs[pref.key] ? "bg-brand-teal" : "bg-gray-200"
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform ${
                  prefs[pref.key] ? "translate-x-5" : ""
                }`}
              />
            </button>
          </div>
        ))}
      </div>

      {/* Bebidas favoritas tipos */}
      <div className="card p-4 space-y-3">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Tipos favoritos</p>
        <p className="text-xs text-gray-400">Selecione para personalizar recomendações</p>
        <div className="flex flex-wrap gap-2">
          {["🍺 Cerveja", "🍷 Vinho", "🥃 Destilado", "🍹 Drinks", "🧉 Prontos"].map((tipo) => (
            <button key={tipo} className="chip chip-inactive text-sm hover:bg-brand-teal/10 hover:text-brand-teal">
              {tipo}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <button className="w-full text-left card p-4 text-sm font-medium text-gray-700 flex items-center justify-between">
          Sobre o app
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
        </button>
        <button className="w-full text-left card p-4 text-sm font-medium text-gray-700 flex items-center justify-between">
          Termos de uso
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
        </button>
        <button className="w-full text-left card p-4 text-sm font-medium text-red-500 flex items-center justify-between">
          Sair
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
        </button>
      </div>

      <p className="text-center text-xs text-gray-300 pb-4">Litrão no Preço Bom v0.1.0</p>
    </div>
  );
}
