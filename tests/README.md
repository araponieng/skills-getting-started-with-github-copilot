# FastAPI Tests

This directory contains comprehensive tests for the Mergington High School Activities API.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_api.py` - API endpoint tests
- `test_integration.py` - Integration and end-to-end tests

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py test

# Run tests with coverage
python run_tests.py coverage

# Run specific test
python run_tests.py specific test_signup_success
```

### Manual pytest Commands
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::TestSignupForActivity::test_signup_success -v
```

## Test Categories

### API Tests (`test_api.py`)
- **GET /activities** - Tests for retrieving activities
- **POST /activities/{name}/signup** - Tests for student signup
- **DELETE /activities/{name}/unregister** - Tests for student unregistration
- **Root endpoint** - Tests for redirect functionality
- **Edge cases** - Special characters, case sensitivity, etc.
- **Complete workflows** - Multi-step operations

### Integration Tests (`test_integration.py`)
- **Data integrity** - State management across operations
- **Concurrent operations** - Simulation of multiple simultaneous requests
- **Performance** - Response time and bulk operation tests
- **Error handling** - Malformed requests, boundary conditions
- **Security** - Basic protection against common attacks

## Test Coverage

The test suite provides **100% code coverage** of the FastAPI application:

```
Name         Stmts   Miss  Cover   Missing
------------------------------------------
src/app.py      33      0   100%
------------------------------------------
TOTAL           33      0   100%
```

## Fixtures

- `client` - FastAPI test client
- `reset_activities` - Resets activity data before each test
- `sample_activity` - Provides sample activity data
- `test_email` - Provides test email address

## Key Test Scenarios

1. **Happy Path Testing**
   - Successful signup and unregistration
   - Multiple students per activity
   - Same student in multiple activities

2. **Error Handling**
   - Non-existent activities
   - Duplicate registrations
   - Students not registered for activities

3. **Edge Cases**
   - Special characters in emails
   - URL encoding/decoding
   - Empty parameters
   - Unicode handling

4. **Data Integrity**
   - State persistence across requests
   - Concurrent operation simulation
   - Boundary condition testing

## Dependencies

- `pytest` - Testing framework
- `httpx` - HTTP client for testing FastAPI
- `pytest-cov` - Coverage reporting

## Adding New Tests

When adding new tests:

1. Use descriptive test names that explain what is being tested
2. Include docstrings explaining the test purpose
3. Use appropriate fixtures for setup and teardown
4. Test both success and failure scenarios
5. Maintain test isolation using the `reset_activities` fixture