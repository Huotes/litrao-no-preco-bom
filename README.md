# 🍺 Litrão no Preço Bom

Buscador de preços de bebidas alcoólicas — encontre promoções comparando preços de diversas lojas online.

## Arquitetura

| Serviço | Tecnologia | Porta | Função |
|---------|-----------|-------|--------|
| **nginx** | Nginx Alpine | 80 | Reverse proxy |
| **frontend** | Next.js 15 + TypeScript | 3000 | Interface do usuário |
| **api** | FastAPI + Pydantic | 8000 | REST API |
| **scraper** | Celery + httpx | — | Coleta de preços |
| **celery-beat** | Celery Beat | — | Agendamento (4/4h) |
| **postgres** | PostgreSQL 16 | 5432 | Banco de dados |
| **redis** | Redis 7 | 6379 | Cache + broker Celery |

## Quick Start

```bash
# Subir tudo
make build
make up

# Acessar
open http://localhost

# Logs
make logs
```

## Estrutura

```
├── api/                    # Serviço REST (FastAPI)
│   └── app/
│       ├── core/           # Config, database, cache
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic schemas
│       ├── routes/         # Endpoints
│       └── services/       # Lógica de negócio
├── scraper/                # Serviço de scraping (Celery)
│   └── app/
│       ├── spiders/        # Spiders por loja
│       └── tasks/          # Tasks Celery
├── frontend/               # Interface (Next.js)
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # React components
│       ├── hooks/          # Custom hooks
│       ├── lib/            # API client, utils
│       └── types/          # TypeScript types
├── nginx/                  # Config do reverse proxy
├── docker-compose.yml
└── Makefile
```

## Adicionando uma nova loja

1. Copie `scraper/app/spiders/exemplo.py` para um novo arquivo
2. Ajuste `nome_loja`, `url_base` e os seletores CSS
3. Registre a classe no `SPIDERS_REGISTRY` em `scraper/app/tasks/scrape_tasks.py`
4. Rebuild: `make build && make restart`

## Comandos úteis

```bash
make db-shell       # psql no banco
make redis-cli      # redis-cli
make nuke           # destrói volumes e rebuilda tudo
```
