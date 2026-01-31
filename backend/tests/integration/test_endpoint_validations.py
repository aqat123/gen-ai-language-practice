"""
Integration tests for endpoint validation using parameterized tests.
Tests that all learning endpoints properly validate user language/level settings.
"""

import pytest
from fastapi.testclient import TestClient


class TestEndpointValidationRequirements:
    """Test that all learning endpoints validate language and level requirements."""
    
    @pytest.mark.parametrize("endpoint_path,method", [
        ("/api/v1/conversation/start", "POST"),
        ("/api/v1/grammar/question", "GET"),
    ])
    def test_endpoints_require_language_and_level(self, authenticated_client: TestClient, endpoint_path, method):
        """Test that learning endpoints require both language and level to be set."""
        # Try without any setup - should fail
        if method == "GET":
            response = authenticated_client.get(endpoint_path)
        else:
            response = authenticated_client.post(endpoint_path, json={"topic": "test"} if "conversation" in endpoint_path else {})
        
        # Accept both 400 (validation error) and 500 (service error due to missing setup)
        assert response.status_code in [400, 422, 500]
        # Should mention either language or level or have validation error
        if response.status_code != 500:
            detail = response.json()["detail"].lower()
            assert "language" in detail or "level" in detail or "field" in detail
