import os
import time

import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg.rows import dict_row


app = Flask(__name__)
CORS(app)

MAX_USER_NAME_LENGTH = 80


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
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS users_name_unique
                    ON users (name)
                    """
                )
                conn.execute(
                    """
                    INSERT INTO users (name)
                    SELECT 'Demo User'
                    WHERE NOT EXISTS (SELECT 1 FROM users)
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

    return jsonify(user), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
