import os

# Тесты ходят в отдельную БД todo_test, чтобы не трогать данные локального запуска.
os.environ.setdefault("DATABASE_URL", "postgresql://todo:todo@localhost:5433/todo_test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import get_conn  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    # with запускает lifespan приложения, т.е. применяет миграции.
    with TestClient(app) as test_client:
        with get_conn() as conn:
            conn.execute("TRUNCATE tasks RESTART IDENTITY")
        yield test_client
