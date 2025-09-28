# E-commerce Analytics Dashboard

A professional Streamlit dashboard for comprehensive e-commerce data analysis, featuring revenue trends, product performance, geographic insights, and customer experience metrics.

## Features

### 📊 Dashboard Layout

**Header Section**
- Professional title with global date range filter
- Date range filter applies to all dashboard components

**KPI Cards Row**
- **Total Revenue**: Current period revenue with trend indicator
- **Period Growth**: Revenue growth percentage with trend arrow
- **Average Order Value**: AOV with period-over-period comparison
- **Total Orders**: Order count with growth indicator

**Analytics Grid (2x2)**
- **Revenue Trend**: Line chart comparing current vs previous period
- **Top 10 Categories**: Horizontal bar chart with blue gradient
- **Revenue by State**: Interactive US choropleth map
- **Delivery vs Satisfaction**: Bar chart showing review scores by delivery time buckets

**Bottom Metrics Row**
- **Average Delivery Time**: With trend indicator
- **Review Score**: Average rating with star display and trend

### 🎨 Design Features

- **Professional Styling**: Clean, modern interface with card-based layout
- **Trend Indicators**: Green arrows (↗) for positive trends, red arrows (↘) for negative
- **Uniform Card Heights**: Consistent sizing across each row
- **Interactive Charts**: All visualizations built with Plotly for interactivity
- **Responsive Layout**: Adapts to different screen sizes
- **Currency Formatting**: Displays as $300K, $2M for better readability

## Installation

### Prerequisites
- Python 3.11+ (specified in `.python-version`)
- Virtual environment (recommended)

### Setup with uv (recommended)

```bash
# Install dependencies
uv sync

# Run the dashboard
uv run streamlit run dashboard.py
```

### Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

## Usage

1. **Start the Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Access the Dashboard**
   - Open your browser to `http://localhost:8501`
   - The dashboard will load with default date range (2023 data)

3. **Interactive Features**
   - **Date Range Selection**: Use the date pickers in the header to filter all data
   - **Hover Effects**: Hover over charts to see detailed tooltips
   - **Zoom and Pan**: Use Plotly's built-in zoom and pan features on charts
   - **Geographic Exploration**: Click and explore the choropleth map

## Data Requirements

The dashboard expects the following CSV files in the `ecommerce_data/` directory:

- `orders_dataset.csv` - Order transactions and status
- `order_items_dataset.csv` - Individual items and pricing
- `products_dataset.csv` - Product catalog with categories
- `customers_dataset.csv` - Customer geographic data
- `order_reviews_dataset.csv` - Customer reviews and ratings
- `order_payments_dataset.csv` - Payment transaction data

### Data Processing

The dashboard automatically:
- Merges multiple datasets using order and customer IDs
- Filters for delivered orders only
- Calculates delivery times and review metrics
- Applies date range filters across all visualizations
- Handles missing data gracefully

## Architecture

### File Structure
```
├── dashboard.py           # Main Streamlit application
├── data_loader.py         # Data loading and preprocessing
├── business_metrics.py    # Business metric calculations
├── requirements.txt       # Python dependencies
├── ecommerce_data/       # CSV data files
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   ├── customers_dataset.csv
│   ├── order_reviews_dataset.csv
│   └── order_payments_dataset.csv
└── README.md
```

### Key Components

- **DataLoader**: Handles CSV loading, data merging, and preprocessing
- **BusinessMetrics**: Calculates KPIs, trends, and business analytics
- **Dashboard**: Streamlit UI with responsive layout and interactive charts

## Key Metrics Explained

### KPI Calculations
- **Total Revenue**: Sum of all order item prices in selected period
- **Period Growth**: Percentage change compared to previous period of same length
- **Average Order Value**: Mean total value per order
- **Total Orders**: Count of unique orders in the period

### Trend Indicators
- **Green ↗**: Positive growth (revenue, orders, AOV increase)
- **Red ↘**: Negative growth (metrics decreased vs previous period)
- **Two Decimal Places**: All trend percentages show precise values

### Chart Details
- **Revenue Trend**: Solid line for current period, dashed for previous
- **Top Categories**: Sorted descending by revenue, blue gradient
- **Geographic Map**: Blue gradient with state-level revenue data
- **Delivery Satisfaction**: Delivery time buckets vs average review scores

## Customization

### Modifying Date Ranges
Edit the default date ranges in `dashboard.py`:
```python
start_date = st.date_input(
    "Start Date",
    value=datetime(2023, 1, 1).date(),  # Change default start
)
```

### Styling Updates
Modify the CSS in the `st.markdown()` section for custom styling:
- Card colors and shadows
- Font sizes and weights
- Trend indicator colors

### Adding New Metrics
1. Create calculation functions in `business_metrics.py`
2. Add new cards or charts in `dashboard.py`
3. Follow the existing pattern for data filtering and display

## Troubleshooting

### Common Issues

**Data Loading Errors**
- Ensure all CSV files are in the `ecommerce_data/` directory
- Check file names match exactly (case-sensitive)
- Verify CSV files have the expected column names

**Performance Issues**
- Use date range filters to limit data processing
- Consider adding `@st.cache_data` decorators for expensive operations
- Check data file sizes (large files may need chunking)

**Chart Display Issues**
- Ensure Plotly is properly installed
- Check browser compatibility (modern browsers required)
- Clear Streamlit cache: `streamlit cache clear`

### Error Messages

**"Data not available"**
- Selected date range has no data
- Missing required columns in source files
- Data preprocessing failed

**"Geographic data not available"**
- Customer state information missing
- Geographic merge failed
- Date range filter too restrictive

## Development

### Running in Development Mode
```bash
# Enable debug mode
streamlit run dashboard.py --server.headless=false --logger.level=debug

# Enable auto-reload
streamlit run dashboard.py --server.fileWatcherType=auto
```

### Code Quality
```bash
# Format code
black dashboard.py data_loader.py business_metrics.py

# Check code quality
pylint dashboard.py

# Run tests (if test files exist)
pytest
```

## Performance Optimization

- **Data Caching**: Uses `@st.cache_data` for expensive data loading
- **Efficient Filtering**: Date filters applied at the data level
- **Optimized Charts**: Plotly charts with minimal data processing
- **Responsive Design**: CSS optimized for fast rendering

## Contributing

When contributing to this dashboard:

1. Follow the existing code structure and styling
2. Test with different date ranges and data scenarios
3. Ensure all charts handle empty data gracefully
4. Maintain consistent formatting (currency, percentages)
5. Update this README for any new features

## License

This project is part of an e-commerce data analysis suite. See the main project for licensing information.