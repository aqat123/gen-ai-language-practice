"""
Integration tests for greeting and health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestGreetingEndpoints:
    """Test greeting and health check endpoints."""
    
    def test_health_check_returns_ok(self, client: TestClient):
        """Test that health check endpoint returns ok status."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_greeting_returns_message(self, client: TestClient):
        """Test that greeting endpoint returns welcome message."""
        response = client.get("/api/v1/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Language Learning Backend" in data["message"]
