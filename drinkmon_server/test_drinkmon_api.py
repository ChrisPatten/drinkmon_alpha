"""
Unit tests for drinkmon_api.py FastAPI backend.
Covers session open, close, and GET logic.
"""

import pytest
from fastapi.testclient import TestClient
from drinkmon_server.drinkmon_api import app

client = TestClient(app)

def test_start_and_get_sessions():
    # Start a session
    color = {"r": 10, "g": 20, "b": 30}
    resp = client.post("/api/start_session", json={"color": color})
    assert resp.status_code == 200
    guid = resp.json()["guid"]
    # Should appear in GET
    resp2 = client.get("/api/friend_sessions")
    assert resp2.status_code == 200
    sessions = resp2.json()
    assert any(s["color"] == color for s in sessions)
    # Close session
    resp3 = client.post("/api/close_session", json={"guid": guid})
    assert resp3.status_code == 200
    # Should not appear in GET
    resp4 = client.get("/api/friend_sessions")
    assert all(s["color"] != color for s in resp4.json())

def test_close_invalid_guid():
    resp = client.post("/api/close_session", json={"guid": "not-a-guid"})
    assert resp.status_code == 404

def test_double_close():
    color = {"r": 1, "g": 2, "b": 3}
    resp = client.post("/api/start_session", json={"color": color})
    guid = resp.json()["guid"]
    client.post("/api/close_session", json={"guid": guid})
    resp2 = client.post("/api/close_session", json={"guid": guid})
    assert resp2.status_code == 400
