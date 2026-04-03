import { TIPO_LABELS } from "@/lib/format";
import type { TipoBebida } from "@/types/produto";

interface TipoBadgeProps {
  tipo: TipoBebida;
}

export function TipoBadge({ tipo }: TipoBadgeProps) {
  return (
    <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
      {TIPO_LABELS[tipo] ?? tipo}
    </span>
  );
}
