# Simple Grocery Store API - Test Framework

A beginner-friendly Python pytest framework for testing the [Simple Grocery Store API](https://simple-grocery-store-api.click).

## Features

- Clean, organized folder structure with beginner-friendly comments
- Easy-to-use API client class with helper methods
- Automatic request/response logging
- HTML test reports with timestamps
- Full response printing in console
- Step-by-step API workflow documentation

---

## Project Structure

```
pytest-framework/
├── config.py              # Base URL, headers, logging config
├── conftest.py            # Pytest fixtures and hooks
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   ├── __init__.py
│   └── api_client.py     # API client class
├── tests/
│   ├── __init__.py
│   ├── test_products.py  # Product & Cart CRUD tests
│   ├── test_cart.py      # Cart workflow tests
│   └── test_orders.py    # Order & Authentication tests
├── logs/                 # Auto-generated log files
└── reports/              # Auto-generated HTML reports
```

---

## API Endpoint Sequence

### Complete Order Workflow (Step-by-Step)

This shows the correct order to call APIs for placing a grocery order:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE ORDER WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 1: Check API Status (Optional)                               │
│  ┌──────────────────────────────────────────┐                      │
│  │ GET /status                               │                      │
│  │ Purpose: Verify API is running            │                      │
│  │ Response: {"status": "UP"}                │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 2: Get Products (Optional - for browsing)                    │
│  ┌──────────────────────────────────────────┐                      │
│  │ GET /products                             │                      │
│  │ Purpose: Browse available products        │                      │
│  │ Response: [{id, name, category, inStock}] │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 3: Register API Client (Required for orders)                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ POST /api-clients                         │                      │
│  │ Body: {"clientName": "name",              │                      │
│  │        "clientEmail": "email"}            │                      │
│  │ Response: {"accessToken": "token123"}     │                      │
│  │ NOTE: Save token for Step 6 & 7           │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 4: Create a New Cart                                         │
│  ┌──────────────────────────────────────────┐                      │
│  │ POST /carts                               │                      │
│  │ Body: (empty)                             │                      │
│  │ Response: {"created": true,               │                      │
│  │           "cartId": "xyz123"}             │                      │
│  │ NOTE: Save cartId for Steps 5-8           │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 5: Add Items to Cart (Repeat as needed)                      │
│  ┌──────────────────────────────────────────┐                      │
│  │ POST /carts/{cartId}/items                │                      │
│  │ Body: {"productId": 4643,                 │                      │
│  │        "quantity": 2}                     │                      │
│  │ Response: {"itemId": "abc456"}            │                      │
│  │ NOTE: You can add multiple items          │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 6: (Optional) View Cart Details                              │
│  ┌──────────────────────────────────────────┐                      │
│  │ GET /carts/{cartId}                       │                      │
│  │ Purpose: Verify cart contents             │                      │
│  │ Response: {created, items: [...]}         │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 7: Create Order from Cart                                    │
│  ┌──────────────────────────────────────────┐                      │
│  │ POST /orders                              │                      │
│  │ Headers: Authorization: Bearer {token}    │                      │
│  │ Body: {"cartId": "xyz123",                │                      │
│  │        "customerName": "John Doe",        │                      │
│  │        "comment": "Optional note"}        │                      │
│  │ Response: {"orderId": "order123"}         │                      │
│  │ NOTE: Cart is emptied after order         │                      │
│  └──────────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│  STEP 8: View Orders (Optional)                                    │
│  ┌──────────────────────────────────────────┐                      │
│  │ GET /orders                               │                      │
│  │ Headers: Authorization: Bearer {token}    │                      │
│  │ Response: [{orderId, customerName, ...}]  │                      │
│  └──────────────────────────────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Reference

### 1. Status Endpoints (No Authentication)

| Method | Endpoint | Purpose | When to Use |
|--------|----------|---------|-------------|
| `GET` | `/status` | Check if API is running | First call to verify API health |

**Example:**
```
GET https://simple-grocery-store-api.click/status
Response: {"status": "UP"}
```

---

### 2. Products Endpoints (No Authentication)

| Method | Endpoint | Purpose | When to Use |
|--------|----------|---------|-------------|
| `GET` | `/products` | Get all products | Browse available products |
| `GET` | `/products?category=coffee` | Filter by category | Find specific product types |
| `GET` | `/products?results=5` | Limit results | Get limited number of products |
| `GET` | `/products/{productId}` | Get single product | View product details |

**Example Sequence:**
```
1. GET /products                    → Browse all products
2. GET /products?category=coffee    → Filter for coffee
3. GET /products/4643               → Get details of product 4643
```

---

### 3. Cart Endpoints (No Authentication)

| Method | Endpoint | Purpose | When to Use |
|--------|----------|---------|-------------|
| `POST` | `/carts` | Create new cart | Start a new shopping session |
| `GET` | `/carts/{cartId}` | Get cart details | View cart info |
| `GET` | `/carts/{cartId}/items` | Get cart items | See what's in cart |
| `POST` | `/carts/{cartId}/items` | Add item to cart | Add product to cart |
| `PATCH` | `/carts/{cartId}/items/{itemId}` | Modify item quantity | Change how many |
| `PUT` | `/carts/{cartId}/items/{itemId}` | Replace item | Swap product |
| `DELETE` | `/carts/{cartId}/items/{itemId}` | Remove item | Delete from cart |

**Example Sequence:**
```
1. POST /carts                              → Create cart, get cartId
2. POST /carts/{cartId}/items               → Add product 4643, qty 2
3. POST /carts/{cartId}/items               → Add product 1709, qty 1
4. GET /carts/{cartId}/items                → View all items
5. PATCH /carts/{cartId}/items/{itemId}     → Change qty to 5
6. DELETE /carts/{cartId}/items/{itemId}    → Remove item
7. GET /carts/{cartId}/items                → Verify final cart
```

---

### 4. Authentication Endpoints

| Method | Endpoint | Purpose | When to Use |
|--------|----------|---------|-------------|
| `POST` | `/api-clients` | Register & get token | Before making order requests |

**Example:**
```
POST /api-clients
Body: {
    "clientName": "My Test Client",
    "clientEmail": "test@example.com"
}
Response: {"accessToken": "eyJhbGciOiJIUzI1NiIs..."}
```

---

### 5. Orders Endpoints (Requires Authentication)

| Method | Endpoint | Purpose | When to Use |
|--------|----------|---------|-------------|
| `POST` | `/orders` | Create order | Place order from cart |
| `GET` | `/orders` | Get all orders | View your orders |
| `GET` | `/orders/{orderId}` | Get single order | View order details |
| `PATCH` | `/orders/{orderId}` | Update order | Modify order info |
| `DELETE` | `/orders/{orderId}` | Delete order | Cancel order |

**Example Sequence:**
```
1. POST /api-clients          → Register, get token
2. POST /carts                → Create cart
3. POST /carts/{id}/items     → Add items
4. POST /orders               → Create order (use token)
5. GET /orders                → View all orders
6. PATCH /orders/{orderId}    → Update order
7. DELETE /orders/{orderId}   → Cancel order
```

---

## Complete API Call Sequence

### Scenario: Customer Places a Grocery Order

```
Timeline of API Calls:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIME 1: [Browser/App opens]
        │
        ▼
        GET /status
        Purpose: "Is the API working?"
        Response: {"status": "UP"}
        │
        ▼
TIME 2: [Customer browses products]
        │
        ▼
        GET /products?category=coffee
        Purpose: "Show me coffee products"
        Response: [{id: 4643, name: "Starbucks...", ...}]
        │
        ▼
TIME 3: [Customer wants to shop]
        │
        ▼
        POST /api-clients
        Body: {"clientName": "MyApp", "clientEmail": "user@email.com"}
        Purpose: "Register for order access"
        Response: {"accessToken": "token123"}
        │
        ▼
TIME 4: [Customer starts shopping]
        │
        ▼
        POST /carts
        Purpose: "Create a new cart"
        Response: {"created": true, "cartId": "cart123"}
        │
        ▼
TIME 5: [Customer adds Starbucks coffee]
        │
        ▼
        POST /carts/cart123/items
        Body: {"productId": 4643, "quantity": 2}
        Purpose: "Add 2 coffees to cart"
        Response: {"itemId": "item456"}
        │
        ▼
TIME 6: [Customer adds more items]
        │
        ▼
        POST /carts/cart123/items
        Body: {"productId": 1709, "quantity": 1}
        Purpose: "Add steak to cart"
        Response: {"itemId": "item789"}
        │
        ▼
TIME 7: [Customer reviews cart]
        │
        ▼
        GET /carts/cart123/items
        Purpose: "Show me my cart"
        Response: [{id: item456, productId: 4643, ...}, 
                   {id: item789, productId: 1709, ...}]
        │
        ▼
TIME 8: [Customer changes mind, wants 3 coffees]
        │
        ▼
        PATCH /carts/cart123/items/item456
        Body: {"quantity": 3}
        Purpose: "Update coffee quantity to 3"
        Response: 204 No Content
        │
        ▼
TIME 9: [Customer places order]
        │
        ▼
        POST /orders
        Headers: Authorization: Bearer token123
        Body: {"cartId": "cart123", "customerName": "John Doe"}
        Purpose: "Complete the purchase"
        Response: {"orderId": "order999"}
        │
        ▼
TIME 10: [Customer views order confirmation]
         │
         ▼
         GET /orders/order999
         Headers: Authorization: Bearer token123
         Purpose: "Show order details"
         Response: {id: order999, customerName: "John Doe", ...}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd "D:\Simple Grocery Store API\pytest-framework"
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
pytest -v
```

### 3. Run Specific Test File

```bash
pytest tests/test_products.py -v   # Product tests
pytest tests/test_cart.py -v       # Cart tests
pytest tests/test_orders.py -v     # Order tests
```

### 4. Run Single Test

```bash
pytest tests/test_products.py::TestGetProducts::test_get_all_products -v
```

---

## Test Files Overview

| Test File | What It Tests | API Sequence |
|-----------|---------------|--------------|
| `test_products.py` | GET products, CRUD via cart | GET /products → POST /carts → CRUD items |
| `test_cart.py` | Complete cart workflow | POST /carts → POST items → PATCH → DELETE |
| `test_orders.py` | Auth + Orders workflow | POST /api-clients → POST /carts → POST /orders |

---

## Understanding HTTP Status Codes

| Code | Meaning | When You See It |
|------|---------|-----------------|
| `200` | OK | Successful GET request |
| `201` | Created | Successful POST (resource created) |
| `204` | No Content | Successful PUT/PATCH/DELETE |
| `400` | Bad Request | Invalid request body |
| `401` | Unauthorized | Missing or invalid token |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate registration |

---

## Configuration

Edit `config.py` to customize:

```python
# Change base URL
BASE_URL = "https://simple-grocery-store-api.click"

# Change test product IDs
TEST_PRODUCT_ID = 4643      # Starbucks Coffee
SECOND_PRODUCT_ID = 1709    # Beef Ribeye
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `ConnectionError` | Check internet connection |
| `404 Not Found` | Product ID may not exist |
| `401 Unauthorized` | Run `test_register_new_client` first |
| `409 Conflict` | Email already registered (use new email) |

---

## Learning Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Requests Library](https://requests.readthedocs.io/)
- [REST API Best Practices](https://restfulapi.net/)
