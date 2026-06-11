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


def load_user_app():
    install_fake_psycopg()
    install_fake_flask_cors()
    service_path = Path(__file__).resolve().parents[1] / "user-service"
    sys.path.insert(0, str(service_path))
    try:
        spec = importlib.util.spec_from_file_location(
            "user_service_app",
            service_path / "app.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.app.config.update(TESTING=True)
        return module
    finally:
        sys.path.remove(str(service_path))


class FakeConnection:
    def __init__(self, row=None, error=None):
        self.row = row
        self.error = error
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, values=None):
        self.executed.append((query, values))
        if self.error:
            raise self.error
        return self

    def fetchone(self):
        return self.row


def test_health_checks_database(monkeypatch):
    user_app = load_user_app()
    connection = FakeConnection()
    monkeypatch.setattr(user_app, "connect", lambda: connection)

    response = user_app.app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "user-service",
        "database": "ok",
    }
    assert connection.executed[0][0] == "SELECT 1"


def test_health_reports_unavailable_database(monkeypatch):
    user_app = load_user_app()
    monkeypatch.setattr(
        user_app,
        "connect",
        lambda: FakeConnection(error=FakeOperationalError("db down")),
    )

    response = user_app.app.test_client().get("/health")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "error",
        "service": "user-service",
        "database": "unavailable",
    }


def test_create_user_rejects_invalid_name():
    user_app = load_user_app()

    response = user_app.app.test_client().post("/users", json={"name": 123})

    assert response.status_code == 400
    assert response.get_json() == {"error": "name must be a string"}


def test_create_user_rejects_too_long_name():
    user_app = load_user_app()

    response = user_app.app.test_client().post("/users", json={"name": "x" * 81})

    assert response.status_code == 400
    assert response.get_json() == {"error": "name must be at most 80 characters"}


def test_create_user_handles_duplicate_name(monkeypatch):
    user_app = load_user_app()
    monkeypatch.setattr(
        user_app,
        "connect",
        lambda: FakeConnection(error=FakeUniqueViolation("duplicate")),
    )

    response = user_app.app.test_client().post("/users", json={"name": "Demo User"})

    assert response.status_code == 409
    assert response.get_json() == {"error": "name already exists"}


def test_create_user_returns_created_user(monkeypatch):
    user_app = load_user_app()
    row = {"id": 3, "name": "Ada", "created_at": "now"}
    connection = FakeConnection(row=row)
    monkeypatch.setattr(user_app, "connect", lambda: connection)

    response = user_app.app.test_client().post("/users", json={"name": " Ada "})

    assert response.status_code == 201
    assert response.get_json() == row
    assert connection.executed[0][1] == ("Ada",)
