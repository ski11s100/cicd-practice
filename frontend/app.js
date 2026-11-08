// Фронтенд ходит в бэкенд по относительному адресу /api — nginx проксирует его в контейнер backend.
async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${response.status}: ${await response.text()}`);
  }
  return response.status === 204 ? null : response.json();
}

const ENV_LABELS = {
  local: "LOCAL — твой компьютер",
  dev: "DEV — тестовый контур",
  prod: "PROD — боевой контур",
};

const form = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const list = document.getElementById("tasks");
const errorBox = document.getElementById("error");

function showError(error) {
  errorBox.textContent = `Ошибка: ${error.message}`;
  errorBox.hidden = false;
}

async function loadInfo() {
  const { env, version } = await api("/info");
  const banner = document.getElementById("env-banner");
  banner.textContent = ENV_LABELS[env] ?? env;
  banner.className = `banner banner-${env}`;
  document.getElementById("version").textContent = version;
  document.title = `[${env.toUpperCase()}] Список задач`;
}

function renderTask(task) {
  const item = document.createElement("li");
  item.classList.toggle("done", task.done);

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = task.done;
  checkbox.addEventListener("change", () =>
    api(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ done: checkbox.checked }),
    }).then(loadTasks, showError),
  );

  const title = document.createElement("span");
  title.textContent = task.title;

  const remove = document.createElement("button");
  remove.className = "remove";
  remove.title = "Удалить";
  remove.textContent = "×";
  remove.addEventListener("click", () =>
    api(`/tasks/${task.id}`, { method: "DELETE" }).then(loadTasks, showError),
  );

  item.append(checkbox, title, remove);
  return item;
}

async function loadTasks() {
  const tasks = await api("/tasks");
  list.replaceChildren(...tasks.map(renderTask));
  document.getElementById("empty").hidden = tasks.length > 0;
  errorBox.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/tasks", {
      method: "POST",
      body: JSON.stringify({ title: titleInput.value }),
    });
    titleInput.value = "";
    await loadTasks();
  } catch (error) {
    showError(error);
  }
});

loadInfo().catch(showError);
loadTasks().catch(showError);
