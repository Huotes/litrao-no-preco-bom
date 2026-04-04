import type { Regiao } from "@/types/produto";

/**
 * Regiões disponíveis para seleção.
 * Mantido aqui pois é dado estático de UX, não mock de produto.
 */
export const REGIOES: Regiao[] = [
  { estado: "São Paulo", sigla: "SP", cidades: ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"] },
  { estado: "Rio de Janeiro", sigla: "RJ", cidades: ["Rio de Janeiro", "Niterói", "Petrópolis", "Nova Iguaçu"] },
  { estado: "Minas Gerais", sigla: "MG", cidades: ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Ouro Preto"] },
  { estado: "Paraná", sigla: "PR", cidades: ["Curitiba", "Londrina", "Maringá", "Foz do Iguaçu"] },
  { estado: "Rio Grande do Sul", sigla: "RS", cidades: ["Porto Alegre", "Caxias do Sul", "Pelotas", "Gramado"] },
  { estado: "Bahia", sigla: "BA", cidades: ["Salvador", "Feira de Santana", "Ilhéus", "Porto Seguro"] },
];
