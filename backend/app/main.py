"""API списка задач. Версия 1: задачи хранятся в памяти процесса."""

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Todo API")

# Пока вместо базы данных — обычный список в памяти.
tasks: list[dict] = []
next_id = 1


class TaskIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)


class TaskPatch(BaseModel):
    done: bool


def find_task(task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks():
    return tasks


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskIn):
    global next_id
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, patch: TaskPatch):
    task = find_task(task_id)
    task["done"] = patch.done
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    tasks.remove(find_task(task_id))
    return Response(status_code=204)