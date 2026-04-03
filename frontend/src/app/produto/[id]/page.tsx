"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { obterProduto } from "@/lib/api";
import { formatarPreco, formatarVolume, TIPO_LABELS } from "@/lib/format";
import { ProductImage } from "@/components/ProductImage";
import { TipoBadge } from "@/components/TipoBadge";
import type { ProdutoDetalhe } from "@/types/produto";

function isValidUrl(url: string): boolean {
  return url.startsWith("https://") || url.startsWith("http://");
}

export default function ProdutoPage() {
  const { id } = useParams<{ id: string }>();
  const [produto, setProduto] = useState<ProdutoDetalhe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
    return <div className="py-12 text-center text-gray-400">Carregando...</div>;
  }

  if (error || !produto) {
    return (
      <div className="py-12 text-center text-red-500">
        {error ?? "Produto não encontrado"}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/" className="text-sm text-amber-600 hover:underline">
        &larr; Voltar à busca
      </Link>

      <div className="flex flex-col gap-6 sm:flex-row">
        <ProductImage src={produto.imagem_url} alt={produto.nome} size="lg" />

        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {produto.nome}
          </h1>

          <div className="mt-2 flex flex-wrap gap-2 text-sm text-gray-500 dark:text-gray-400">
            <TipoBadge tipo={produto.tipo} />
            {produto.marca && <span>Marca: {produto.marca}</span>}
            {produto.volume_ml && <span>{formatarVolume(produto.volume_ml)}</span>}
            {produto.teor_alcoolico && <span>{produto.teor_alcoolico}% vol</span>}
          </div>

          {produto.descricao && (
            <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
              {produto.descricao}
            </p>
          )}
        </div>
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-800 dark:text-gray-200">
          Preços encontrados ({produto.precos.length})
        </h2>

        {produto.precos.length === 0 ? (
          <p className="text-sm text-gray-400">Nenhum preço disponível no momento.</p>
        ) : (
          <div className="space-y-2">
            {produto.precos.map((preco, idx) => {
              const linkProps = isValidUrl(preco.url_oferta)
                ? { href: preco.url_oferta, target: "_blank" as const, rel: "noopener noreferrer" }
                : { href: "#" };

              return (
                <a
                  key={preco.id}
                  {...linkProps}
                  className="flex items-center justify-between rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800/50"
                >
                  <div>
                    <span className="font-medium text-gray-800 dark:text-gray-200">
                      {preco.loja.nome}
                    </span>
                    {preco.em_promocao && (
                      <span className="ml-2 rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                        Promoção
                      </span>
                    )}
                    <div className="mt-1 text-xs text-gray-400">
                      Coletado em{" "}
                      {new Date(preco.coletado_em).toLocaleDateString("pt-BR")}
                    </div>
                  </div>

                  <div className="text-right">
                    <span
                      className={`text-lg font-bold ${
                        idx === 0
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-700 dark:text-gray-300"
                      }`}
                    >
                      {formatarPreco(preco.valor)}
                    </span>
                    {preco.valor_original && preco.valor_original > preco.valor && (
                      <div className="text-xs text-gray-400 line-through">
                        {formatarPreco(preco.valor_original)}
                      </div>
                    )}
                  </div>
                </a>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
