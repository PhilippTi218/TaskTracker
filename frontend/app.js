const taskForm = document.querySelector("#taskForm");
const userForm = document.querySelector("#userForm");
const taskList = document.querySelector("#taskList");
const userList = document.querySelector("#userList");
const userSelect = document.querySelector("#userSelect");
const refreshButton = document.querySelector("#refreshButton");
const taskFilter = document.querySelector("#taskFilter");

let currentTaskFilter = "all";
let allTasks = [];
let allUsers = [];
let isLoading = false;

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function renderUsers(users) {
  userSelect.innerHTML = "";
  userList.innerHTML = "";

  if (users.length === 0) {
    userList.innerHTML = '<p class="empty">Noch keine User vorhanden.</p>';
    userSelect.innerHTML = '<option value="">Kein User</option>';
    return;
  }

  for (const user of users) {
    const option = document.createElement("option");
    option.value = user.id;
    option.textContent = user.name;
    userSelect.appendChild(option);

    const row = document.createElement("div");
    row.className = "user-row";
    row.textContent = `${user.id}: ${user.name}`;
    userList.appendChild(row);
  }
}

function renderTasks(tasks, users) {
  const usersById = new Map(users.map(user => [Number(user.id), user.name]));
  taskList.innerHTML = "";

  if (tasks.length === 0) {
    taskList.innerHTML = '<p class="empty">Noch keine Tasks vorhanden.</p>';
    return;
  }

  for (const task of tasks) {
    const item = document.createElement("article");
    item.className = `task-card ${task.done ? "is-done" : ""}`;
    item.innerHTML = `
      <div>
        <h3>${escapeHtml(task.title)}</h3>
        <p>${escapeHtml(task.description || "Keine Beschreibung")}</p>
        <span>User: ${task.user_id ? escapeHtml(usersById.get(Number(task.user_id)) || "Unbekannt") : "nicht gesetzt"}</span>
      </div>
      <div class="task-actions">
        <button type="button" data-action="toggle" data-id="${task.id}">
          ${task.done ? "Öffnen" : "Erledigt"}
        </button>
        <button type="button" data-action="delete" data-id="${task.id}">Löschen</button>
      </div>
    `;
    taskList.appendChild(item);
  }
}

function renderFilteredTasks() {
  let filteredTasks = allTasks;

  if (currentTaskFilter === "open") {
    filteredTasks = allTasks.filter(task => !task.done);
  }

  if (currentTaskFilter === "done") {
    filteredTasks = allTasks.filter(task => task.done);
  }

  renderTasks(filteredTasks, allUsers);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setLoading(loading) {
  isLoading = loading;

  refreshButton.disabled = loading;
  taskForm.querySelector("button[type='submit']").disabled = loading;
  userForm.querySelector("button[type='submit']").disabled = loading;

  taskList.querySelectorAll("button").forEach((button) => {
    button.disabled = loading;
  });

  if (loading) {
    refreshButton.textContent = "Lade...";
  } else {
    refreshButton.textContent = "Aktualisieren";
  }
}

async function loadData() {
  setLoading(true);

  taskList.innerHTML = '<p class="empty">Lade Tasks...</p>';
  userList.innerHTML = '<p class="empty">Lade User...</p>';

  try {
    const [users, tasks] = await Promise.all([
      request("/api/users"),
      request("/api/tasks"),
    ]);

    allUsers = users;
    allTasks = tasks;

    renderUsers(allUsers);
    renderFilteredTasks();
  } catch (error) {
    taskList.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
  } finally {
    setLoading(false);
  }
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (isLoading) return;

  setLoading(true);

  try {
    const formData = new FormData(taskForm);

    await request("/api/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title"),
        description: formData.get("description"),
        user_id: formData.get("user_id") || null,
      }),
    });

    taskForm.reset();
    await loadData();
  } finally {
    setLoading(false);
  }
});

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (isLoading) return;

  setLoading(true);

  try {
    const formData = new FormData(userForm);

    await request("/api/users", {
      method: "POST",
      body: JSON.stringify({ name: formData.get("name") }),
    });

    userForm.reset();
    await loadData();
  } finally {
    setLoading(false);
  }
});

taskList.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button || isLoading) return;

  setLoading(true);

  try {
    const taskId = button.dataset.id;
    const action = button.dataset.action;

    if (action === "delete") {
      await request(`/api/tasks/${taskId}`, { method: "DELETE" });
    }

    if (action === "toggle") {
      const currentDone = button.closest(".task-card").classList.contains("is-done");

      await request(`/api/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ done: !currentDone }),
      });
    }

    await loadData();
  } finally {
    setLoading(false);
  }
});

refreshButton.addEventListener("click", () => {
  if (!isLoading) {
    loadData();
  }
});

loadData().catch((error) => {
  taskList.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
});

taskFilter.addEventListener("change", () => {
  currentTaskFilter = taskFilter.value;
  renderFilteredTasks();
});
