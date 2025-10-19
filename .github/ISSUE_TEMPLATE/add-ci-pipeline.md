---
name: Add CI Pipeline with pytest
about: Set up continuous integration to run tests automatically
title: "[CI] Add GitHub Actions workflow for running pytest tests"
labels: ["enhancement", "ci", "testing"]
assignees: ""
---

## Description

Add a GitHub Actions workflow to automatically run pytest tests on every push and pull request.

## Current Status

- ✅ Basic pytest tests are implemented in `tests/test_db_connectivity.py`
- ✅ pytest is added as a dependency in `requirements.txt`
- ✅ pytest configuration is set up in `pytest.ini`

## Proposed CI Pipeline

The CI pipeline should:

1. **Trigger on:**
   - Push to main branch
   - Pull requests
   - Manual workflow dispatch

2. **Steps:**
   - Checkout code
   - Set up Python environment
   - Install dependencies from `requirements.txt`
   - Run pytest tests
   - Report test results

3. **Matrix testing:**
   - Test on Python 3.8, 3.9, 3.10, 3.11 (or latest stable versions)

## Files to Create

- `.github/workflows/test.yml` - GitHub Actions workflow file

## Example Workflow Structure

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest tests/ -v
```

## Acceptance Criteria

- [ ] GitHub Actions workflow file created
- [ ] Tests run automatically on push/PR
- [ ] Tests pass on multiple Python versions
- [ ] Test results are visible in PR checks
- [ ] Workflow is documented in README

## Additional Considerations

- Consider adding test coverage reporting
- Consider adding linting (flake8, black, etc.)
- Consider adding security scanning
- Consider caching dependencies for faster builds
