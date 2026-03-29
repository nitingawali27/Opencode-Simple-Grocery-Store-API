"""
=============================================================================
TEST_PRODUCTS.PY - Product Tests
=============================================================================
This file contains tests for:
1. GET requests to retrieve products
2. POST requests to create carts and add items
3. PUT requests to replace items
4. PATCH requests to modify items
5. DELETE requests to remove items

Note: The Simple Grocery Store API is a practice API for learning.
Products are read-only (no POST/PUT/DELETE for products themselves).
So we demonstrate CRUD operations using Cart endpoints instead.

Key Concepts:
- Each test function starts with "test_" so pytest can find it
- We use "setup_method" to run code before each test
- We use "assert" to check that responses are correct
- We use "print()" to show full responses in the console
=============================================================================
"""

import pytest
import logging
import json
from utils.api_client import APIClient
from config import TEST_PRODUCT_ID

# Create a logger for this module
# This logger writes to both console and log file
logger = logging.getLogger("test.products")


class TestGetProducts:
    """
    Test class for GET operations on products.
    
    GET = Retrieve data from the API (no changes are made)
    """
    
    def setup_method(self):
        """
        This runs BEFORE each test in this class.
        
        We create a fresh API client for each test to ensure
        tests are independent of each other.
        """
        self.client = APIClient()
        logger.info("APIClient initialized for test")

    def test_get_all_products(self):
        """
        Test: Retrieve all products from the API.
        
        This test:
        1. Makes a GET request to /products
        2. Prints the full response to console
        3. Verifies the status code is 200 (OK)
        4. Verifies we got a list of products
        """
        logger.info("Test: Get All Products")

        # Step 1: Make the API call
        response = self.client.get_all_products()

        # Step 2: Print response to console (so user can see it)
        print("\n" + "="*60)
        print("RESPONSE - Get All Products:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        # Step 3: Assert status code is 200
        # If this fails, the test fails with the error message
        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"

        # Step 4: Assert we got a list of products
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        assert len(products) > 0, "Product list should not be empty"
        
        logger.info(f"Successfully retrieved {len(products)} products")

    def test_get_products_by_category(self):
        """
        Test: Get products filtered by category.
        
        Query parameters:
        - category: Filter products by category (e.g., "coffee")
        """
        category = "coffee"
        logger.info(f"Test: Get Products by Category - {category}")

        # Make request with category filter
        response = self.client.get_all_products(category=category)

        # Print response
        print("\n" + "="*60)
        print(f"RESPONSE - Get Products by Category ({category}):")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        # Verify response
        assert response.status_code == 200
        
        # Verify all products have the correct category
        products = response.json()
        for product in products:
            assert product["category"] == category, \
                f"Product {product['id']} has wrong category"
        
        logger.info(f"Successfully retrieved {len(products)} products in {category}")

    def test_get_products_with_limit(self):
        """
        Test: Get a limited number of products.
        
        Query parameters:
        - results: Maximum number of products to return (1-20)
        """
        limit = 5
        logger.info(f"Test: Get Products with Limit - {limit}")

        response = self.client.get_all_products(results=limit)

        print("\n" + "="*60)
        print(f"RESPONSE - Get Products (Limit: {limit}):")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200

        products = response.json()
        assert len(products) <= limit, \
            f"Expected at most {limit} products, got {len(products)}"
        
        logger.info(f"Successfully retrieved {len(products)} products (limit: {limit})")

    def test_get_single_product(self):
        """
        Test: Get a single product by its ID.
        
        URL path parameter:
        - productId: The unique ID of the product (e.g., 4643)
        """
        logger.info(f"Test: Get Single Product - ID: {TEST_PRODUCT_ID}")

        response = self.client.get_product(TEST_PRODUCT_ID)

        print("\n" + "="*60)
        print(f"RESPONSE - Get Product (ID: {TEST_PRODUCT_ID}):")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200

        product = response.json()
        assert product["id"] == TEST_PRODUCT_ID, \
            f"Expected product ID {TEST_PRODUCT_ID}, got {product['id']}"
        assert "name" in product, "Product should have a name"
        assert "category" in product, "Product should have a category"
        
        logger.info(f"Successfully retrieved product: {product.get('name')}")

    def test_get_product_not_found(self):
        """
        Test: Request a product that doesn't exist.
        
        Expected behavior: 404 Not Found status code
        """
        fake_id = 999999
        logger.info(f"Test: Get Product Not Found - ID: {fake_id}")

        response = self.client.get_product(fake_id)

        print("\n" + "="*60)
        print(f"RESPONSE - Get Product Not Found (ID: {fake_id}):")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print("="*60 + "\n")

        # 404 means "not found" - this is expected for invalid IDs
        assert response.status_code == 404, \
            f"Expected status 404, got {response.status_code}"
        
        logger.info("Correctly returned 404 for non-existent product")


class TestAPIStatus:
    """Test class for checking API health status."""
    
    def setup_method(self):
        """Create a fresh API client for each test."""
        self.client = APIClient()

    def test_api_status(self):
        """
        Test: Check if the API is running and healthy.
        
        This is useful to verify the API is up before running other tests.
        Expected response: {"status": "UP"}
        """
        logger.info("Test: API Status Check")

        response = self.client.get_status()

        print("\n" + "="*60)
        print("RESPONSE - API Status:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        print("="*60 + "\n")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "UP", f"API status is not UP: {data}"
        
        logger.info("API is UP and running")


class TestCartCRUDOperations:
    """
    Test class demonstrating CRUD operations using Cart endpoints.
    
    CRUD = Create, Read, Update, Delete
    
    Since products are read-only in this API, we use carts to
    demonstrate all four operations:
    
    - CREATE: POST /carts (create cart), POST /carts/{id}/items (add item)
    - READ: GET /carts/{id} (get cart), GET /carts/{id}/items (get items)
    - UPDATE: PATCH /carts/{id}/items/{itemId} (modify quantity)
    - UPDATE: PUT /carts/{id}/items/{itemId} (replace item)
    - DELETE: DELETE /carts/{id}/items/{itemId} (remove item)
    """
    
    def setup_method(self):
        """Create a fresh API client for each test."""
        self.client = APIClient()
        self.cart_id = None

    def teardown_method(self):
        """
        This runs AFTER each test in this class.
        Carts are automatically cleaned up by the API, so no action needed.
        """
        pass

    def test_post_create_cart(self):
        """
        POST - Create a new cart.
        
        HTTP Method: POST
        Endpoint: /carts
        Body: None (empty request)
        
        Expected Response:
        - Status: 201 Created
        - Body: {"created": true, "cartId": "xyz123"}
        """
        logger.info("Test: POST - Create Cart")

        response = self.client.create_cart()

        print("\n" + "="*60)
        print("RESPONSE - POST Create Cart:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        # 201 means "Created" - resource was successfully created
        assert response.status_code == 201, \
            f"Expected status 201, got {response.status_code}"

        data = response.json()
        assert data["created"] is True, "Cart should be marked as created"
        assert "cartId" in data, "Response should contain cartId"
        self.cart_id = data["cartId"]
        
        logger.info(f"Successfully created cart: {self.cart_id}")

    def test_post_add_item_to_cart(self):
        """
        POST - Add an item to a cart.
        
        HTTP Method: POST
        Endpoint: /carts/{cartId}/items
        Body: {"productId": 4643, "quantity": 2}
        
        Expected Response:
        - Status: 201 Created
        - Body: {"itemId": "abc123"}
        """
        logger.info("Test: POST - Add Item to Cart")

        # First, we need a cart
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        logger.info(f"Created cart: {cart_id}")

        # Now add an item to the cart
        response = self.client.add_item_to_cart(
            cart_id=cart_id,
            product_id=TEST_PRODUCT_ID,
            quantity=2
        )

        print("\n" + "="*60)
        print("RESPONSE - POST Add Item to Cart:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 201, \
            f"Expected status 201, got {response.status_code}"

        data = response.json()
        assert "itemId" in data, "Response should contain itemId"
        
        logger.info(f"Successfully added item to cart. Item ID: {data['itemId']}")

    def test_get_cart_details(self):
        """
        GET - Retrieve cart details.
        
        HTTP Method: GET
        Endpoint: /carts/{cartId}
        
        Expected Response:
        - Status: 200 OK
        - Body: {"created": "2026-01-01T00:00:00Z", "items": [...]}
        """
        logger.info("Test: GET - Cart Details")

        # Create a cart and add an item first
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        self.client.add_item_to_cart(cart_id, TEST_PRODUCT_ID, 1)

        # Now get the cart details
        response = self.client.get_cart(cart_id)

        print("\n" + "="*60)
        print("RESPONSE - GET Cart Details:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"

        cart = response.json()
        assert "created" in cart, "Cart should have created timestamp"
        assert "items" in cart, "Cart should have items list"
        
        logger.info("Successfully retrieved cart details")

    def test_get_cart_items(self):
        """
        GET - Retrieve all items in a cart.
        
        HTTP Method: GET
        Endpoint: /carts/{cartId}/items
        
        Expected Response:
        - Status: 200 OK
        - Body: [{"id": "item1", "productId": 4643, ...}, ...]
        """
        logger.info("Test: GET - Cart Items")

        # Create a cart and add an item
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        self.client.add_item_to_cart(cart_id, TEST_PRODUCT_ID, 1)

        # Get the items
        response = self.client.get_cart_items(cart_id)

        print("\n" + "="*60)
        print("RESPONSE - GET Cart Items:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"

        items = response.json()
        assert isinstance(items, list), "Items should be a list"
        assert len(items) > 0, "Cart should have at least one item"
        
        logger.info(f"Successfully retrieved {len(items)} items from cart")

    def test_patch_modify_item_quantity(self):
        """
        PATCH - Modify item quantity in cart.
        
        HTTP Method: PATCH
        Endpoint: /carts/{cartId}/items/{itemId}
        Body: {"quantity": 5}
        
        PATCH is used for partial updates - we only change the quantity.
        
        Expected Response:
        - Status: 204 No Content (success, no response body)
        """
        logger.info("Test: PATCH - Modify Item Quantity")

        # Create cart and add item
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        item_response = self.client.add_item_to_cart(cart_id, TEST_PRODUCT_ID, 1)
        item_id = item_response.json()["itemId"]

        # Modify the quantity from 1 to 5
        response = self.client.modify_cart_item(cart_id, item_id, 5)

        print("\n" + "="*60)
        print("RESPONSE - PATCH Modify Item Quantity:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"(No content - 204 indicates success)")
        print("="*60 + "\n")

        # 204 means "No Content" - the update was successful
        assert response.status_code == 204, \
            f"Expected status 204, got {response.status_code}"
        
        logger.info("Successfully modified item quantity")

    def test_put_replace_item(self):
        """
        PUT - Replace an item in cart with a different product.
        
        HTTP Method: PUT
        Endpoint: /carts/{cartId}/items/{itemId}
        Body: {"productId": 1709, "quantity": 3}
        
        PUT is used to replace the entire resource.
        Here we replace one product with another.
        
        Expected Response:
        - Status: 204 No Content
        """
        logger.info("Test: PUT - Replace Item")

        # Create cart and add item
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        item_response = self.client.add_item_to_cart(cart_id, TEST_PRODUCT_ID, 1)
        item_id = item_response.json()["itemId"]

        # Replace with different product (product ID 1709)
        response = self.client.replace_cart_item(
            cart_id, item_id, product_id=1709, quantity=3
        )

        print("\n" + "="*60)
        print("RESPONSE - PUT Replace Item:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"(No content - 204 indicates success)")
        print("="*60 + "\n")

        assert response.status_code == 204, \
            f"Expected status 204, got {response.status_code}"
        
        logger.info("Successfully replaced item in cart")

    def test_delete_item_from_cart(self):
        """
        DELETE - Remove an item from cart.
        
        HTTP Method: DELETE
        Endpoint: /carts/{cartId}/items/{itemId}
        Body: None
        
        Expected Response:
        - Status: 204 No Content
        """
        logger.info("Test: DELETE - Remove Item from Cart")

        # Create cart and add item
        cart_response = self.client.create_cart()
        cart_id = cart_response.json()["cartId"]
        item_response = self.client.add_item_to_cart(cart_id, TEST_PRODUCT_ID, 1)
        item_id = item_response.json()["itemId"]

        # Delete the item
        response = self.client.delete_cart_item(cart_id, item_id)

        print("\n" + "="*60)
        print("RESPONSE - DELETE Item from Cart:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"(No content - 204 indicates success)")
        print("="*60 + "\n")

        assert response.status_code == 204, \
            f"Expected status 204, got {response.status_code}"

        # Verify the cart is now empty
        items_response = self.client.get_cart_items(cart_id)
        assert len(items_response.json()) == 0, "Cart should be empty after deletion"
        
        logger.info("Successfully deleted item from cart")
