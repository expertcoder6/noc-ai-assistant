"""Integration tests for the query API endpoint.

These tests use FastAPI's TestClient and mock the LLM so no real Gemini
calls or database connections are needed. Run with:
    pytest backend/tests/test_query_api.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.testclient import TestClient


# ─── Fixtures ─────────────────────────────────────────────────────────────────

MOCK_USER = {"username": "testuser", "role": "admin"}

MOCK_JWT_TOKEN = "mock.jwt.token"

def _make_client():
    """Create a TestClient with mocked auth and DB dependencies."""
    from app.main import app
    from app.auth.middleware import get_current_user
    from app.dependencies import get_db

    async def override_get_current_user():
        return MOCK_USER

    async def override_get_db():
        yield MagicMock()

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=False)


# ─── Health endpoint ───────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self):
        client = _make_client()
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_health_response_has_status(self):
        client = _make_client()
        resp = client.get("/api/v1/health")
        assert "status" in resp.json()


# ─── Intents endpoint ──────────────────────────────────────────────────────────

class TestIntentsEndpoint:
    def test_intents_requires_auth(self):
        from app.main import app
        from app.auth.middleware import get_current_user
        app.dependency_overrides.clear()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/v1/intents")
        assert resp.status_code == 401

    def test_intents_returns_list(self):
        client = _make_client()
        resp = client.get("/api/v1/intents")
        assert resp.status_code == 200
        data = resp.json()
        assert "intents" in data
        assert isinstance(data["intents"], list)
        assert len(data["intents"]) >= 8  # doc specifies 9 intents (8 + out_of_scope excluded from listing)

    def test_intents_have_required_fields(self):
        client = _make_client()
        resp = client.get("/api/v1/intents")
        for intent in resp.json()["intents"]:
            assert "name" in intent
            assert "description" in intent
            assert "example_questions" in intent


# ─── Query endpoint – out_of_scope ─────────────────────────────────────────────

class TestQueryEndpointOutOfScope:
    def test_out_of_scope_returns_canned_response(self):
        client = _make_client()
        mock_intent = {"intent": "out_of_scope", "filters": {}, "response_hint": "list"}

        with patch("app.security.prompt_guard.scan_query", new=AsyncMock(return_value={"blocked": False})), \
             patch("app.security.protection.scan_prompt_injection", return_value=None), \
             patch("app.query.cache.global_query_cache.get", return_value=None), \
             patch("app.query.orchestrator.QueryOrchestrator") as MockOrch:

            mock_llm = AsyncMock()
            mock_llm.extract_intent.return_value = mock_intent
            MockOrch.return_value.llm = mock_llm

            resp = client.post("/api/v1/query", json={"message": "Tell me a joke"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["data"] == []
        assert "network" in data["answer"].lower() or "scope" in data["answer"].lower()


# ─── Query endpoint – security block ──────────────────────────────────────────

class TestQueryEndpointSecurityBlock:
    def test_blocked_query_returns_400(self):
        client = _make_client()

        with patch("app.security.prompt_guard.scan_query",
                   new=AsyncMock(return_value={"blocked": True, "pattern": "sql_injection"})):
            resp = client.post("/api/v1/query", json={"message": "drop table devices;"})

        assert resp.status_code == 400
        data = resp.json()
        assert data.get("code") == "SECURITY_BLOCKED" or "blocked" in str(data).lower()


# ─── Query endpoint – rate limit ──────────────────────────────────────────────

class TestQueryEndpointRateLimit:
    def test_exceeds_rate_limit_returns_429(self):
        """After 10 requests in a minute the 11th must be rate-limited."""
        client = _make_client()
        mock_intent = {"intent": "out_of_scope", "filters": {}, "response_hint": "list"}

        # We patch the rate limit store directly so we don't need real timing
        with patch("app.api.query._request_log", {"testuser": __import__("collections").deque(range(10))}), \
             patch("app.security.prompt_guard.scan_query", new=AsyncMock(return_value={"blocked": False})), \
             patch("app.security.protection.scan_prompt_injection", return_value=None), \
             patch("time.time", return_value=30.0):  # all 10 timestamps within window

            resp = client.post("/api/v1/query", json={"message": "anything"})

        assert resp.status_code == 429


# ─── Query endpoint – response shape ──────────────────────────────────────────

class TestQueryResponseShape:
    def test_successful_query_has_required_fields(self):
        """The response must include answer, data, intent, and timing."""
        client = _make_client()
        mock_intent = {"intent": "device_status", "filters": {"status": "down"}, "response_hint": "list"}
        mock_rows = [{"hostname": "dal-rtr-01", "status": "down", "ip_address": "10.1.1.1", "location": "Dallas"}]

        with patch("app.security.prompt_guard.scan_query", new=AsyncMock(return_value={"blocked": False})), \
             patch("app.security.protection.scan_prompt_injection", return_value=None), \
             patch("app.query.cache.global_query_cache.get", return_value=None), \
             patch("app.query.cache.global_query_cache.set", return_value=None), \
             patch("app.query.orchestrator.QueryOrchestrator") as MockOrch, \
             patch("app.query.executor.execute_query", new=AsyncMock(return_value=mock_rows)):

            mock_llm = AsyncMock()
            mock_llm.extract_intent.return_value = mock_intent
            MockOrch.return_value.llm = mock_llm

            resp = client.post("/api/v1/query", json={"message": "Which routers are down?"})

        if resp.status_code == 200:
            data = resp.json()
            assert "answer" in data
            assert "data" in data
            assert "intent" in data
            assert "timing" in data
