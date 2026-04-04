"use client";

import { useState } from "react";

import { ProductCard } from "@/components/ProductCard";
import { MOCK_PRODUTOS } from "@/lib/mock-data";

const INITIAL_FAVS = MOCK_PRODUTOS.filter((_, i) => [2, 3, 8, 11, 15].includes(i));

export default function FavoritosPage() {
  const [favoritos] = useState(INITIAL_FAVS);
  const [tab, setTab] = useState<"favoritos" | "recentes">("favoritos");

  const recentes = MOCK_PRODUTOS.slice(0, 5);

  const items = tab === "favoritos" ? favoritos : recentes;

  return (
    <div className="space-y-5 pt-4">
      <h1 className="text-xl font-bold text-gray-800">Meus itens</h1>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setTab("favoritos")}
          className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
            tab === "favoritos"
              ? "bg-white text-brand-teal shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          ❤️ Favoritos ({favoritos.length})
        </button>
        <button
          onClick={() => setTab("recentes")}
          className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
            tab === "recentes"
              ? "bg-white text-brand-teal shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          🕐 Vistos recente
        </button>
      </div>

      {items.length > 0 ? (
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2">
          {items.map((p) => (
            <ProductCard key={p.id} produto={p} />
          ))}
        </div>
      ) : (
        <div className="py-16 text-center">
          <p className="text-4xl mb-3">{tab === "favoritos" ? "❤️" : "🕐"}</p>
          <p className="text-gray-500 text-sm">
            {tab === "favoritos"
              ? "Nenhum favorito ainda. Explore produtos e toque no coração!"
              : "Nenhum produto visto recentemente."}
          </p>
        </div>
      )}
    </div>
  );
}
