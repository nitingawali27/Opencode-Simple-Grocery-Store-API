"""
=============================================================================
TEST_CART.PY - Cart Workflow Tests
=============================================================================
This file contains tests for the complete cart workflow.
It demonstrates how to chain multiple operations together.

Key Concepts:
- pytest fixtures with "yield" for setup and teardown
- Chaining operations: create cart -> add items -> modify -> delete
- Full workflow testing instead of individual operations
=============================================================================
"""

import pytest
import logging
import json
from utils.api_client import APIClient
from config import TEST_PRODUCT_ID, SECOND_PRODUCT_ID

# Create logger for this module
logger = logging.getLogger("test.cart")


class TestCartWorkflow:
    """
    Test class for complete cart workflow tests.
    
    Instead of testing individual operations, these tests
    chain multiple operations together to simulate real usage.
    """
    
    @pytest.fixture(autouse=True)
    def setup_cart(self):
        """
        Fixture that creates a fresh cart before each test.
        
        - "autouse=True" means it runs automatically for every test
        - "yield" separates setup from teardown
        - Code before yield = setup (runs before test)
        - Code after yield = teardown (runs after test)
        """
        # SETUP: Create API client and cart
        self.client = APIClient()
        self.cart_id = None
        self.item_ids = []

        # Create a new cart for this test
        response = self.client.create_cart()
        if response.status_code == 201:
            self.cart_id = response.json()["cartId"]
            logger.info(f"Created test cart: {self.cart_id}")

        # Yield control to the test
        yield

        # TEARDOWN: Clean up after test completes
        logger.info(f"Test completed for cart: {self.cart_id}")

    def test_full_cart_workflow(self):
        """
        Test the complete cart workflow from start to finish.
        
        Steps:
        1. Verify cart was created
        2. Add first product to cart
        3. Add second product to cart
        4. View all items in cart
        5. Modify quantity of first item
        6. Delete second item
        7. Verify final cart state
        """
        logger.info("Starting full cart workflow test")

        # STEP 1: Verify cart was created
        print("\n" + "="*70)
        print("STEP 1: Verify Cart Creation")
        print("="*70)
        response = self.client.get_cart(self.cart_id)
        print(f"Status: {response.status_code}")
        print(f"Cart: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        logger.info("Step 1: Cart verified")

        # STEP 2: Add first product to cart
        print("\n" + "="*70)
        print("STEP 2: Add First Item to Cart")
        print("="*70)
        response = self.client.add_item_to_cart(self.cart_id, TEST_PRODUCT_ID, 2)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 201
        item_id_1 = response.json()["itemId"]
        self.item_ids.append(item_id_1)
        logger.info(f"Step 2: Added item {item_id_1}")

        # STEP 3: Add second product to cart
        print("\n" + "="*70)
        print("STEP 3: Add Second Item to Cart")
        print("="*70)
        response = self.client.add_item_to_cart(self.cart_id, SECOND_PRODUCT_ID, 1)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 201
        item_id_2 = response.json()["itemId"]
        self.item_ids.append(item_id_2)
        logger.info(f"Step 3: Added item {item_id_2}")

        # STEP 4: View all items in cart
        print("\n" + "="*70)
        print("STEP 4: Get All Cart Items")
        print("="*70)
        response = self.client.get_cart_items(self.cart_id)
        print(f"Status: {response.status_code}")
        print(f"Items: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert len(response.json()) == 2
        logger.info("Step 4: Retrieved 2 items from cart")

        # STEP 5: Modify quantity of first item
        print("\n" + "="*70)
        print("STEP 5: Modify First Item Quantity")
        print("="*70)
        response = self.client.modify_cart_item(self.cart_id, item_id_1, 5)
        print(f"Status: {response.status_code}")
        assert response.status_code == 204
        logger.info("Step 5: Modified item quantity to 5")

        # STEP 6: Delete second item
        print("\n" + "="*70)
        print("STEP 6: Delete Second Item")
        print("="*70)
        response = self.client.delete_cart_item(self.cart_id, item_id_2)
        print(f"Status: {response.status_code}")
        assert response.status_code == 204
        logger.info("Step 6: Deleted second item")

        # STEP 7: Verify final cart state
        print("\n" + "="*70)
        print("STEP 7: Verify Final Cart State")
        print("="*70)
        response = self.client.get_cart_items(self.cart_id)
        print(f"Status: {response.status_code}")
        print(f"Items: {json.dumps(response.json(), indent=2)}")
        assert len(response.json()) == 1
        logger.info("Step 7: Cart has 1 item as expected")

        print("\n" + "="*70)
        print("FULL CART WORKFLOW TEST COMPLETED SUCCESSFULLY")
        print("="*70)

    def test_replace_item_in_cart(self):
        """Test replacing an item in the cart with a different product."""
        logger.info("Testing item replacement")

        response = self.client.add_item_to_cart(self.cart_id, TEST_PRODUCT_ID, 1)
        item_id = response.json()["itemId"]
        print(f"\nOriginal item added: {item_id}")

        response = self.client.replace_cart_item(
            self.cart_id, item_id, product_id=SECOND_PRODUCT_ID, quantity=3
        )
        print(f"Replace status: {response.status_code}")
        assert response.status_code == 204

        items = self.client.get_cart_items(self.cart_id).json()
        print(f"Cart items after replacement: {json.dumps(items, indent=2)}")
        assert items[0]["productId"] == SECOND_PRODUCT_ID
        logger.info("Item replacement successful")

    def test_empty_cart(self):
        """Test retrieving an empty cart."""
        logger.info("Testing empty cart")

        response = self.client.get_cart_items(self.cart_id)
        print(f"\nEmpty cart response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert len(response.json()) == 0
        logger.info("Empty cart verified")

    def test_nonexistent_cart(self):
        """Test accessing a cart that doesn't exist."""
        logger.info("Testing non-existent cart")

        response = self.client.get_cart("fake_cart_id_12345")
        print(f"\nNon-existent cart status: {response.status_code}")
        assert response.status_code == 404
        logger.info("Non-existent cart returned 404 as expected")
