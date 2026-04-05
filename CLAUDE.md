# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python pytest framework for testing the [Simple Grocery Store API](https://simple-grocery-store-api.click), a REST API for managing products, carts, and orders.

## Common Commands

**Setup:**
```bash
cd pytest-framework
pip install -r requirements.txt
```

**Run Tests:**
```bash
pytest -v                              # Run all tests with verbose output
pytest tests/test_cart.py -v          # Run specific test file
pytest tests/test_cart.py::TestCartWorkflow::test_full_cart_workflow -v  # Run single test
```

**Generate Reports:**
HTML reports are auto-generated in `reports/test_report_YYYYMMDD_HHMMSS.html` after each run.
Logs are auto-generated in `logs/test_execution_YYYYMMDD_HHMMSS.log`.

## Architecture

### Framework Structure

```
pytest-framework/
├── config.py           # Configuration: BASE_URL, HEADERS, test product IDs
├── conftest.py         # Pytest fixtures: logging setup, HTML report hooks
├── utils/
│   └── api_client.py   # APIClient class - wraps all HTTP requests
└── tests/
    ├── test_products.py
    ├── test_cart.py    # Uses pytest fixtures with yield for setup/teardown
    └── test_orders.py  # Requires authentication via register_client()
```

### Key Patterns

**APIClient (utils/api_client.py):**
- Centralized HTTP client that automatically logs all requests/responses
- Auth token management via `set_auth_token()` - sets Bearer header
- Helper methods like `create_cart()`, `add_item_to_cart()`, `register_client()`
- Returns `requests.Response` objects for assertions

**Authentication Flow:**
```python
client = APIClient()
client.register_client("Name", "email@example.com")  # Sets token internally
# Now client has auth header set for order operations
```

**Test Fixtures (conftest.py):**
- Session-scoped `setup_logging` - logs to both console and timestamped files
- Function-scoped `log_test_name` - logs test start/end
- `autouse=True` fixtures run automatically without being requested

**Test Data:**
Edit `config.py` to change test product IDs:
- `TEST_PRODUCT_ID = 4643` (Starbucks Coffee)
- `SECOND_PRODUCT_ID = 1709` (Beef Ribeye)

## API Workflow

The API follows this sequence for a complete order:
1. `POST /api-clients` - Register to get access token
2. `POST /carts` - Create cart, get cartId
3. `POST /carts/{cartId}/items` - Add products
4. `POST /orders` - Create order (requires auth token)

## Important Notes

- **409 Conflict**: Email already registered - use `uuid.uuid4()` for unique emails in tests
- **401 Unauthorized**: Call `register_client()` before order operations
- The APIClient stores the token internally after registration
- HTML reports and logs are auto-generated via conftest.py hooks
