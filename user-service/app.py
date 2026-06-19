import os

import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics

from database import connect
from settings import MAX_USER_NAME_LENGTH


app = Flask(__name__)
CORS(app)

# Observability: /metrics endpoint for Prometheus
metrics = PrometheusMetrics(app)
metrics.info("user_service_info", "User service information", version="1.0.0")

USERS_CREATED_TOTAL = Counter(
    "tasktracker_users_created_total",
    "Total number of users created",
)



@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return {
            "status": "error",
            "service": "user-service",
            "database": "unavailable",
        }, 503

    return {"status": "ok", "service": "user-service", "database": "ok"}


def validate_user_name(value):
    if not isinstance(value, str):
        return None, "name must be a string"

    name = value.strip()
    if not name:
        return None, "name is required"

    if len(name) > MAX_USER_NAME_LENGTH:
        return None, f"name must be at most {MAX_USER_NAME_LENGTH} characters"

    return name, None


@app.get("/users")
def list_users():
    with connect() as conn:
        users = conn.execute(
            "SELECT id, name, created_at FROM users ORDER BY id ASC"
        ).fetchall()
    return jsonify(users)


@app.post("/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    name, error = validate_user_name(payload.get("name"))

    if error:
        return {"error": error}, 400

    try:
        with connect() as conn:
            user = conn.execute(
                """
                INSERT INTO users (name)
                VALUES (%s)
                RETURNING id, name, created_at
                """,
                (name,),
            ).fetchone()
    except psycopg.errors.UniqueViolation:
        return {"error": "name already exists"}, 409

    USERS_CREATED_TOTAL.inc()
    return jsonify(user), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
