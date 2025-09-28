# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive e-commerce data analysis project with three main components:
1. **Data Analysis** - Jupyter notebooks for exploratory data analysis and business insights
2. **Interactive Dashboard** - Streamlit web application for real-time analytics
3. **Testing Infrastructure** - Playwright-based testing suite for dashboard validation

The project analyzes sales data, customer behavior, and business metrics across multiple e-commerce datasets.

## Development Commands

### Environment Setup

```bash
# Using uv (recommended) - uv manages Python versions and dependencies
uv sync  # Install all dependencies from pyproject.toml

# Install new dependencies
uv add package-name

# Install Playwright browsers (for testing)
uv run playwright install
```

### Running Applications

```bash
# Start Streamlit dashboard
uv run streamlit run dashboard.py

# Start Jupyter server
uv run jupyter notebook

# Run specific Python scripts
uv run python main.py
```

### Testing Commands

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --type core        # Core dashboard tests
python run_tests.py --type interactions # Data filtering tests
python run_tests.py --type visual      # Visual regression tests
python run_tests.py --type fast        # Skip slow visual tests

# Run tests manually with pytest
uv run pytest tests/                   # All tests
uv run pytest tests/test_dashboard_core.py  # Single test file
uv run pytest -v -m "not slow"        # Exclude slow tests
```

## Architecture & Code Structure

### Core Architecture Pattern

The project follows a modular architecture with clear separation of concerns:

**Data Layer (`data_loader.py`)**
- `DataLoader` class handles all CSV loading and preprocessing
- Provides unified interface for accessing multiple datasets
- Handles date parsing, data cleaning, and relationship merging
- Key methods: `load_all_datasets()`, `create_sales_data()`, `create_sales_with_products()`

**Business Logic (`business_metrics.py`)**
- `BusinessMetrics` class encapsulates all metric calculations
- Revenue, order, product, and customer experience metrics
- Time-period aggregations and year-over-year comparisons
- Follows consistent interface pattern for filtering by date ranges

**Presentation Layer**
- `dashboard.py` - Streamlit web application with interactive visualizations
- `EDA_Refactored.ipynb` - Jupyter notebook for deep analysis
- Both consume the same data/business logic modules for consistency

### Data Processing Pipeline

1. **Raw Data** → `DataLoader.load_*()` methods parse CSV files
2. **Cleaned Data** → Date parsing, type conversion, relationship establishment
3. **Merged Datasets** → `create_sales_*()` methods join related tables
4. **Business Metrics** → `BusinessMetrics` class calculates KPIs and aggregations
5. **Visualization** → Dashboard charts and notebook plots render insights

### Key Integration Points

**Dashboard-Business Logic Integration:**
```python
# dashboard.py pattern
data = load_data()  # Uses DataLoader
metrics = BusinessMetrics(data['sales_data'])
revenue = metrics.calculate_total_revenue(start_date, end_date)
```

**Cross-Component Data Flow:**
- `order_id` is the primary key linking orders, items, and reviews
- `customer_id` links orders to customer geography
- `product_id` links items to product categories
- Date filtering is applied consistently across all components

### Testing Architecture

**Test Structure:**
- `tests/conftest.py` - Fixtures for Streamlit server management and browser automation
- `tests/test_dashboard_core.py` - UI component and layout validation
- `tests/test_dashboard_interactions.py` - Data filtering and user interaction tests
- `tests/test_dashboard_visual.py` - Visual regression and chart rendering tests

**Test Strategy:**
- Automated Streamlit server startup/shutdown
- Playwright browser automation for UI testing
- Screenshot-based visual regression testing
- Data consistency validation across date filters

## Data Architecture

### Dataset Relationships

```
orders (order_id) ←→ order_items (order_id, product_id)
orders (order_id) ←→ order_reviews (order_id)
orders (customer_id) ←→ customers (customer_id)
order_items (product_id) ←→ products (product_id)
orders (order_id) ←→ order_payments (order_id)
```

### Critical Data Dependencies

**Dashboard Functionality Requirements:**
- All CSV files must exist in `ecommerce_data/` directory
- Orders must have valid `order_purchase_timestamp` for date filtering
- Price data in order_items enables revenue calculations
- Customer geography enables state-level analysis
- Review scores enable satisfaction metrics

**Date Range Considerations:**
- Dashboard defaults to 2023 data for current period
- Period comparison requires sufficient historical data
- Empty date ranges are handled gracefully with "no data" messages

## Configuration Patterns

### Analysis Configuration
```python
# Notebook configuration pattern
ANALYSIS_CONFIG = {
    'current_year': 2023,
    'previous_year': 2022,
    'start_date': '2023-01-01',
    'end_date': '2023-12-31'
}
```

### Dashboard Date Filtering
```python
# dashboard.py date handling
start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date)
current_data = filter_data_by_date(data, start_datetime, end_datetime)
```

## Development Workflows

### Adding New Metrics
1. Add calculation method to `BusinessMetrics` class
2. Update dashboard to display new metric in appropriate section
3. Add tests to validate metric calculation and display
4. Update notebook analysis if needed

### Extending Dashboard
1. Modify `dashboard.py` layout and add new components
2. Ensure new components use existing data loading patterns
3. Add corresponding tests in appropriate test file
4. Test responsiveness across different viewport sizes

### Testing New Features
1. Add UI tests to `test_dashboard_core.py` for layout changes
2. Add interaction tests to `test_dashboard_interactions.py` for filtering
3. Add visual tests to `test_dashboard_visual.py` for chart changes
4. Update test fixtures if new data requirements emerge

## Important Technical Notes

- Uses Python 3.11 with `uv` for dependency management
- Streamlit dashboard runs on port 8502 during testing (8501 for development)
- Tests require `ecommerce_data/` directory with valid CSV files
- Visual regression tests generate screenshots in `tests/screenshots/`
- All tests are designed to be independent and can run in parallel
