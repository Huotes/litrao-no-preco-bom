import { TIPO_LABELS } from "@/lib/format";
import type { TipoBebida } from "@/types/produto";

interface TipoBadgeProps {
  tipo: TipoBebida;
}

const TIPO_COLORS: Record<TipoBebida, string> = {
  cerveja: "bg-brand-gold/20 text-brand-orange-dark",
  vinho: "bg-red-50 text-red-600",
  destilado: "bg-brand-teal/10 text-brand-teal-dark",
  refrigerante_alcoolico: "bg-purple-50 text-purple-600",
  drink_pronto: "bg-brand-green/10 text-brand-green-dark",
  outros: "bg-gray-100 text-gray-600",
};

export function TipoBadge({ tipo }: TipoBadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${TIPO_COLORS[tipo] ?? TIPO_COLORS.outros}`}>
      {TIPO_LABELS[tipo] ?? tipo}
    </span>
  );
}
