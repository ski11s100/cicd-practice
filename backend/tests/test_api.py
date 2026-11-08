def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_info_reports_env_and_version(client):
    body = client.get("/api/info").json()
    assert set(body) == {"env", "version"}


def test_create_and_list_tasks(client):
    created = client.post("/api/tasks", json={"title": "  Купить молоко  "})
    assert created.status_code == 201
    assert created.json()["title"] == "Купить молоко"
    assert created.json()["done"] is False

    tasks = client.get("/api/tasks").json()
    assert [t["title"] for t in tasks] == ["Купить молоко"]


def test_empty_title_is_rejected(client):
    assert client.post("/api/tasks", json={"title": "   "}).status_code == 422


def test_mark_task_done(client):
    task_id = client.post("/api/tasks", json={"title": "Сдать отчёт"}).json()["id"]

    response = client.patch(f"/api/tasks/{task_id}", json={"done": True})
    assert response.status_code == 200
    assert response.json()["done"] is True


def test_delete_task(client):
    task_id = client.post("/api/tasks", json={"title": "Удалить меня"}).json()["id"]

    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get("/api/tasks").json() == []


def test_missing_task_returns_404(client):
    assert client.patch("/api/tasks/999", json={"done": True}).status_code == 404
    assert client.delete("/api/tasks/999").status_code == 404
