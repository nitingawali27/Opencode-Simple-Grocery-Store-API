"""
=============================================================================
CONFIG.PY - Configuration Settings
=============================================================================
This file contains all the configuration settings for the test framework.
Edit this file to change the API URL, headers, test data, or file paths.

What is this file for?
- Store the base URL of the API we want to test
- Define common headers used in all requests
- Set up paths for logs and reports folders
- Configure logging format and settings
=============================================================================
"""

import os
from datetime import datetime

# =============================================================================
# API Configuration
# =============================================================================
# These settings control how we connect to the Simple Grocery Store API

# The base URL of the API - all requests will be sent to this server
# Example: When we call /products, it becomes https://simple-grocery-store-api.click/products
BASE_URL = "https://simple-grocery-store-api.click"

# Common headers sent with every request
# - Content-Type: tells the server we're sending JSON data
# - Accept: tells the server we want JSON data back
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# How long to wait for a response before giving up (in seconds)
# If the API takes longer than this, the test will fail with a timeout error
TIMEOUT = 30

# =============================================================================
# Test Data
# =============================================================================
# These are the product IDs we use in our tests
# You can change these if you want to test with different products

# A valid product ID for testing (Starbucks Coffee)
TEST_PRODUCT_ID = 4643

# Another valid product ID for testing (Beef Ribeye Steak)
SECOND_PRODUCT_ID = 1709

# =============================================================================
# File Paths
# =============================================================================
# These settings control where logs and reports are saved

# Get the root folder of our project (where this config.py file is located)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder where log files will be saved
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# Folder where HTML test reports will be saved
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")

# Create the folders if they don't exist
# This ensures the folders are always available when tests run
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# =============================================================================
# Logging Configuration
# =============================================================================
# These settings control how our test logs look

# Log file name includes the timestamp so each run creates a new file
# Example: test_execution_20260329_155115.log
LOG_FILENAME = f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Full path to the log file
LOG_FILEPATH = os.path.join(LOGS_DIR, LOG_FILENAME)

# How log messages should be formatted
# %(asctime)s = date and time
# %(levelname)s = INFO, ERROR, WARNING, etc.
# %(message)s = the actual log message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# Date format used in logs
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
