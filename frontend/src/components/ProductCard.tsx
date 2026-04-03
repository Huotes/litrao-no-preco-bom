import Link from "next/link";

import { formatarPreco, formatarVolume, TIPO_LABELS } from "@/lib/format";
import type { Produto } from "@/types/produto";

interface ProductCardProps {
  produto: Produto;
}

export function ProductCard({ produto }: ProductCardProps) {
  const desconto =
    produto.menor_preco && produto.menor_preco > 0
      ? produto.menor_preco
      : null;

  return (
    <Link
      href={`/produto/${produto.id}`}
      className="block rounded-lg border border-gray-200 p-4 transition-shadow hover:shadow-md dark:border-gray-700"
    >
      <div className="flex gap-4">
        {produto.imagem_url && (
          <div className="h-20 w-20 flex-shrink-0 overflow-hidden rounded bg-gray-100 dark:bg-gray-800">
            <img
              src={produto.imagem_url}
              alt={produto.nome}
              className="h-full w-full object-contain"
            />
          </div>
        )}

        <div className="flex-1 min-w-0">
          <h3 className="truncate font-medium text-gray-900 dark:text-gray-100">
            {produto.nome}
          </h3>

          <div className="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
              {TIPO_LABELS[produto.tipo] ?? produto.tipo}
            </span>
            {produto.marca && <span>{produto.marca}</span>}
            {produto.volume_ml && (
              <span>{formatarVolume(produto.volume_ml)}</span>
            )}
          </div>

          <div className="mt-2 flex items-baseline gap-2">
            {desconto ? (
              <>
                <span className="text-lg font-bold text-green-600 dark:text-green-400">
                  {formatarPreco(desconto)}
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
