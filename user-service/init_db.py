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
                        name VARCHAR({MAX_USER_NAME_LENGTH}) UNIQUE NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            return
        except psycopg.OperationalError:
            if attempt == 10:
                raise
            time.sleep(2)


if __name__ == "__main__":
    init_db()
