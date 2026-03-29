"""
=============================================================================
TEST_ORDERS.PY - Authentication and Order Tests
=============================================================================
This file contains tests for:
1. API client registration (getting an access token)
2. Creating orders from carts
3. Managing orders (get, update, delete)
4. Authentication error handling

Key Concepts:
- Authentication: Some endpoints require a special token
- Access Token: A unique string that identifies and authorizes you
- Bearer Token: The type of authentication used by this API
- Order Workflow: register -> create cart -> add items -> create order
=============================================================================
"""

import pytest
import logging
import json
import uuid
from utils.api_client import APIClient
from config import TEST_PRODUCT_ID

# Create logger for this module
logger = logging.getLogger("test.orders")


class TestAuthentication:
    """
    Test class for API client registration and authentication.
    
    Before making order-related requests, you must:
    1. Register a new API client (or use existing email)
    2. Receive an access token
    3. Use the token in the Authorization header
    """
    
    def setup_method(self):
        """Create a fresh API client for each test."""
        self.client = APIClient()

    def test_register_new_client(self):
        """
        Test registering a new API client.
        
        This is the first step to get an access token.
        
        Request Body:
        - clientName: Any string to identify your client
        - clientEmail: An email address (doesn't need to be real!)
        
        Expected Response:
        - Status: 201 Created
        - Body: {"accessToken": "your_token_here"}
        """
        # Generate unique name and email to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        client_name = f"Test Client {unique_id}"
        client_email = f"test_{unique_id}@example.com"

        logger.info(f"Registering new client: {client_name}")

        response = self.client.register_client(client_name, client_email)

        print("\n" + "="*60)
        print("RESPONSE - Register New Client:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 201
        data = response.json()
        assert "accessToken" in data
        assert len(data["accessToken"]) > 0
        
        logger.info(f"Successfully registered client. Token: {data['accessToken'][:20]}...")

    def test_register_duplicate_email(self):
        """
        Test that registering with an already-used email returns an error.
        
        Expected behavior: 409 Conflict
        """
        client_name = "Duplicate Test"
        client_email = "duplicate_test@example.com"

        # First registration - should succeed
        self.client.register_client(client_name, client_email)

        # Try again with same email - should fail
        response = self.client.register_client(client_name, client_email)

        print("\n" + "="*60)
        print("RESPONSE - Duplicate Registration:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print("="*60 + "\n")

        assert response.status_code == 409
        logger.info("Duplicate email correctly rejected with 409")


class TestOrderWorkflow:
    """
    Test class for the complete order workflow.
    
    Full workflow:
    1. Register client (get token)
    2. Create a cart
    3. Add items to cart
    4. Create order from cart
    5. View/update/delete orders
    """
    
    @pytest.fixture(autouse=True)
    def setup_order_environment(self):
        """
        Fixture that sets up everything needed for order tests.
        
        This runs BEFORE each test:
        1. Create API client
        2. Register new client (get token)
        3. Create a cart
        4. Add an item to cart
        """
        self.client = APIClient()
        self.cart_id = None
        self.order_id = None

        # Register a new client to get access token
        unique_id = str(uuid.uuid4())[:8]
        self.client.register_client(
            f"Order Test {unique_id}",
            f"order_test_{unique_id}@example.com"
        )
        logger.info("Registered new client for order test")

        # Create a cart and add an item
        cart_response = self.client.create_cart()
        self.cart_id = cart_response.json()["cartId"]
        self.client.add_item_to_cart(self.cart_id, TEST_PRODUCT_ID, 2)
        logger.info(f"Created cart {self.cart_id} with item")

        yield

        # TEARDOWN: Clean up the order if it was created
        if self.order_id:
            self.client.delete_order(self.order_id)
            logger.info(f"Cleaned up order: {self.order_id}")

    def test_create_order(self):
        """
        Test creating a new order.
        
        Request Body:
        - cartId: The cart to convert to an order
        - customerName: Name of the customer
        - comment: Optional order notes
        
        Expected Response:
        - Status: 201 Created
        - Body: {"orderId": "your_order_id"}
        """
        logger.info("Test: Create Order")

        response = self.client.create_order(
            cart_id=self.cart_id,
            customer_name="John Doe",
            comment="Please prepare quickly"
        )

        print("\n" + "="*60)
        print("RESPONSE - Create Order:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 201
        data = response.json()
        assert "orderId" in data
        self.order_id = data["orderId"]
        
        logger.info(f"Order created successfully: {self.order_id}")

    def test_get_all_orders(self):
        """Test retrieving all orders for the authenticated client."""
        logger.info("Test: Get All Orders")

        create_response = self.client.create_order(self.cart_id, "Test Customer")
        self.order_id = create_response.json()["orderId"]

        response = self.client.get_all_orders()

        print("\n" + "="*60)
        print("RESPONSE - Get All Orders:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        assert len(orders) > 0
        
        logger.info(f"Retrieved {len(orders)} orders")

    def test_get_single_order(self):
        """Test retrieving a single order by its ID."""
        logger.info("Test: Get Single Order")

        create_response = self.client.create_order(self.cart_id, "Test Customer")
        order_id = create_response.json()["orderId"]

        response = self.client.get_order(order_id)

        print("\n" + "="*60)
        print("RESPONSE - Get Single Order:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        print("="*60 + "\n")

        assert response.status_code == 200
        order = response.json()
        assert order["id"] == order_id
        assert "customerName" in order
        
        logger.info(f"Retrieved order: {order_id}")

    def test_update_order(self):
        """Test updating an existing order."""
        logger.info("Test: Update Order")

        create_response = self.client.create_order(self.cart_id, "Original Name")
        order_id = create_response.json()["orderId"]

        response = self.client.update_order(
            order_id,
            customer_name="Updated Name",
            comment="Updated comment"
        )

        print("\n" + "="*60)
        print("RESPONSE - Update Order:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print("(No content - 204 indicates success)")
        print("="*60 + "\n")

        assert response.status_code == 204

        get_response = self.client.get_order(order_id)
        order = get_response.json()
        assert order["customerName"] == "Updated Name"
        
        logger.info(f"Order updated successfully: {order_id}")

    def test_delete_order(self):
        """Test deleting an order."""
        logger.info("Test: Delete Order")

        create_response = self.client.create_order(self.cart_id, "Delete Test")
        order_id = create_response.json()["orderId"]

        response = self.client.delete_order(order_id)

        print("\n" + "="*60)
        print("RESPONSE - Delete Order:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print("(No content - 204 indicates success)")
        print("="*60 + "\n")

        assert response.status_code == 204

        get_response = self.client.get_order(order_id)
        assert get_response.status_code == 404

        self.order_id = None
        logger.info(f"Order deleted successfully: {order_id}")

    def test_unauthorized_access(self):
        """Test that requests without authentication return an error."""
        logger.info("Test: Unauthorized Access")

        # Create a client WITHOUT registration (no token)
        unauth_client = APIClient()
        response = unauth_client.get_all_orders()

        print("\n" + "="*60)
        print("RESPONSE - Unauthorized Access:")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print("="*60 + "\n")

        assert response.status_code == 401
        logger.info("Unauthorized request correctly rejected with 401")
