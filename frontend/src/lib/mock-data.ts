import type { Produto, Regiao } from "@/types/produto";

export const REGIOES: Regiao[] = [
  { estado: "São Paulo", sigla: "SP", cidades: ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"] },
  { estado: "Rio de Janeiro", sigla: "RJ", cidades: ["Rio de Janeiro", "Niterói", "Petrópolis", "Nova Iguaçu"] },
  { estado: "Minas Gerais", sigla: "MG", cidades: ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Ouro Preto"] },
  { estado: "Paraná", sigla: "PR", cidades: ["Curitiba", "Londrina", "Maringá", "Foz do Iguaçu"] },
  { estado: "Rio Grande do Sul", sigla: "RS", cidades: ["Porto Alegre", "Caxias do Sul", "Pelotas", "Gramado"] },
  { estado: "Bahia", sigla: "BA", cidades: ["Salvador", "Feira de Santana", "Ilhéus", "Porto Seguro"] },
];

export const MOCK_PRODUTOS: Produto[] = [
  { id: 1, nome: "Skol Pilsen Lata 350ml", tipo: "cerveja", subtipo: "Pilsen", marca: "Skol", volume_ml: 350, teor_alcoolico: 4.7, imagem_url: null, menor_preco: 3.49, loja_menor_preco: "Pão de Açúcar" },
  { id: 2, nome: "Brahma Duplo Malte 600ml", tipo: "cerveja", subtipo: "Lager", marca: "Brahma", volume_ml: 600, teor_alcoolico: 4.7, imagem_url: null, menor_preco: 6.99, loja_menor_preco: "Extra" },
  { id: 3, nome: "Heineken Long Neck 330ml", tipo: "cerveja", subtipo: "Lager", marca: "Heineken", volume_ml: 330, teor_alcoolico: 5.0, imagem_url: null, menor_preco: 5.29, loja_menor_preco: "Carrefour" },
  { id: 4, nome: "Corona Extra 355ml", tipo: "cerveja", subtipo: "Lager", marca: "Corona", volume_ml: 355, teor_alcoolico: 4.5, imagem_url: null, menor_preco: 7.49, loja_menor_preco: "Pão de Açúcar" },
  { id: 5, nome: "Budweiser Lata 473ml", tipo: "cerveja", subtipo: "Lager", marca: "Budweiser", volume_ml: 473, teor_alcoolico: 5.0, imagem_url: null, menor_preco: 4.29, loja_menor_preco: "Assaí" },
  { id: 6, nome: "Antarctica Original 600ml", tipo: "cerveja", subtipo: "Pilsen", marca: "Antarctica", volume_ml: 600, teor_alcoolico: 5.0, imagem_url: null, menor_preco: 5.49, loja_menor_preco: "Atacadão" },
  { id: 7, nome: "Stella Artois 275ml", tipo: "cerveja", subtipo: "Lager", marca: "Stella Artois", volume_ml: 275, teor_alcoolico: 5.0, imagem_url: null, menor_preco: 4.99, loja_menor_preco: "Carrefour" },
  { id: 8, nome: "IPA Lagunitas 355ml", tipo: "cerveja", subtipo: "IPA", marca: "Lagunitas", volume_ml: 355, teor_alcoolico: 6.2, imagem_url: null, menor_preco: 12.90, loja_menor_preco: "Empório da Cerveja" },
  { id: 9, nome: "Vinho Casillero del Diablo Cabernet 750ml", tipo: "vinho", subtipo: "Tinto", marca: "Casillero del Diablo", volume_ml: 750, teor_alcoolico: 13.5, imagem_url: null, menor_preco: 39.90, loja_menor_preco: "Wine.com" },
  { id: 10, nome: "Vinho Santa Helena Reservado Merlot 750ml", tipo: "vinho", subtipo: "Tinto", marca: "Santa Helena", volume_ml: 750, teor_alcoolico: 13.0, imagem_url: null, menor_preco: 29.90, loja_menor_preco: "Carrefour" },
  { id: 11, nome: "Vinho Miolo Seleção Chardonnay 750ml", tipo: "vinho", subtipo: "Branco", marca: "Miolo", volume_ml: 750, teor_alcoolico: 12.5, imagem_url: null, menor_preco: 34.50, loja_menor_preco: "Evino" },
  { id: 12, nome: "Espumante Chandon Brut 750ml", tipo: "vinho", subtipo: "Espumante", marca: "Chandon", volume_ml: 750, teor_alcoolico: 12.0, imagem_url: null, menor_preco: 69.90, loja_menor_preco: "Wine.com" },
  { id: 13, nome: "Absolut Vodka Original 750ml", tipo: "destilado", subtipo: "Vodka", marca: "Absolut", volume_ml: 750, teor_alcoolico: 40.0, imagem_url: null, menor_preco: 69.90, loja_menor_preco: "Extra" },
  { id: 14, nome: "Smirnoff Ice Long Neck 275ml", tipo: "drink_pronto", subtipo: "Ice", marca: "Smirnoff", volume_ml: 275, teor_alcoolico: 5.0, imagem_url: null, menor_preco: 5.99, loja_menor_preco: "Pão de Açúcar" },
  { id: 15, nome: "Jack Daniel's Tennessee 1L", tipo: "destilado", subtipo: "Whisky", marca: "Jack Daniel's", volume_ml: 1000, teor_alcoolico: 40.0, imagem_url: null, menor_preco: 159.90, loja_menor_preco: "Atacadão" },
  { id: 16, nome: "Gin Tanqueray London Dry 750ml", tipo: "destilado", subtipo: "Gin", marca: "Tanqueray", volume_ml: 750, teor_alcoolico: 43.1, imagem_url: null, menor_preco: 99.90, loja_menor_preco: "Carrefour" },
  { id: 17, nome: "Cachaça 51 965ml", tipo: "destilado", subtipo: "Cachaça", marca: "51", volume_ml: 965, teor_alcoolico: 40.0, imagem_url: null, menor_preco: 12.90, loja_menor_preco: "Assaí" },
  { id: 18, nome: "Tequila José Cuervo Ouro 750ml", tipo: "destilado", subtipo: "Tequila", marca: "José Cuervo", volume_ml: 750, teor_alcoolico: 38.0, imagem_url: null, menor_preco: 89.90, loja_menor_preco: "Extra" },
  { id: 19, nome: "Campari Bitter 998ml", tipo: "destilado", subtipo: "Bitter", marca: "Campari", volume_ml: 998, teor_alcoolico: 25.0, imagem_url: null, menor_preco: 49.90, loja_menor_preco: "Pão de Açúcar" },
  { id: 20, nome: "Beats GT 313ml Lata", tipo: "drink_pronto", subtipo: "Misto", marca: "Beats", volume_ml: 313, teor_alcoolico: 7.9, imagem_url: null, menor_preco: 4.49, loja_menor_preco: "Assaí" },
];

export const PROMOCOES = MOCK_PRODUTOS.filter((_, i) => [0, 2, 4, 9, 13, 16, 19].includes(i));
export const MAIS_PEDIDOS = MOCK_PRODUTOS.filter((_, i) => [0, 1, 2, 3, 5, 6, 12, 15].includes(i));
