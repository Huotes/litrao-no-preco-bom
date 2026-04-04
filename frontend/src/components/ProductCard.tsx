import Link from "next/link";

import { formatarPreco, formatarVolume } from "@/lib/format";
import { TipoBadge } from "@/components/TipoBadge";
import { ProductImage } from "@/components/ProductImage";
import { StoreIcon } from "@/components/StoreIcon";
import type { Produto } from "@/types/produto";

interface ProductCardProps {
  produto: Produto;
  compact?: boolean;
}

export function ProductCard({ produto, compact = false }: ProductCardProps) {
  const menorPreco =
    produto.menor_preco && produto.menor_preco > 0 ? produto.menor_preco : null;

  if (compact) {
    return (
      <Link
        href={`/produto/${produto.id}`}
        className="card flex items-center gap-3 p-3 min-w-[200px]"
      >
        <ProductImage src={produto.imagem_url} alt={produto.nome} tipo={produto.tipo} size="sm" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-gray-800 truncate">{produto.nome}</p>
          {menorPreco && (
            <p className="text-sm font-bold text-brand-teal">{formatarPreco(menorPreco)}</p>
          )}
        </div>
      </Link>
    );
  }

  return (
    <Link href={`/produto/${produto.id}`} className="card p-4 block group">
      <div className="flex gap-3">
        <ProductImage src={produto.imagem_url} alt={produto.nome} tipo={produto.tipo} size="sm" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <h3 className="text-sm font-semibold text-gray-800 line-clamp-2 leading-snug">
              {produto.nome}
            </h3>
            {produto.artesanal && (
              <span className="flex-shrink-0 text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-medium">
                Artesanal
              </span>
            )}
          </div>
          <div className="mt-1 flex items-center gap-2">
            <TipoBadge tipo={produto.tipo} />
            {produto.volume_ml && (
              <span className="text-xs text-gray-400">{formatarVolume(produto.volume_ml)}</span>
            )}
          </div>
        </div>
      </div>

      <div className="mt-3 flex items-end justify-between">
        <div>
          {menorPreco ? (
            <>
              <p className="text-xs text-gray-400">a partir de</p>
              <p className="text-lg font-bold text-brand-teal">{formatarPreco(menorPreco)}</p>
            </>
          ) : (
            <p className="text-sm text-gray-400">Sem preço</p>
          )}
        </div>
        {produto.loja_menor_preco && (
          <span className="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded-full flex items-center gap-1.5">
            <StoreIcon src={produto.loja_icone} nome={produto.loja_menor_preco} size={16} />
            {produto.loja_menor_preco}
          </span>
        )}
      </div>

      {/* URL da loja estilo Google */}
      {produto.url_oferta && (
        <div className="mt-2 pt-2 border-t border-gray-50">
          <span className="text-xs text-brand-teal/70 truncate block">
            {produto.url_oferta.replace(/^https?:\/\//, "").split("/")[0]}
          </span>
        </div>
      )}
    </Link>
  );
}
