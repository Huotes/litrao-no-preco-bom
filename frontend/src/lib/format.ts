export function formatarPreco(valor: number): string {
  return valor.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export function formatarVolume(ml: number | null): string {
  if (!ml) return "";
  return ml >= 1000 ? `${(ml / 1000).toFixed(1)}L` : `${ml}ml`;
}

export const TIPO_LABELS: Record<string, string> = {
  cerveja: "Cerveja",
  vinho: "Vinho",
  destilado: "Destilado",
  refrigerante_alcoolico: "Refrigerante Alcoólico",
  drink_pronto: "Drink Pronto",
  outros: "Outros",
};
