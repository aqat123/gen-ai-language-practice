"""
Integration tests for authentication endpoints.

These tests verify the complete request/response cycle for auth APIs.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthRegistration:
    """Test cases for user registration endpoint."""
    
    def test_register_new_user_success(self, client: TestClient):
        """Test successful user registration returns token and user data."""
        # Arrange
        user_data = {
            "username": "newuser",
            "password": "strongpassword123",
            "full_name": "New User"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["full_name"] == "New User"
        assert "hashed_password" not in data["user"]  # Should not expose password
    
    def test_register_duplicate_username_fails(self, client: TestClient):
        """Test that registering duplicate username returns 400."""
        # Arrange
        user_data = {
            "username": "duplicate",
            "password": "password123",
            "full_name": "First User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Act - Try to register again
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_with_minimal_data(self, client: TestClient):
        """Test registration with only required fields."""
        # Arrange
        user_data = {
            "username": "minimaluser",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["username"] == "minimaluser"
    
    def test_register_with_invalid_data_fails(self, client: TestClient):
        """Test that registration with missing required fields fails."""
        # Arrange
        invalid_data = {
            "username": "testuser"
            # Missing password
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestAuthLogin:
    """Test cases for user login endpoint."""
    
    def test_login_with_correct_credentials(self, client: TestClient):
        """Test successful login with correct username and password."""
        # Arrange - Register a user first
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "password": "mypassword123",
                "full_name": "Login User"
            }
        )
        
        # Act - Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "loginuser",
                "password": "mypassword123"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "loginuser"
    
    def test_login_with_wrong_password_fails(self, client: TestClient):
        """Test that login fails with incorrect password."""
        # Arrange
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "wrongpass",
                "password": "correctpassword"
            }
        )
        
        # Act
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "wrongpass",
                "password": "wrongpassword"
            }
        )
        
        # Assert
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_with_nonexistent_user_fails(self, client: TestClient):
        """Test that login fails for non-existent user."""
        # Act
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "anypassword"
            }
        )
        
        # Assert
        assert response.status_code == 401


class TestAuthMe:
    """Test cases for current user info endpoint."""
    
    def test_get_current_user_with_valid_token(self, authenticated_client: TestClient):
        """Test getting current user info with valid authentication."""
        # Act
        response = authenticated_client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "hashed_password" not in data
    
    def test_get_current_user_without_token_fails(self, client: TestClient):
        """Test that accessing /me without token returns 403 (Forbidden)."""
        # Act
        response = client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 403  # FastAPI returns 403 for missing credentials
    
    def test_get_current_user_with_invalid_token_fails(self, client: TestClient):
        """Test that invalid token returns 401."""
        # Arrange
        client.headers = {"Authorization": "Bearer invalid_token_here"}
        
        # Act
        response = client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 401


class TestUpdateLanguage:
    """Test cases for updating user language."""
    
    def test_update_target_language_success(self, authenticated_client: TestClient):
        """Test successfully updating user's target language."""
        # Act
        response = authenticated_client.put(
            "/api/v1/auth/me/language",
            json={"target_language": "French"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["target_language"] == "French"
    
    def test_update_language_without_auth_fails(self, client: TestClient):
        """Test that updating language without auth fails."""
        # Act
        response = client.put(
            "/api/v1/auth/me/language",
            json={"target_language": "Spanish"}
        )
        
        # Assert
        assert response.status_code == 403  # FastAPI returns 403 for missing credentials
    
    def test_update_language_persists_in_database(
        self,
        authenticated_client: TestClient
    ):
        """Test that language update persists across requests."""
        # Act - Update language
        authenticated_client.put(
            "/api/v1/auth/me/language",
            json={"target_language": "German"}
        )
        
        # Get user info again
        response = authenticated_client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["target_language"] == "German"


class TestUpdateLevel:
    """Test cases for updating user level."""
    
    def test_update_level_success(self, authenticated_client: TestClient):
        """Test successfully updating user's proficiency level."""
        # Act
        response = authenticated_client.put(
            "/api/v1/auth/me/level",
            json={"level": "B2"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "B2"
    
    @pytest.mark.parametrize("level", ["A1", "A2", "B1", "B2", "C1", "C2"])
    def test_update_all_valid_levels(
        self,
        authenticated_client: TestClient,
        level: str
    ):
        """Test that all CEFR levels can be set."""
        # Act
        response = authenticated_client.put(
            "/api/v1/auth/me/level",
            json={"level": level}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["level"] == level
    
    def test_update_level_without_auth_fails(self, client: TestClient):
        """Test that updating level without auth fails."""
        # Act
        response = client.put(
            "/api/v1/auth/me/level",
            json={"level": "C1"}
        )
        
        # Assert
        assert response.status_code == 403  # FastAPI returns 403 for missing credentials


class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    def test_complete_registration_and_login_flow(self, client: TestClient):
        """Test full user journey: register -> login -> access protected endpoint."""
        # Step 1: Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "flowtest",
                "password": "password123",
                "full_name": "Flow Test User"
            }
        )
        assert register_response.status_code == 201
        register_token = register_response.json()["access_token"]
        
        # Step 2: Use token from registration to access protected endpoint
        client.headers = {"Authorization": f"Bearer {register_token}"}
        me_response = client.get("/api/v1/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "flowtest"
        
        # Step 3: Login again
        client.headers = {}  # Clear headers
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "flowtest", "password": "password123"}
        )
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        
        # Step 4: Use login token
        client.headers = {"Authorization": f"Bearer {login_token}"}
        me_response2 = client.get("/api/v1/auth/me")
        assert me_response2.status_code == 200
    
    def test_token_works_across_requests(self, client: TestClient):
        """Test that a token can be used for multiple requests."""
        # Arrange - Register and get token
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "persistent", "password": "password123"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        
        # Act - Make multiple requests with same token
        response1 = client.get("/api/v1/auth/me")
        response2 = client.put(
            "/api/v1/auth/me/language",
            json={"target_language": "Italian"}
        )
        response3 = client.get("/api/v1/auth/me")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert response3.json()["target_language"] == "Italian"


class TestLegacyAuthEndpoints:
    """Test legacy auth endpoints for backward compatibility."""
    
    def test_create_legacy_user_success(self, client: TestClient):
        """Test creating a user via legacy endpoint."""
        response = client.post(
            "/api/v1/auth/users",
            json={
                "external_id": "legacy_user_123",
                "target_language": "French",
                "level": "A2"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "legacy_user_123"  # external_id is used as username
        assert data["target_language"] == "French"
        assert data["level"] == "A2"
    
    def test_create_duplicate_legacy_user_fails(self, client: TestClient):
        """Test that duplicate external_id fails."""
        user_data = {
            "external_id": "duplicate_legacy",
            "target_language": "Spanish",
            "level": "B1"
        }
        
        client.post("/api/v1/auth/users", json=user_data)
        response = client.post("/api/v1/auth/users", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_get_legacy_user_success(self, client: TestClient):
        """Test getting user via legacy endpoint."""
        client.post(
            "/api/v1/auth/users",
            json={"external_id": "get_test_user", "target_language": "German", "level": "A1"}
        )
        
        response = client.get("/api/v1/auth/users/get_test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "get_test_user"
        assert data["target_language"] == "German"
    
    def test_get_legacy_user_not_found(self, client: TestClient):
        """Test getting non-existent user returns 404."""
        response = client.get("/api/v1/auth/users/nonexistent_user")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_legacy_user_progress(self, client: TestClient, db_session):
        """Test getting user progress via legacy endpoint."""
        from app.db.models import User, UserProgress
        
        # Create user
        client.post(
            "/api/v1/auth/users",
            json={"external_id": "progress_test_user", "target_language": "Italian", "level": "B1"}
        )
        
        # Add some progress manually
        user = db_session.query(User).filter(User.external_id == "progress_test_user").first()
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            score=85,
            total_attempts=20,
            correct_attempts=17
        )
        db_session.add(progress)
        db_session.commit()
        
        response = client.get("/api/v1/auth/users/progress_test_user/progress")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["module"] == "vocabulary" for p in data)


class TestAuthErrorHandling:
    """Test error handling in auth endpoints."""
    
    def test_update_language_with_deleted_user(self, authenticated_client: TestClient):
        """Test that updating language handles missing user gracefully."""
        from unittest.mock import patch
        
        with patch('app.api.v1.endpoints.auth.update_user_language', return_value=None):
            response = authenticated_client.put(
                "/api/v1/auth/me/language",
                json={"target_language": "Portuguese"}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    def test_update_level_with_deleted_user(self, authenticated_client: TestClient):
        """Test that updating level handles missing user gracefully."""
        from unittest.mock import patch
        
        with patch('app.api.v1.endpoints.auth.update_user_level', return_value=None):
            response = authenticated_client.put(
                "/api/v1/auth/me/level",
                json={"level": "C2"}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    def test_manual_level_update_marks_placement_complete(self, authenticated_client: TestClient, db_session):
        """Test that manually setting level marks placement test as completed."""
        from app.db.models import User
        
        # Get user before update
        user_response = authenticated_client.get("/api/v1/auth/me")
        user_id = user_response.json()["id"]
        
        # Verify placement test not completed initially
        user = db_session.query(User).filter(User.id == user_id).first()
        initial_status = user.placement_test_completed
        
        # Update level
        authenticated_client.put(
            "/api/v1/auth/me/level",
            json={"level": "B1"}
        )
        
        # Verify placement test is now marked complete
        db_session.refresh(user)
        assert user.placement_test_completed == True
        assert user.level == "B1"
    
    def test_get_progress_for_user_with_no_progress(self, authenticated_client: TestClient):
        """Test getting progress for user with no progress records returns empty list."""
        # User exists but has no progress yet
        response = authenticated_client.get("/api/v1/auth/me/progress")
        
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or minimal progress
        assert isinstance(data, list)
