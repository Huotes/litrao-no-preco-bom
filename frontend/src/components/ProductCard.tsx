import Link from "next/link";

import { formatarPreco, formatarVolume } from "@/lib/format";
import { ProductImage } from "@/components/ProductImage";
import { TipoBadge } from "@/components/TipoBadge";
import type { Produto } from "@/types/produto";

interface ProductCardProps {
  produto: Produto;
}

export function ProductCard({ produto }: ProductCardProps) {
  const menorPreco =
    produto.menor_preco && produto.menor_preco > 0
      ? produto.menor_preco
      : null;

  return (
    <Link
      href={`/produto/${produto.id}`}
      className="block rounded-lg border border-gray-200 p-4 transition-shadow hover:shadow-md dark:border-gray-700"
    >
      <div className="flex gap-4">
        <ProductImage src={produto.imagem_url} alt={produto.nome} size="sm" />

        <div className="flex-1 min-w-0">
          <h3 className="truncate font-medium text-gray-900 dark:text-gray-100">
            {produto.nome}
          </h3>

          <div className="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <TipoBadge tipo={produto.tipo} />
            {produto.marca && <span>{produto.marca}</span>}
            {produto.volume_ml && (
              <span>{formatarVolume(produto.volume_ml)}</span>
            )}
          </div>

          <div className="mt-2 flex items-baseline gap-2">
            {menorPreco ? (
              <>
                <span className="text-lg font-bold text-green-600 dark:text-green-400">
                  {formatarPreco(menorPreco)}
                </span>
                {produto.loja_menor_preco && (
                  <span className="text-xs text-gray-400">
                    em {produto.loja_menor_preco}
                  </span>
                )}
              </>
            ) : (
              <span className="text-sm text-gray-400">Sem preço</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
