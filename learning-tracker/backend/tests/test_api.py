import os
import tempfile

# Use a throw-away database file for the tests (set BEFORE importing the app)
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import database  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    database.Base.metadata.drop_all(bind=database.engine)  # empty database for every test
    with TestClient(app) as c:  # starting the app creates the tables again
        yield c


def add(client, topic="Docker", hours=2, notes=""):
    return client.post("/api/entries", json={"topic": topic, "hours": hours, "notes": notes})


def test_health_is_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["database"] == "up"


def test_create_and_list(client):
    assert add(client, "Terraform", 1.5, "state files").status_code == 201
    items = client.get("/api/entries").json()
    assert len(items) == 1 and items[0]["topic"] == "Terraform"


def test_newest_first(client):
    add(client, "first")
    add(client, "second")
    assert [e["topic"] for e in client.get("/api/entries").json()] == ["second", "first"]


def test_blank_topic_rejected(client):
    assert client.post("/api/entries", json={"topic": "", "hours": 1}).status_code == 422


def test_hours_must_be_positive(client):
    assert client.post("/api/entries", json={"topic": "x", "hours": 0}).status_code == 422
    assert client.post("/api/entries", json={"topic": "x", "hours": 25}).status_code == 422


def test_delete(client):
    entry_id = add(client).json()["id"]
    assert client.delete(f"/api/entries/{entry_id}").status_code == 204
    assert client.get("/api/entries").json() == []


def test_delete_missing_is_404(client):
    assert client.delete("/api/entries/999").status_code == 404


def test_stats(client):
    add(client, "Docker", 2)
    add(client, "Docker", 1)
    add(client, "Git", 1)
    s = client.get("/api/stats").json()
    assert s == {"entries": 3, "total_hours": 4.0, "top_topic": "Docker"}


def test_stats_when_empty(client):
    assert client.get("/api/stats").json() == {"entries": 0, "total_hours": 0.0, "top_topic": None}
