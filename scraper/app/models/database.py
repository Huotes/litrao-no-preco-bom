"""Base declarativa compartilhada para o scraper."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa para todos os models."""
