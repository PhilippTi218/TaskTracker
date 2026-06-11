import importlib.util
import sys
import types
from pathlib import Path


class FakePsycopgError(Exception):
    pass


class FakeOperationalError(FakePsycopgError):
    pass


class FakeUniqueViolation(FakePsycopgError):
    pass


def install_fake_psycopg():
    psycopg = types.ModuleType("psycopg")
    psycopg.Error = FakePsycopgError
    psycopg.OperationalError = FakeOperationalError
    psycopg.connect = lambda **kwargs: None
    psycopg.errors = types.SimpleNamespace(UniqueViolation=FakeUniqueViolation)

    rows = types.ModuleType("psycopg.rows")
    rows.dict_row = object()

    sys.modules["psycopg"] = psycopg
    sys.modules["psycopg.rows"] = rows
    return psycopg


def install_fake_flask_cors():
    flask_cors = types.ModuleType("flask_cors")
    flask_cors.CORS = lambda app: app
    sys.modules["flask_cors"] = flask_cors


def load_task_app():
    install_fake_psycopg()
    install_fake_flask_cors()
    module_path = Path(__file__).resolve().parents[1] / "task-service" / "app.py"
    spec = importlib.util.spec_from_file_location("task_service_app", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True)
    return module


class FakeConnection:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, values=None):
        self.executed.append((query, values))
        return self

    def fetchall(self):
        return self.rows


def test_list_tasks_passes_done_and_user_filters_to_database(monkeypatch):
    task_app = load_task_app()
    connection = FakeConnection(rows=[])
    monkeypatch.setattr(task_app, "connect", lambda: connection)

    response = task_app.app.test_client().get("/tasks?done=true&user_id=7")

    assert response.status_code == 200
    assert response.get_json() == []
    query, values = connection.executed[0]
    assert "WHERE done = %s AND user_id = %s" in query
    assert values == [True, 7]


def test_list_tasks_rejects_invalid_done_filter():
    task_app = load_task_app()

    response = task_app.app.test_client().get("/tasks?done=maybe")

    assert response.status_code == 400
    assert response.get_json() == {"error": "done must be true or false"}


def test_list_tasks_rejects_invalid_user_filter():
    task_app = load_task_app()

    response = task_app.app.test_client().get("/tasks?user_id=abc")

    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id must be a number"}


def test_create_task_rejects_string_user_id():
    task_app = load_task_app()

    response = task_app.app.test_client().post(
        "/tasks",
        json={"title": "Test", "user_id": "1"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id must be a number or null"}
