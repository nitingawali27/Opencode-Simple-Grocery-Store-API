"""
=============================================================================
CONFTEST.PY - Pytest Configuration and Fixtures
=============================================================================
This file contains pytest configuration and fixtures that are automatically
used by all test files. You don't need to import anything from this file -
pytest automatically loads it.

What is this file for?
- Set up logging before tests start
- Configure HTML report generation
- Log the start and end of each test
- Log test results (passed/failed)

Key Concepts:
- "Fixtures" are setup/teardown functions that run before/after tests
- "Hooks" are special pytest functions that let you customize behavior
- "autouse=True" means the fixture runs automatically for every test
=============================================================================
"""

import pytest
import logging
import os
from datetime import datetime
from config import LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT, REPORTS_DIR

# =============================================================================
# LOGGING SETUP (Runs before any tests)
# =============================================================================
# We set up logging here so it's ready before any test runs

# Create a unique timestamp for this test run
# This ensures each test run has its own log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filepath = os.path.join(LOGS_DIR, f"test_execution_{timestamp}.log")

# File Handler - writes logs to a file
# This saves all logs to: logs/test_execution_YYYYMMDD_HHMMSS.log
file_handler = logging.FileHandler(log_filepath)
file_handler.setLevel(logging.INFO)  # Only save INFO level and above
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

# Console Handler - prints logs to the terminal
# This shows logs in the console as tests run
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

# Configure the root logger - this is the main logger for the entire application
# Both file and console handlers are added so logs go to both places
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """
    This function runs once when pytest starts up.
    It configures the HTML report file path.
    
    Args:
        config: pytest configuration object
    """
    # Create timestamp for the HTML report filename
    report_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"{REPORTS_DIR}/test_report_{report_timestamp}.html"
    
    # Tell pytest where to save the HTML report
    config.option.htmlpath = report_path
    
    # Log the configuration details
    root_logger.info("=" * 70)
    root_logger.info("PYTEST CONFIGURATION")
    root_logger.info(f"Log file: {log_filepath}")
    root_logger.info(f"Report file: {report_path}")
    root_logger.info("=" * 70)


# =============================================================================
# FIXTURES (Setup/Teardown for tests)
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """
    Session-scoped fixture that logs session start/end.
    
    - "scope='session'" means this runs ONCE for the entire test session
    - "autouse=True" means this runs automatically without being requested
    
    Yields:
        The root logger for use in tests
    """
    # Log that the test session is starting
    root_logger.info("=" * 70)
    root_logger.info("TEST SESSION STARTED")
    root_logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    root_logger.info("=" * 70)
    
    # "yield" pauses here and lets tests run
    # After all tests complete, the code after yield runs
    yield root_logger
    
    # Log that the test session has ended
    root_logger.info("=" * 70)
    root_logger.info("TEST SESSION COMPLETED")
    root_logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    root_logger.info("=" * 70)


@pytest.fixture(autouse=True)
def log_test_name(request):
    """
    Function-scoped fixture that logs the start/end of each test.
    
    - "autouse=True" means this runs for EVERY test automatically
    - The "request" parameter gives us info about the current test
    
    Args:
        request: pytest request object containing test info
    """
    # Get the name of the test that's about to run
    test_name = request.node.nodeid
    # Example: tests/test_products.py::TestGetProducts::test_get_all_products
    
    # Log that the test is starting
    root_logger.info(f"\n{'#'*70}")
    root_logger.info(f"STARTING TEST: {test_name}")
    root_logger.info(f"{'#'*70}")
    
    # Let the test run
    yield
    
    # After the test completes, log that it finished
    root_logger.info(f"{'#'*70}")
    root_logger.info(f"COMPLETED TEST: {test_name}")
    root_logger.info(f"{'#'*70}\n")


# =============================================================================
# PYTEST HOOKS (Custom pytest behavior)
# =============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook that runs after each test to log the result.
    
    This is called by pytest after every test runs.
    We use it to log whether the test passed or failed.
    
    Args:
        item: The test item that was run
        call: The call phase information
    """
    # Get the test result
    outcome = yield
    report = outcome.get_result()
    
    # Only process the "call" phase (not setup/teardown)
    if report.when == "call":
        if report.failed:
            # Test failed - log the error
            root_logger.error(f"TEST FAILED: {item.nodeid}")
            if report.longrepr:
                root_logger.error(f"FAILURE DETAILS: {report.longrepr}")
        else:
            # Test passed - log success
            root_logger.info(f"TEST PASSED: {item.nodeid}")
