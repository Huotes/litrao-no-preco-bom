#!/bin/sh
set -e

echo "Aplicando migrations..."
alembic upgrade head

echo "Populando dados de exemplo..."
python -m app.seed

echo "Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
