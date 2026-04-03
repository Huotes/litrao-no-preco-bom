"""Configuração do Celery para o serviço de scraping."""

import os

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "litrao_scraper",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.scrape_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    task_soft_time_limit=300,
    task_time_limit=600,
    worker_max_tasks_per_child=50,
    beat_schedule={
        "scrape-all-stores": {
            "task": "app.tasks.scrape_tasks.scrape_todas_lojas",
            "schedule": crontab(minute=0, hour="*/4"),
        },
    },
)
