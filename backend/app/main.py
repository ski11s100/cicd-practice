"""REST API списка задач."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from app.db import get_conn
from app.migrate import migrate

# Один и тот же образ работает во всех контурах; различается только окружение.
APP_ENV = os.environ.get("APP_ENV", "local")
# Версию «вшивает» в образ пайплайн при сборке (глава 9).
APP_VERSION = os.environ.get("APP_VERSION", "local")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    migrate()
    yield


app = FastAPI(title="Todo API", lifespan=lifespan)


class TaskIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)


class TaskPatch(BaseModel):
    done: bool


@app.get("/api/health")
def health():
    with get_conn() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/info")
def info():
    return {"env": APP_ENV, "version": APP_VERSION}


@app.get("/api/tasks")
def list_tasks():
    with get_conn() as conn:
        return conn.execute("SELECT id, title, done, created_at FROM tasks ORDER BY id").fetchall()


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskIn):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done, created_at",
            (task.title,),
        ).fetchone()


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, patch: TaskPatch):
    with get_conn() as conn:
        row = conn.execute(
            "UPDATE tasks SET done = %s WHERE id = %s RETURNING id, title, done, created_at",
            (patch.done, task_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return row


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_conn() as conn:
        deleted = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,)).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return Response(status_code=204)
