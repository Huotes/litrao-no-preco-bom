"use client";

import { useState } from "react";
import Link from "next/link";

import { ProductCard } from "@/components/ProductCard";
import { RegionSelector } from "@/components/RegionSelector";
import { SectionHeader } from "@/components/SectionHeader";
import { MOCK_PRODUTOS, PROMOCOES, MAIS_PEDIDOS } from "@/lib/mock-data";
import { TIPO_LABELS, TIPO_ICONS } from "@/lib/format";
import type { TipoBebida } from "@/types/produto";

const CATEGORIAS = Object.entries(TIPO_LABELS).slice(0, 5) as [TipoBebida, string][];

export default function HomePage() {
  const [recentSearches] = useState(["Heineken", "Vinho tinto", "Gin"]);

  return (
    <div className="space-y-6 pt-4">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gradient">Litrão no Preço Bom</h1>
          <RegionSelector />
        </div>
        <Link
          href="/perfil"
          className="w-10 h-10 rounded-full bg-brand-teal/10 flex items-center justify-center text-brand-teal hover:bg-brand-teal/20 transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="8" r="4" /><path d="M20 21a8 8 0 0 0-16 0" />
          </svg>
        </Link>
      </header>

      {/* Search bar */}
      <Link href="/busca" className="block">
        <div className="input-field flex items-center gap-2.5 text-gray-400 cursor-pointer hover:border-brand-teal/40 transition-colors">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.35-4.35" />
          </svg>
          <span className="text-sm">Buscar bebida, marca...</span>
        </div>
      </Link>

      {/* Recent searches */}
      {recentSearches.length > 0 && (
        <div className="flex gap-1.5 flex-wrap">
          <span className="text-xs text-gray-400 mr-1 self-center">Recentes:</span>
          {recentSearches.map((term) => (
            <Link
              key={term}
              href={`/busca?q=${encodeURIComponent(term)}`}
              className="chip chip-inactive text-[11px]"
            >
              {term}
            </Link>
          ))}
        </div>
      )}

      {/* Categories */}
      <section>
        <SectionHeader title="Categorias" emoji="📋" />
        <div className="mt-3 grid grid-cols-5 gap-2">
          {CATEGORIAS.map(([tipo, label]) => (
            <Link
              key={tipo}
              href={`/busca?tipo=${tipo}`}
              className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-white shadow-card hover:shadow-card-hover transition-shadow"
            >
              <span className="text-2xl">{TIPO_ICONS[tipo]}</span>
              <span className="text-[10px] font-medium text-gray-600 text-center leading-tight">{label}</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Promotions horizontal scroll */}
      <section>
        <SectionHeader title="Promoções" emoji="🔥" href="/busca?em_promocao=true" />
        <div className="mt-3 flex gap-3 overflow-x-auto pb-2 no-scrollbar">
          {PROMOCOES.map((p) => (
            <div key={p.id} className="min-w-[220px] max-w-[220px]">
              <ProductCard produto={p} />
            </div>
          ))}
        </div>
      </section>

      {/* Stats banner */}
      <section className="gradient-hero rounded-2xl p-5 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium opacity-90">Preços monitorados</p>
            <p className="text-3xl font-bold mt-1">{MOCK_PRODUTOS.length * 3}+</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium opacity-90">Lojas</p>
            <p className="text-3xl font-bold mt-1">6</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium opacity-90">Economia média</p>
            <p className="text-3xl font-bold mt-1">23%</p>
          </div>
        </div>
      </section>

      {/* Most ordered */}
      <section>
        <SectionHeader title="Mais pedidos" emoji="⭐" href="/busca?ordenar_por=mais_pedidos" />
        <div className="mt-3 grid gap-3 grid-cols-1 sm:grid-cols-2">
          {MAIS_PEDIDOS.slice(0, 4).map((p) => (
            <ProductCard key={p.id} produto={p} />
          ))}
        </div>
      </section>

      {/* All products preview */}
      <section>
        <SectionHeader title="Todos os produtos" emoji="🍾" href="/busca" />
        <div className="mt-3 grid gap-3 grid-cols-1 sm:grid-cols-2">
          {MOCK_PRODUTOS.slice(0, 6).map((p) => (
            <ProductCard key={p.id} produto={p} />
          ))}
        </div>
        <Link href="/busca" className="btn-outline block text-center mt-4 text-sm">
          Ver todos os {MOCK_PRODUTOS.length} produtos
        </Link>
      </section>
    </div>
  );
}
