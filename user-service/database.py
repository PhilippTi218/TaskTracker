import os

import psycopg
from psycopg.rows import dict_row


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
