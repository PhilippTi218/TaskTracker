import time

import psycopg

from database import connect
from settings import MAX_USER_NAME_LENGTH


def init_db():
    for attempt in range(1, 11):
        try:
            with connect() as conn:
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                            CHECK (char_length(name) <= {MAX_USER_NAME_LENGTH}),
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


if __name__ == "__main__":
    init_db()
