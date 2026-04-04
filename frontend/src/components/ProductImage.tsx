import { TIPO_ICONS } from "@/lib/format";
import type { TipoBebida } from "@/types/produto";

interface ProductImageProps {
  src: string | null;
  alt: string;
  tipo?: TipoBebida;
  size?: "sm" | "lg";
}

const SIZE_CLASSES = {
  sm: "h-14 w-14 text-2xl",
  lg: "h-32 w-32 text-5xl",
} as const;

export function ProductImage({ src, alt, tipo, size = "sm" }: ProductImageProps) {
  const icon = tipo ? TIPO_ICONS[tipo] : "🍾";

  if (!src) {
    return (
      <div className={`${SIZE_CLASSES[size]} flex-shrink-0 rounded-xl bg-brand-teal/5 flex items-center justify-center`}>
        {icon}
      </div>
    );
  }

  return (
    <div className={`${SIZE_CLASSES[size]} flex-shrink-0 overflow-hidden rounded-xl bg-gray-50 flex items-center justify-center`}>
      <img src={src} alt={alt} className="max-h-full max-w-full object-contain" />
    </div>
  );
}
