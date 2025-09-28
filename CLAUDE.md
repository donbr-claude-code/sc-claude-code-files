# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains course materials for "Claude Code: A Highly Agentic Coding Assistant" short course. The primary focus is on **Lesson 7** - a complete e-commerce data analysis project with three main components:

1. **E-commerce Data Analysis** (`lesson7_files/`) - Production-ready analytics system
2. **Course Notes & Resources** (`reading_notes/`, `updated_reading_notes/`) - Educational materials
3. **Additional Course Assets** (`additional_files/`) - Supplementary resources

The repository demonstrates real-world data science workflows: from Jupyter notebook exploration to production dashboard deployment with comprehensive testing.

## Architecture Overview

### Lesson 7 Project Structure (`lesson7_files/`)

**Three-Layer Architecture:**
- **Data Layer** (`data_loader.py`) - CSV loading, preprocessing, relationship merging
- **Business Logic** (`business_metrics.py`) - KPI calculations, trend analysis, aggregations
- **Presentation Layer** (`dashboard.py` + `EDA_Refactored.ipynb`) - Streamlit dashboard and Jupyter analysis

**Testing Infrastructure:**
- **Playwright Testing Suite** (`tests/`) - Browser automation for dashboard validation
- **Test Categories** - Core functionality, interactions, visual regression
- **CI-Ready** - Automated server management and cross-browser support

### Data Processing Pipeline

```
Raw CSV Files → DataLoader → Cleaned/Merged Data → BusinessMetrics → Visualizations
     ↓              ↓              ↓                    ↓              ↓
  6 datasets    Type conversion  Sales analysis    KPI calculation  Dashboard/Notebook
```

## Development Commands

### Environment Setup

```bash
# Navigate to lesson7_files for main development
cd lesson7_files/

# Install dependencies using uv (modern Python package manager)
uv sync

# Install browser dependencies for testing
uv run playwright install
```

### Running Applications

```bash
# Start Streamlit dashboard (main application)
uv run streamlit run dashboard.py

# Start Jupyter notebook for data analysis
uv run jupyter notebook

# Run the minimal main.py script
uv run python main.py
```

### Testing Commands

```bash
# Run comprehensive test suite (recommended)
python run_tests.py

# Run specific test categories
python run_tests.py --type core         # Core dashboard functionality
python run_tests.py --type interactions # Data filtering and interactions
python run_tests.py --type visual       # Visual regression testing
python run_tests.py --type fast         # Exclude slow visual tests

# Manual pytest execution
uv run pytest tests/                    # All tests
uv run pytest tests/test_dashboard_core.py  # Single test file
uv run pytest -v -m "not slow"         # Skip slow tests
uv run pytest --verbose                # Detailed output
```

### Code Quality

```bash
# Run linting (if available)
uv run black *.py                      # Code formatting
uv run pylint *.py                     # Code analysis
```

## Key Integration Patterns

### Data Loading Pattern
```python
# Standard data loading across notebook and dashboard
from data_loader import DataLoader

loader = DataLoader('ecommerce_data')
sales_data = loader.create_sales_data(start_date='2023-01-01', end_date='2023-12-31')
```

### Business Metrics Pattern
```python
# Consistent metric calculation interface
from business_metrics import BusinessMetrics

metrics = BusinessMetrics(sales_data)
revenue = metrics.calculate_total_revenue(start_date, end_date)
growth = metrics.calculate_yoy_growth(2023, 2022, 'revenue')
```

### Dashboard-Data Integration
All dashboard components use the same data/business logic modules for consistency:
- Date filtering applied at data layer
- Metrics calculated through BusinessMetrics class
- Charts consume processed DataFrames

## Data Requirements

**Required CSV files in `lesson7_files/ecommerce_data/`:**
- `orders_dataset.csv` - Order transactions and delivery tracking
- `order_items_dataset.csv` - Individual items and pricing details
- `products_dataset.csv` - Product catalog with categories
- `customers_dataset.csv` - Customer geographic information
- `order_reviews_dataset.csv` - Customer reviews and ratings
- `order_payments_dataset.csv` - Payment transaction data

**Data Processing Notes:**
- DataLoader automatically handles date parsing and type conversion
- Only 'delivered' orders are included in analysis
- Geographic data merged for state-level analysis
- All components filter consistently by date ranges

## Testing Architecture

### Test Categories and Markers
- `@pytest.mark.ui` - Browser-based UI tests
- `@pytest.mark.slow` - Visual regression tests (can be skipped)
- `@pytest.mark.integration` - End-to-end dashboard tests

### Testing Infrastructure Features
- **Automatic Server Management** - `run_tests.py` handles Streamlit server lifecycle
- **Browser Automation** - Playwright fixtures with WSL/Linux compatibility
- **Visual Regression** - Screenshot baseline comparison in `tests/screenshots/`
- **Responsive Testing** - Mobile, tablet, desktop viewport validation

### Test Helper Methods
```python
# Common testing patterns in conftest.py
streamlit_helpers.get_metric_value()         # Extract KPI values from dashboard
streamlit_helpers.set_date_input()           # Interact with date controls
streamlit_helpers.wait_for_charts_to_load()  # Wait for chart rendering
streamlit_helpers.check_chart_exists()       # Validate chart presence
```

## Repository Navigation

- **Main Development**: Focus on `lesson7_files/` directory for hands-on work
- **Educational Content**: Reference `reading_notes/` for course context and learning objectives
- **Course Links**: Check `links_to_course_repos.md` for related repositories used in other lessons

## Common Development Workflows

### Adding New Metrics
1. Add calculation method to `business_metrics.py`
2. Update dashboard components in `dashboard.py`
3. Add corresponding tests in appropriate test file
4. Update notebook analysis if relevant

### Dashboard Development
1. Data changes → Update `data_loader.py`
2. Metric changes → Update `business_metrics.py`
3. UI changes → Update `dashboard.py`
4. Always test with `python run_tests.py --type core`

### Testing New Features
1. Run existing tests to ensure no regressions: `python run_tests.py --type fast`
2. Add new test cases following existing patterns
3. Update visual baselines if UI changes: `python run_tests.py --type visual`