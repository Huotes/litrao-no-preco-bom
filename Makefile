.PHONY: up down build logs api-logs scraper-logs db-shell redis-cli restart nuke

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

scraper-logs:
	docker compose logs -f scraper

db-shell:
	docker compose exec postgres psql -U litrao_user -d litrao

redis-cli:
	docker compose exec redis redis-cli

restart:
	docker compose restart

nuke:
	@echo "ATENÇÃO: Isso vai DESTRUIR todos os dados (volumes)!"
	@read -p "Continuar? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	docker compose up -d --build
