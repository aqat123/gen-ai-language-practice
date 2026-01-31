# Testing Guide

This directory contains all tests for the Gen AI Language Practice platform.

## Quick Start

```bash
# Install dependencies (including testing tools)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run tests by category
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures (client, db_session, authenticated_client)
├── unit/                    # Unit tests for services and business logic
│   ├── test_auth_service.py
│   ├── test_conversation_service.py
│   ├── test_grammar_service.py
│   ├── test_vocabulary_service.py
│   ├── test_progress_service.py
│   ├── test_ai_services.py
│   └── test_models.py
└── integration/             # Integration tests for API endpoints
    ├── test_auth_endpoints.py
    ├── test_vocabulary_endpoints.py
    ├── test_greeting_endpoints.py
    ├── test_progress_endpoints.py
    ├── test_endpoint_validations.py
    └── test_error_handling.py
```

## Coverage

Current test coverage: **70%**

- Total tests: **186 passing**
- Statements covered: **1244/1786**

### Coverage by Module

**Excellent (>90%):**
- ✅ Auth endpoints: 99%
- ✅ Vocabulary endpoints: 96%
- ✅ Conversation endpoints: 92%
- ✅ Grammar endpoints: 92%
- ✅ Models: 100%
- ✅ Schemas: 98-100%

**Good (70-90%):**
- ⭐ Vocabulary service: 81%
- ⭐ Grammar service: 83%
- ⭐ Progress service: 95%

## Running Specific Tests

```bash
# Run only authentication tests
pytest tests/integration/test_auth_endpoints.py -v

# Run tests matching a pattern
pytest -k "test_register" -v

# Run with verbose output
pytest -v

# Run with minimal output
pytest -q

# Stop at first failure
pytest -x

# Show local variables in tracebacks
pytest -l
```

## Test Configuration

Tests are configured in `pytest.ini`:
- Test discovery patterns
- Coverage settings
- Asyncio mode for async tests
- Test markers (unit, integration, slow, auth, ai, db, api)

## Common Fixtures

Available in `conftest.py`:

- **`client`**: FastAPI TestClient (unauthenticated)
- **`authenticated_client`**: TestClient with valid auth token
- **`db_session`**: SQLAlchemy database session
- **`app`**: FastAPI application instance

## Writing New Tests

### Unit Test Example
```python
def test_register_user(db_session):
    """Test user registration service."""
    user = register_user(db_session, "testuser", "password123")
    assert user is not None
    assert user.username == "testuser"
```

### Integration Test Example
```python
def test_login_endpoint(client):
    """Test login API endpoint."""
    # Register user first
    client.post("/api/v1/auth/register", 
                json={"username": "test", "password": "pass123"})
    
    # Test login
    response = client.post("/api/v1/auth/login",
                          json={"username": "test", "password": "pass123"})
    
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Troubleshooting

**Tests failing with database errors:**
- Check that SQLite database is being created in test mode
- Ensure migrations are up to date

**Import errors:**
- Make sure you're running from the `backend` directory
- Verify virtual environment is activated

**Async test errors:**
- Ensure `@pytest.mark.asyncio` decorator is used for async tests
- Check `pytest-asyncio` is installed

## CI/CD Integration

To run tests in CI/CD pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=app --cov-report=xml --cov-report=term

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure coverage doesn't drop below 70%
3. Run full test suite before committing
4. Add appropriate test markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
