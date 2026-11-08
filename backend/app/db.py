"""Подключение к PostgreSQL."""

import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

DEFAULT_URL = "postgresql://todo:todo@localhost:5433/todo"


def database_url() -> str:
    # Адрес БД приходит из окружения: у local, dev и prod он разный.
    return os.environ.get("DATABASE_URL", DEFAULT_URL)


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    # При выходе из with транзакция коммитится, при исключении — откатывается.
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        yield conn
