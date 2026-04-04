"use client";

import { useState } from "react";

interface StoreIconProps {
  src: string | null;
  nome: string;
  size?: number;
}

/**
 * Renderiza logo da loja (favicon/logo URL) com fallback para inicial.
 */
export function StoreIcon({ src, nome, size = 20 }: StoreIconProps) {
  const [hasError, setHasError] = useState(false);

  if (!src || hasError) {
    return (
      <span
        className="inline-flex items-center justify-center rounded-full bg-brand-teal/10 text-brand-teal font-bold text-[10px] flex-shrink-0"
        style={{ width: size, height: size }}
      >
        {nome.charAt(0).toUpperCase()}
      </span>
    );
  }

  return (
    <img
      src={src}
      alt={nome}
      width={size}
      height={size}
      className="rounded-sm flex-shrink-0 object-contain"
      onError={() => setHasError(true)}
      loading="lazy"
    />
  );
}
