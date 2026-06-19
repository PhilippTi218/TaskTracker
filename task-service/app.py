import os
import time

import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics
from psycopg.rows import dict_row


app = Flask(__name__)
CORS(app)

# Observability: /metrics endpoint for Prometheus
metrics = PrometheusMetrics(app)
metrics.info("task_service_info", "Task service information", version="1.0.0")

TASKS_CREATED_TOTAL = Counter(
    "tasktracker_tasks_created_total",
    "Total number of tasks created",
)
TASKS_UPDATED_TOTAL = Counter(
    "tasktracker_tasks_updated_total",
    "Total number of tasks updated",
)
TASKS_DELETED_TOTAL = Counter(
    "tasktracker_tasks_deleted_total",
    "Total number of tasks deleted",
)



def db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "tasktracker"),
        "user": os.getenv("DB_USER", "tasktracker"),
        "password": os.getenv("DB_PASSWORD", "tasktracker"),
    }


def connect():
    return psycopg.connect(**db_config(), row_factory=dict_row)


def init_db():
    for attempt in range(1, 11):
        try:
            with connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        user_id INTEGER,
                        done BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            return
        except psycopg.OperationalError:
            if attempt == 10:
                raise
            time.sleep(2)


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return {
            "status": "error",
            "service": "task-service",
            "database": "unavailable",
        }, 503

    return {"status": "ok", "service": "task-service", "database": "ok"}


@app.get("/tasks")
def list_tasks():
    filters = []
    values = []

    if "done" in request.args:
        raw = request.args["done"].strip().lower()
        if raw in ("true", "1"):
            filters.append("done = %s")
            values.append(True)
        elif raw in ("false", "0"):
            filters.append("done = %s")
            values.append(False)
        else:
            return {"error": "done must be true or false"}, 400

    if "user_id" in request.args:
        try:
            user_id = int(request.args["user_id"])
        except ValueError:
            return {"error": "user_id must be a number"}, 400
        filters.append("user_id = %s")
        values.append(user_id)

    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    with connect() as conn:
        tasks = conn.execute(
            f"""
            SELECT id, title, description, user_id, done, created_at
            FROM tasks
            {where}
            ORDER BY id DESC
            """,
            values,
        ).fetchall()
    return jsonify(tasks)


def validate_task_fields(payload, require_title):
    if require_title or "title" in payload:
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            return "title must be a non-empty string"

    if "done" in payload and not isinstance(payload["done"], bool):
        return "done must be true or false"

    if "user_id" in payload:
        user_id = payload["user_id"]
        if user_id is not None and (
            isinstance(user_id, bool) or not isinstance(user_id, int)
        ):
            return "user_id must be a number or null"

    return None


@app.post("/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}

    error = validate_task_fields(payload, require_title=True)
    if error:
        return {"error": error}, 400

    title = payload["title"].strip()
    description = (payload.get("description") or "").strip()
    user_id = payload.get("user_id")

    with connect() as conn:
        task = conn.execute(
            """
            INSERT INTO tasks (title, description, user_id)
            VALUES (%s, %s, %s)
            RETURNING id, title, description, user_id, done, created_at
            """,
            (title, description, user_id),
        ).fetchone()

    TASKS_CREATED_TOTAL.inc()
    return jsonify(task), 201


@app.patch("/tasks/<int:task_id>")
def update_task(task_id):
    payload = request.get_json(silent=True) or {}

    error = validate_task_fields(payload, require_title=False)
    if error:
        return {"error": error}, 400

    allowed_fields = {
        "title": payload.get("title"),
        "description": payload.get("description"),
        "user_id": payload.get("user_id"),
        "done": payload.get("done"),
    }
    updates = {key: value for key, value in allowed_fields.items() if key in payload}

    if not updates:
        return {"error": "no supported fields provided"}, 400

    if "title" in updates:
        updates["title"] = updates["title"].strip()

    assignments = ", ".join(f"{field} = %s" for field in updates)
    values = list(updates.values()) + [task_id]

    with connect() as conn:
        task = conn.execute(
            f"""
            UPDATE tasks
            SET {assignments}
            WHERE id = %s
            RETURNING id, title, description, user_id, done, created_at
            """,
            values,
        ).fetchone()

    if task is None:
        return {"error": "task not found"}, 404

    TASKS_UPDATED_TOTAL.inc()
    return jsonify(task)


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    with connect() as conn:
        result = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

    if result.rowcount == 0:
        return {"error": "task not found"}, 404

    TASKS_DELETED_TOTAL.inc()
    return "", 204


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

