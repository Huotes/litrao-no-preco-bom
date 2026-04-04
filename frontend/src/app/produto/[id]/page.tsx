"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { obterProduto } from "@/lib/api";
import { formatarPreco, formatarVolume, TIPO_ICONS } from "@/lib/format";
import { TipoBadge } from "@/components/TipoBadge";
import type { ProdutoDetalhe } from "@/types/produto";

export default function ProdutoPage() {
  const { id } = useParams<{ id: string }>();
  const [produto, setProduto] = useState<ProdutoDetalhe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFav, setIsFav] = useState(false);

  useEffect(() => {
    if (!id) return;
    const numId = Number(id);
    if (Number.isNaN(numId) || numId <= 0) {
      setError("ID inválido");
      setLoading(false);
      return;
    }
    setLoading(true);
    obterProduto(numId)
      .then(setProduto)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="py-16 text-center text-gray-400">Carregando...</div>;
  }

  if (error || !produto) {
    return (
      <div className="py-16 text-center">
        <p className="text-4xl mb-3">😕</p>
        <p className="text-gray-500">{error ?? "Produto não encontrado"}</p>
        <Link href="/" className="btn-primary inline-block mt-4 text-sm">Voltar ao início</Link>
      </div>
    );
  }

  const icon = TIPO_ICONS[produto.tipo] ?? "🍾";
  const precos = produto.precos ?? [];

  return (
    <div className="space-y-5 pt-4">
      {/* Back + fav */}
      <div className="flex items-center justify-between">
        <Link href="/" className="flex items-center gap-1 text-sm text-brand-teal hover:underline">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>
          Voltar
        </Link>
        <button
          onClick={() => setIsFav(!isFav)}
          className="w-10 h-10 rounded-full bg-white shadow-card flex items-center justify-center transition-transform active:scale-90"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill={isFav ? "#FF6B6B" : "none"} stroke={isFav ? "#FF6B6B" : "#ccc"} strokeWidth="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        </button>
      </div>

      {/* Product hero */}
      <div className="card p-6 text-center">
        <div className="w-24 h-24 mx-auto rounded-2xl bg-brand-teal/5 flex items-center justify-center text-5xl mb-4">
          {icon}
        </div>
        <h1 className="text-xl font-bold text-gray-800">{produto.nome}</h1>
        <div className="mt-2 flex items-center justify-center gap-2 flex-wrap">
          <TipoBadge tipo={produto.tipo} />
          {produto.marca && <span className="text-xs text-gray-400">{produto.marca}</span>}
          {produto.volume_ml && <span className="text-xs text-gray-400">{formatarVolume(produto.volume_ml)}</span>}
          {produto.teor_alcoolico && <span className="text-xs text-gray-400">{produto.teor_alcoolico}% vol</span>}
        </div>
        {produto.menor_preco && (
          <div className="mt-4">
            <p className="text-xs text-gray-400">melhor preço</p>
            <p className="text-3xl font-bold text-brand-teal">{formatarPreco(produto.menor_preco)}</p>
          </div>
        )}
      </div>

      {/* Prices */}
      <section>
        <h2 className="section-title mb-3">Preços encontrados ({precos.length})</h2>
        {precos.length === 0 ? (
          <p className="text-sm text-gray-400">Nenhum preço disponível no momento.</p>
        ) : (
          <div className="space-y-2">
            {precos.map((preco, idx) => (
              <div
                key={preco.id}
                className={`card p-4 flex items-center justify-between ${idx === 0 ? "ring-2 ring-brand-teal/20" : ""}`}
              >
                <div>
                  <span className="text-sm font-medium text-gray-800">{preco.loja.nome}</span>
                  {preco.em_promocao && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded-full bg-brand-green/10 text-brand-green-dark uppercase">
                      Promoção
                    </span>
                  )}
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    Atualizado em {new Date(preco.coletado_em).toLocaleDateString("pt-BR")}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-lg font-bold ${idx === 0 ? "text-brand-teal" : "text-gray-700"}`}>
                    {formatarPreco(preco.valor)}
                  </span>
                  {preco.valor_original && preco.valor_original > preco.valor && (
                    <p className="text-xs text-gray-400 line-through">{formatarPreco(preco.valor_original)}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
