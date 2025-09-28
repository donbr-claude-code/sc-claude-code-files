# Streamlit Dashboard Testing with Playwright

This document describes the comprehensive testing setup for the e-commerce analytics dashboard built with Streamlit.

## Overview

The testing suite uses Playwright to automate browser testing of the Streamlit dashboard, validating:
- UI components and layout
- Data interactions and filtering
- Chart rendering and responsiveness
- Visual regression testing
- Cross-device compatibility

## Test Structure

### Test Files

- `tests/test_dashboard_core.py` - Core dashboard functionality and layout tests
- `tests/test_dashboard_interactions.py` - Data filtering and interaction tests
- `tests/test_dashboard_visual.py` - Visual regression and chart validation tests
- `tests/conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest configuration
- `run_tests.py` - Test runner script

### Test Categories

**Core Tests (`test_dashboard_core.py`)**
- Dashboard loads successfully
- All KPI cards present and properly formatted
- Date input controls working
- Chart sections rendering
- CSS styling applied correctly
- No error messages displayed

**Interaction Tests (`test_dashboard_interactions.py`)**
- Date range filtering updates metrics
- Charts respond to date changes
- Period comparison trends update
- No-data scenarios handled gracefully
- Metric consistency across filters
- Browser refresh maintains functionality

**Visual Tests (`test_dashboard_visual.py`)**
- Screenshot baseline generation
- Chart visual validation
- Responsive design (mobile/tablet)
- Color scheme consistency
- Loading states
- Print-friendly layout

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --type core
python run_tests.py --type interactions
python run_tests.py --type visual

# Run fast tests only (skip slow visual tests)
python run_tests.py --type fast

# Verbose output
python run_tests.py --verbose
```

### Manual Test Execution

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_dashboard_core.py

# Run with verbose output
uv run pytest -v tests/

# Run tests excluding slow ones
uv run pytest -m "not slow" tests/
```

### Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync
   uv run playwright install
   ```

2. **Ensure data is available:**
   The dashboard requires data in `ecommerce_data/` directory. Make sure the following files exist:
   - `orders_dataset.csv`
   - `order_items_dataset.csv`
   - `products_dataset.csv`
   - `customers_dataset.csv`
   - `order_reviews_dataset.csv`
   - `order_payments_dataset.csv`

## Test Configuration

### Fixtures (`conftest.py`)

**Streamlit Server Fixture**
- Automatically starts Streamlit server on port 8502
- Waits for server to be ready before running tests
- Cleans up server process after tests complete

**Browser Fixtures**
- Launches Playwright browser (Chromium by default)
- Creates isolated browser context for each test
- Configures viewport size and browser options

**Helper Fixtures**
- `StreamlitHelpers` class with utility methods
- Methods for interacting with Streamlit components
- Date input helpers, metric extraction, chart validation

### Test Markers

- `@pytest.mark.ui` - UI/browser tests
- `@pytest.mark.slow` - Slow tests (visual regression)
- `@pytest.mark.integration` - Integration tests

## Key Testing Scenarios

### Data Validation
- Verify KPI calculations are correct
- Ensure date filtering works across all components
- Validate chart data consistency with metrics
- Test edge cases (no data, extreme date ranges)

### UI/UX Testing
- Responsive design across screen sizes
- Interactive chart elements
- Loading states and error handling
- Accessibility and visual consistency

### Performance Testing
- Dashboard load times
- Chart rendering performance
- Memory usage during interactions
- Server response under test load

## Troubleshooting

### Common Issues

**Streamlit Server Won't Start**
```bash
# Check if port is already in use
lsof -i :8502

# Kill existing process
kill -9 <PID>

# Or use different port
streamlit run dashboard.py --server.port=8503
```

**Browser Installation Issues**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libgtk-3-0

# Reinstall browsers
uv run playwright install
```

**Test Timeouts**
- Increase timeout values in `conftest.py`
- Check data loading performance
- Verify server resources

### WSL/Linux Issues

The setup includes workarounds for WSL environments:
- Headless browser mode by default
- Extended timeouts for slower systems
- Minimal system dependencies

## Screenshot Management

Visual tests generate screenshots in `tests/screenshots/`:
- `dashboard_baseline.png` - Full dashboard baseline
- `dashboard_mobile.png` - Mobile viewport
- `dashboard_tablet.png` - Tablet viewport
- Individual chart screenshots

### Visual Regression Workflow

1. **Initial setup:** Run visual tests to generate baseline screenshots
2. **Development:** Make UI changes
3. **Validation:** Re-run visual tests to compare against baseline
4. **Update baselines:** If changes are intentional, update baseline images

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: uv sync

- name: Install browsers
  run: uv run playwright install --with-deps

- name: Run tests
  run: python run_tests.py --type fast

- name: Upload screenshots
  uses: actions/upload-artifact@v3
  if: failure()
  with:
    name: test-screenshots
    path: tests/screenshots/
```

## Extending Tests

### Adding New Test Cases

1. **Identify test category** (core, interactions, visual)
2. **Create test method** following naming convention `test_*`
3. **Use appropriate fixtures** (`dashboard_page`, `streamlit_helpers`)
4. **Add markers** for categorization
5. **Update documentation**

### Custom Assertions

The test suite includes custom helper methods for Streamlit-specific validations:
- `get_metric_value()` - Extract KPI values
- `set_date_input()` - Interact with date controls
- `wait_for_charts_to_load()` - Wait for chart rendering
- `check_chart_exists()` - Validate chart presence

## Performance Considerations

- Tests run in headless mode for speed
- Parallel test execution with pytest-xdist (optional)
- Screenshot generation only in visual tests
- Cached data loading where possible

## Best Practices

1. **Test Independence:** Each test should be independent and repeatable
2. **Clear Assertions:** Use descriptive assertion messages
3. **Wait Strategies:** Use explicit waits instead of sleep()
4. **Data Validation:** Verify both UI and underlying data
5. **Error Handling:** Test both success and failure scenarios