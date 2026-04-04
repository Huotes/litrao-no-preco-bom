"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { obterProduto } from "@/lib/api";
import { formatarPreco, formatarVolume } from "@/lib/format";
import { TipoBadge } from "@/components/TipoBadge";
import { ProductImage } from "@/components/ProductImage";
import { StoreIcon } from "@/components/StoreIcon";
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
        <p className="text-gray-500 text-lg mb-2">Produto não encontrado</p>
        <p className="text-gray-400 text-sm">{error}</p>
        <Link href="/" className="btn-primary inline-block mt-4 text-sm">Voltar ao início</Link>
      </div>
    );
  }

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
        <div className="mx-auto mb-4 flex items-center justify-center">
          <ProductImage src={produto.imagem_url} alt={produto.nome} tipo={produto.tipo} size="lg" />
        </div>
        <h1 className="text-xl font-bold text-gray-800">{produto.nome}</h1>
        <div className="mt-2 flex items-center justify-center gap-2 flex-wrap">
          <TipoBadge tipo={produto.tipo} />
          {produto.artesanal && (
            <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">
              Artesanal
            </span>
          )}
          {produto.marca && <span className="text-xs text-gray-400">{produto.marca}</span>}
          {produto.volume_ml && <span className="text-xs text-gray-400">{formatarVolume(produto.volume_ml)}</span>}
          {produto.teor_alcoolico && <span className="text-xs text-gray-400">{produto.teor_alcoolico}% vol</span>}
        </div>

        {produto.descricao && (
          <p className="mt-3 text-sm text-gray-500 leading-relaxed">{produto.descricao}</p>
        )}

        {produto.menor_preco && (
          <div className="mt-4">
            <p className="text-xs text-gray-400">melhor preço</p>
            <p className="text-3xl font-bold text-brand-teal">{formatarPreco(produto.menor_preco)}</p>
            {produto.loja_menor_preco && (
              <p className="text-xs text-gray-400 mt-1 flex items-center justify-center gap-1.5">
                <StoreIcon src={produto.loja_icone} nome={produto.loja_menor_preco} size={16} />
                {produto.loja_menor_preco}
              </p>
            )}
          </div>
        )}

        {/* Botão de redirecionamento principal */}
        {produto.url_redirecionamento && (
          <a
            href={produto.url_redirecionamento}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 btn-primary inline-flex items-center gap-2 text-sm"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Ir para a oferta
          </a>
        )}
      </div>

      {/* Prices list — estilo Google Shopping */}
      <section>
        <h2 className="section-title mb-3">Preços encontrados ({precos.length})</h2>
        {precos.length === 0 ? (
          <p className="text-sm text-gray-400">Nenhum preço disponível no momento.</p>
        ) : (
          <div className="space-y-2">
            {precos.map((preco, idx) => (
              <a
                key={preco.id}
                href={preco.url_redirecionamento ?? preco.url_oferta}
                target="_blank"
                rel="noopener noreferrer"
                className={`card p-4 flex items-center justify-between hover:shadow-md transition-shadow ${idx === 0 ? "ring-2 ring-brand-teal/20" : ""}`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <StoreIcon src={preco.loja.icone} nome={preco.loja.nome} size={20} />
                    <span className="text-sm font-medium text-gray-800">
                      {preco.loja.nome}
                    </span>
                    {preco.em_promocao && (
                      <span className="inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded-full bg-brand-green/10 text-brand-green-dark uppercase">
                        Promo
                      </span>
                    )}
                    {idx === 0 && (
                      <span className="inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded-full bg-brand-teal/10 text-brand-teal uppercase">
                        Menor
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-gray-400 mt-0.5 truncate">
                    {preco.url_oferta.replace(/^https?:\/\//, "").split("/")[0]}
                    {" · "}
                    {new Date(preco.coletado_em).toLocaleDateString("pt-BR")}
                  </p>
                </div>
                <div className="text-right flex-shrink-0 ml-3">
                  <span className={`text-lg font-bold ${idx === 0 ? "text-brand-teal" : "text-gray-700"}`}>
                    {formatarPreco(preco.valor)}
                  </span>
                  {preco.valor_original && preco.valor_original > preco.valor && (
                    <p className="text-xs text-gray-400 line-through">{formatarPreco(preco.valor_original)}</p>
                  )}
                </div>
                <svg className="ml-2 flex-shrink-0 text-gray-300" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </a>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
