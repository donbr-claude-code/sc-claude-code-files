# E-commerce Data Analysis

A comprehensive e-commerce analytics project that analyzes sales performance, customer behavior, and business metrics using Python and Jupyter notebooks.

## Project Overview

This project provides tools for analyzing e-commerce data with focus on:
- Revenue analysis and growth trends
- Order performance metrics
- Product category analysis
- Geographic distribution of sales
- Customer experience metrics (delivery times, reviews)

## Files Structure

### Core Analysis Files
- **`EDA_Refactored.ipynb`** - Main analysis notebook with comprehensive business metrics
- **`data_loader.py`** - Data loading and preprocessing utilities
- **`business_metrics.py`** - Business metric calculation functions

### Data Directory
- **`ecommerce_data/`** - Contains CSV datasets:
  - `orders_dataset.csv` - Order transactions and delivery information
  - `order_items_dataset.csv` - Individual items within orders with pricing
  - `products_dataset.csv` - Product catalog with categories
  - `customers_dataset.csv` - Customer information and geography
  - `order_reviews_dataset.csv` - Customer reviews and ratings
  - `order_payments_dataset.csv` - Payment transaction data

### Configuration Files
- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Project configuration for uv
- **`CLAUDE.md`** - Project documentation and development guidelines

## Quick Start

### 1. Environment Setup

Using uv (recommended):
```bash
# Install dependencies
uv sync

# Start Jupyter notebook
uv run jupyter notebook
```

Using pip:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Jupyter notebook
jupyter notebook
```

### 2. Running the Analysis

1. Open `EDA_Refactored.ipynb` in Jupyter
2. Configure analysis parameters in the "Configuration & Setup" section:
   ```python
   ANALYSIS_CONFIG = {
       'current_year': 2023,
       'previous_year': 2022,
       'start_date': '2023-01-01',
       'end_date': '2023-12-31',
       'comparison_start_date': '2022-01-01',
       'comparison_end_date': '2022-12-31'
   }
   ```
3. Run all cells to generate the complete analysis

## Key Features

### Configurable Analysis
- **Flexible Date Ranges**: Analyze any time period by modifying configuration parameters
- **Year-over-Year Comparisons**: Compare performance across different years
- **Custom Filters**: Filter by order status, product categories, or geographic regions

### Business Metrics
- **Revenue Analysis**: Total revenue, growth rates, monthly trends
- **Order Performance**: Order counts, average order value, order status distribution
- **Product Insights**: Top categories, revenue distribution, product performance
- **Geographic Analysis**: Sales by state with interactive maps
- **Customer Experience**: Delivery times, review scores, satisfaction metrics

### Professional Visualizations
- Clean, business-ready charts with proper labels and units
- Interactive maps for geographic analysis
- Consistent color schemes and styling
- Executive summary with key insights

## Understanding the Data

### Key Business Metrics

**Revenue Metrics:**
- Total revenue and year-over-year growth
- Month-over-month trends
- Revenue by product category and geography

**Order Metrics:**
- Total order count and growth
- Average order value trends
- Order status distribution

**Customer Experience:**
- Average delivery time
- Review score distribution
- Correlation between delivery speed and satisfaction

### Data Dictionary

**Orders Dataset:**
- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `order_status`: Current status (delivered, shipped, canceled, etc.)
- `order_purchase_timestamp`: Order placement date/time
- `order_delivered_customer_date`: Actual delivery date

**Order Items Dataset:**
- `order_id`: Links to orders
- `product_id`: Product identifier
- `price`: Item price in USD
- `freight_value`: Shipping cost

**Products Dataset:**
- `product_id`: Product identifier
- `product_category_name`: Product category

**Customers Dataset:**
- `customer_id`: Customer identifier
- `customer_state`: US state
- `customer_city`: City name

## Advanced Usage

### Custom Analysis Periods
```python
# Analyze Q4 2023 performance
ANALYSIS_CONFIG = {
    'start_date': '2023-10-01',
    'end_date': '2023-12-31',
    'comparison_start_date': '2022-10-01',
    'comparison_end_date': '2022-12-31'
}
```

### Using the Modules Independently
```python
from data_loader import DataLoader
from business_metrics import BusinessMetrics

# Load data
loader = DataLoader('ecommerce_data')
sales_data = loader.create_sales_data(
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Calculate metrics
metrics = BusinessMetrics(sales_data)
revenue_growth = metrics.calculate_yoy_growth(2023, 2022, 'revenue')
```

## Troubleshooting

**Common Issues:**

1. **Missing Dependencies**: Run `uv sync` or `pip install -r requirements.txt`
2. **Data Not Found**: Ensure `ecommerce_data/` directory exists with CSV files
3. **Memory Issues**: For large datasets, consider filtering by date ranges
4. **Pandas Warnings**: Warnings are suppressed but can be enabled by modifying the configuration

**Performance Tips:**

- Use date range filters for large datasets
- Limit geographic analysis to top N states/cities
- Cache intermediate results for repeated analysis

## Contributing

When extending the analysis:

1. Follow the existing code structure and naming conventions
2. Add appropriate docstrings to new functions
3. Update this README with new features
4. Test with different date ranges and data subsets

## License

This project is for educational and business analysis purposes.