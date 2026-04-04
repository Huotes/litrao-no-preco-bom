import type { TipoBebida } from "@/types/produto";

export function formatarPreco(valor: number): string {
  return valor.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export function formatarVolume(ml: number | null): string {
  if (ml == null) return "";
  return ml >= 1000 ? `${(ml / 1000).toFixed(1)}L` : `${ml}ml`;
}

export const TIPO_LABELS: Record<TipoBebida, string> = {
  cerveja: "Cerveja",
  vinho: "Vinho",
  destilado: "Destilado",
  refrigerante_alcoolico: "Refrigerante Alcoólico",
  drink_pronto: "Drink Pronto",
  outros: "Outros",
};

export const TIPO_ICONS: Record<TipoBebida, string> = {
  cerveja: "🍺",
  vinho: "🍷",
  destilado: "🥃",
  refrigerante_alcoolico: "🍹",
  drink_pronto: "🧉",
  outros: "🍾",
};
