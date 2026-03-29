"""
=============================================================================
API_CLIENT.PY - API Client Class
=============================================================================
This file contains the APIClient class that handles all API requests.
Instead of writing request code in every test file, we use this class.

What is this class for?
- Makes HTTP requests (GET, POST, PUT, PATCH, DELETE) to the API
- Automatically logs all requests and responses
- Provides easy-to-use methods like get_all_products(), create_cart(), etc.

How to use it:
    from utils.api_client import APIClient
    
    # Create a client instance
    client = APIClient()
    
    # Make a request
    response = client.get_all_products()
    print(response.status_code)  # 200
    print(response.json())       # The actual data
=============================================================================
"""

import requests
import logging
import json
from config import BASE_URL, HEADERS, TIMEOUT

# Create a logger for this module
# This logger writes to both the console and the log file
logger = logging.getLogger("api_client")


class APIClient:
    """
    A simple API client for making HTTP requests to the Simple Grocery Store API.
    
    All requests are automatically logged with:
    - Request URL and method
    - Request body (for POST/PUT/PATCH)
    - Response status code
    - Response body
    
    Example usage:
        client = APIClient()
        response = client.get_all_products()
        if response.status_code == 200:
            products = response.json()
    """
    
    def __init__(self, base_url=BASE_URL):
        """
        Initialize the API client.
        
        Args:
            base_url (str): The base URL of the API
                          Default: https://simple-grocery-store-api.click
        """
        # Store the base URL for all requests
        self.base_url = base_url
        
        # Copy the common headers (we'll add auth token later if needed)
        self.headers = HEADERS.copy()
        
        # Store the access token (None until we register)
        self.access_token = None
        
        # Log that the client was created
        logger.info(f"API Client initialized with base URL: {self.base_url}")
    
    def set_auth_token(self, token):
        """
        Set the authorization token for authenticated requests.
        
        Some API endpoints require authentication. After registering
        a new client, we get a token that we set here.
        
        Args:
            token (str): The access token from /api-clients registration
        """
        self.access_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        logger.info("Authorization token set successfully")
    
    # =========================================================================
    # PRIVATE HELPER METHODS (used internally)
    # =========================================================================
    
    def _log_request(self, method, url, data=None, params=None):
        """Log the details of an outgoing request."""
        logger.info(f"{'='*60}")
        logger.info(f"REQUEST: {method} {url}")
        if params:
            logger.info(f"QUERY PARAMS: {json.dumps(params, indent=2)}")
        if data:
            logger.info(f"REQUEST BODY: {json.dumps(data, indent=2)}")
        logger.info(f"{'='*60}")
    
    def _log_response(self, response):
        """Log the details of a response."""
        logger.info(f"RESPONSE STATUS: {response.status_code} {response.reason}")
        try:
            response_body = response.json()
            logger.info(f"RESPONSE BODY: {json.dumps(response_body, indent=2)}")
        except:
            logger.info(f"RESPONSE BODY: {response.text}")
        logger.info(f"{'='*60}\n")
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make an HTTP request and log everything."""
        url = f"{self.base_url}{endpoint}"
        self._log_request(method, url, data, params)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=TIMEOUT
            )
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"REQUEST FAILED: {str(e)}")
            raise
    
    # =========================================================================
    # GET METHODS - Retrieve data from the API
    # =========================================================================
    
    def get(self, endpoint, params=None):
        """Make a GET request to the API."""
        return self._make_request("GET", endpoint, params=params)
    
    def get_all_products(self, category=None, results=None, available=None):
        """Get all products with optional filters."""
        params = {}
        if category:
            params["category"] = category
        if results:
            params["results"] = results
        if available is not None:
            params["available"] = str(available).lower()
        return self.get("/products", params=params if params else None)
    
    def get_product(self, product_id):
        """Get a single product by its ID."""
        return self.get(f"/products/{product_id}")
    
    def get_status(self):
        """Check if the API is running."""
        return self.get("/status")
    
    def get_cart(self, cart_id):
        """Get cart details."""
        return self.get(f"/carts/{cart_id}")
    
    def get_cart_items(self, cart_id):
        """Get all items in a cart."""
        return self.get(f"/carts/{cart_id}/items")
    
    def get_all_orders(self):
        """Get all orders (requires authentication)."""
        return self.get("/orders")
    
    def get_order(self, order_id):
        """Get a single order (requires authentication)."""
        return self.get(f"/orders/{order_id}")
    
    # =========================================================================
    # POST METHODS - Create new resources
    # =========================================================================
    
    def post(self, endpoint, data=None):
        """Make a POST request to the API."""
        return self._make_request("POST", endpoint, data=data)
    
    def create_cart(self):
        """Create a new empty shopping cart."""
        return self.post("/carts")
    
    def add_item_to_cart(self, cart_id, product_id, quantity=1):
        """Add a product to a cart."""
        data = {"productId": product_id, "quantity": quantity}
        return self.post(f"/carts/{cart_id}/items", data=data)
    
    def register_client(self, client_name, client_email):
        """Register a new API client and get an access token."""
        data = {"clientName": client_name, "clientEmail": client_email}
        response = self.post("/api-clients", data=data)
        if response.status_code == 201:
            self.set_auth_token(response.json().get("accessToken"))
        return response
    
    def create_order(self, cart_id, customer_name, comment=None):
        """Create a new order from a cart (requires authentication)."""
        data = {"cartId": cart_id, "customerName": customer_name}
        if comment:
            data["comment"] = comment
        return self.post("/orders", data=data)
    
    # =========================================================================
    # PUT METHODS - Replace resources completely
    # =========================================================================
    
    def put(self, endpoint, data=None):
        """Make a PUT request to the API."""
        return self._make_request("PUT", endpoint, data=data)
    
    def replace_cart_item(self, cart_id, item_id, product_id, quantity=1):
        """Replace a cart item with a different product."""
        data = {"productId": product_id, "quantity": quantity}
        return self.put(f"/carts/{cart_id}/items/{item_id}", data=data)
    
    # =========================================================================
    # PATCH METHODS - Update parts of a resource
    # =========================================================================
    
    def patch(self, endpoint, data=None):
        """Make a PATCH request to the API."""
        return self._make_request("PATCH", endpoint, data=data)
    
    def modify_cart_item(self, cart_id, item_id, quantity):
        """Update the quantity of an item in the cart."""
        data = {"quantity": quantity}
        return self.patch(f"/carts/{cart_id}/items/{item_id}", data=data)
    
    def update_order(self, order_id, customer_name=None, comment=None):
        """Update an order (requires authentication)."""
        data = {}
        if customer_name:
            data["customerName"] = customer_name
        if comment:
            data["comment"] = comment
        return self.patch(f"/orders/{order_id}", data=data)
    
    # =========================================================================
    # DELETE METHODS - Remove resources
    # =========================================================================
    
    def delete(self, endpoint):
        """Make a DELETE request to the API."""
        return self._make_request("DELETE", endpoint)
    
    def delete_cart_item(self, cart_id, item_id):
        """Remove an item from a cart."""
        return self.delete(f"/carts/{cart_id}/items/{item_id}")
    
    def delete_order(self, order_id):
        """Delete an order (requires authentication)."""
        return self.delete(f"/orders/{order_id}")
