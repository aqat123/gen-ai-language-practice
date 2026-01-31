"""
Pytest configuration and shared fixtures.

This file contains fixtures that are automatically available to all tests.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base
from app.db.models import User
from app.main import app
from app.core.security import get_password_hash
from app.api.deps import get_db

# Test database URL - use a separate database for tests
TEST_DATABASE_URL = "sqlite:///./test_language_app.db"


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a test database engine.
    
    This fixture creates a new database engine for each test function
    and cleans up after the test completes.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    
    # Remove test database file
    if os.path.exists("./test_language_app.db"):
        os.remove("./test_language_app.db")


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create a fresh database session for each test.
    
    This ensures each test has a clean database state.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client with overridden database dependency.
    
    This client can be used to make HTTP requests to the API endpoints.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Override the startup event to prevent database initialization
    # The test database is already created by db_engine fixture
    original_startup_events = app.router.on_startup.copy()
    app.router.on_startup.clear()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original startup events
    app.router.on_startup = original_startup_events
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for testing.
    
    Returns a User object with:
    - username: "testuser"
    - password: "testpass123" (hashed)
    - target_language: "German"
    - level: "A1"
    """
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        target_language="German",
        level="A1",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_advanced(db_session):
    """
    Create an advanced level sample user for testing.
    """
    user = User(
        username="advanceduser",
        hashed_password=get_password_hash("advanced123"),
        full_name="Advanced User",
        target_language="French",
        level="B2",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, sample_user):
    """
    Get an authentication token for the sample user.
    
    Returns the JWT token string.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def authenticated_client(client, auth_token):
    """
    Create a test client with authentication headers set.
    
    This client automatically includes the Authorization header
    in all requests.
    """
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {auth_token}"
    }
    return client


@pytest.fixture
def mock_llm_response():
    """
    Mock response data for LLM API calls.
    
    Returns a dictionary that mimics Gemini API response structure.
    """
    return {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "Mocked LLM response text"
                }]
            }
        }]
    }


@pytest.fixture
def mock_vocabulary_flashcard():
    """
    Mock flashcard data for vocabulary tests.
    """
    return {
        "word": "Haus",
        "translation": "house",
        "example_sentence": "Das Haus ist groß.",
        "example_translation": "The house is big.",
        "difficulty": "A1",
        "image_url": "https://example.com/house.jpg"
    }


@pytest.fixture
def mock_grammar_question():
    """
    Mock grammar question data.
    """
    return {
        "question_text": "Fill in the blank: Ich ___ ein Student.",
        "options": ["bin", "bist", "ist", "sind"],
        "correct_answer": "bin",
        "explanation": "Use 'bin' with 'ich' (I am).",
        "difficulty": "A1"
    }


# Pytest configuration hooks

def pytest_configure(config):
    """
    Configure pytest before running tests.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test items after collection.
    
    This automatically adds markers based on test file location.
    """
    for item in items:
        # Add 'unit' marker to tests in tests/unit/
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add 'integration' marker to tests in tests/integration/
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
