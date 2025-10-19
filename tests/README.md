# Tests

This directory contains tests for the Chat-SQL application.

## Running Tests

To run the tests, make sure you have pytest installed:

```bash
pip install pytest
```

Then run the tests from the project root:

```bash
pytest
```

Or run with verbose output:

```bash
pytest -v
```

## Test Structure

- `test_db_connectivity.py`: Tests for SQLite database connectivity and STUDENT table existence

## Adding New Tests

When adding new tests:

1. Create test files with the prefix `test_`
2. Use descriptive test function names starting with `test_`
3. Group related tests in classes that start with `Test`
4. Use pytest fixtures for setup and teardown
