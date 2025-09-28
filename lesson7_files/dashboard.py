"""
E-commerce Dashboard
A professional Streamlit dashboard for e-commerce data analysis
"""

import warnings
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import DataLoader

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .big-font {
        font-size: 2rem !important;
        font-weight: bold;
        color: #1f77b4;
        margin: 0;
    }

    .trend-positive {
        color: #28a745;
        font-weight: bold;
    }

    .trend-negative {
        color: #dc3545;
        font-weight: bold;
    }

    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        height: 400px;
    }

    .bottom-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        text-align: center;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stSelectbox > div > div > select {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and prepare data for the dashboard"""
    loader = DataLoader('ecommerce_data')
    datasets = loader.load_all_datasets()

    # Create comprehensive dataset
    sales_data = loader.create_sales_data(status_filter='delivered')
    sales_with_products = loader.create_sales_with_products()
    sales_with_geography = loader.create_sales_with_geography()

    # Merge with reviews
    sales_with_reviews = pd.merge(
        sales_data,
        datasets['reviews'][['order_id', 'review_score']].drop_duplicates(subset=['order_id']),
        on='order_id',
        how='left'
    )

    return {
        'sales_data': sales_data,
        'sales_with_products': sales_with_products,
        'sales_with_geography': sales_with_geography,
        'sales_with_reviews': sales_with_reviews,
        'datasets': datasets
    }

def format_currency(value):
    """Format currency values with K/M suffixes"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

def format_percentage(value):
    """Format percentage with proper sign and color"""
    if value > 0:
        return f"↗ +{value:.2f}%"
    else:
        return f"↘ {value:.2f}%"

def get_trend_color(value):
    """Get color class for trend indicators"""
    return "trend-positive" if value > 0 else "trend-negative"

def filter_data_by_date(data, start_date, end_date):
    """Filter data by date range"""
    return data[
        (data['order_purchase_timestamp'] >= start_date) &
        (data['order_purchase_timestamp'] <= end_date)
    ]

def calculate_period_comparison(current_data, previous_data, metric_column):
    """Calculate percentage change between periods"""
    if metric_column == 'revenue':
        current_value = current_data['price'].sum()
        previous_value = previous_data['price'].sum()
    elif metric_column == 'orders':
        current_value = current_data['order_id'].nunique()
        previous_value = previous_data['order_id'].nunique()
    elif metric_column == 'aov':
        current_value = current_data.groupby('order_id')['price'].sum().mean()
        previous_value = previous_data.groupby('order_id')['price'].sum().mean()

    if metric_column not in ['revenue', 'orders', 'aov']:
        return 0

    if previous_value == 0:
        return 0

    return ((current_value - previous_value) / previous_value) * 100

def main():
    # Load data
    data = load_data()

    # Header section
    st.markdown("## E-commerce Analytics Dashboard")

    # Date range filter in header
    _, col2, col3 = st.columns([2, 1, 1])

    with col2:
        # Get available date range
        min_date = data['sales_data']['order_purchase_timestamp'].min().date()
        max_date = data['sales_data']['order_purchase_timestamp'].max().date()

        start_date = st.date_input(
            "Start Date",
            value=datetime(2023, 1, 1).date(),
            min_value=min_date,
            max_value=max_date
        )

    with col3:
        end_date = st.date_input(
            "End Date",
            value=datetime(2023, 12, 31).date(),
            min_value=min_date,
            max_value=max_date
        )

    # Convert to datetime for filtering
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)

    # Calculate previous period for comparison
    period_length = (end_datetime - start_datetime).days
    previous_start = start_datetime - timedelta(days=period_length)
    previous_end = start_datetime - timedelta(days=1)

    # Filter data for current and previous periods
    current_data = filter_data_by_date(
        data['sales_with_reviews'], start_datetime, end_datetime
    )
    previous_data = filter_data_by_date(
        data['sales_with_reviews'], previous_start, previous_end
    )

    # KPI Row - 4 cards
    st.markdown("### Key Performance Indicators")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # Total Revenue
    with kpi_col1:
        total_revenue = current_data['price'].sum()
        revenue_trend = calculate_period_comparison(current_data, previous_data, 'revenue')

        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Revenue</h4>
            <div class="big-font">{format_currency(total_revenue)}</div>
            <div class="{get_trend_color(revenue_trend)}">{format_percentage(revenue_trend)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Period Growth
    with kpi_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Period Growth</h4>
            <div class="big-font">{revenue_trend:.1f}%</div>
            <div class="{get_trend_color(revenue_trend)}">{format_percentage(revenue_trend)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Average Order Value
    with kpi_col3:
        avg_order_value = current_data.groupby('order_id')['price'].sum().mean()
        aov_trend = calculate_period_comparison(current_data, previous_data, 'aov')

        st.markdown(f"""
        <div class="metric-card">
            <h4>Average Order Value</h4>
            <div class="big-font">${avg_order_value:.0f}</div>
            <div class="{get_trend_color(aov_trend)}">{format_percentage(aov_trend)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Total Orders
    with kpi_col4:
        total_orders = current_data['order_id'].nunique()
        orders_trend = calculate_period_comparison(current_data, previous_data, 'orders')

        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Orders</h4>
            <div class="big-font">{total_orders:,}</div>
            <div class="{get_trend_color(orders_trend)}">{format_percentage(orders_trend)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Grid - 2x2 layout
    st.markdown("### Analytics Overview")

    chart_col1, chart_col2 = st.columns(2)

    # Revenue Trend Chart
    with chart_col1:
        st.markdown("#### Revenue Trend")

        # Prepare revenue trend data
        current_monthly = current_data.groupby(
            current_data['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        current_monthly['period'] = current_monthly['order_purchase_timestamp'].dt.to_timestamp()

        previous_monthly = previous_data.groupby(
            previous_data['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        previous_monthly['period'] = previous_monthly['order_purchase_timestamp'].dt.to_timestamp()

        # Create revenue trend chart
        fig_revenue = go.Figure()

        if not current_monthly.empty:
            fig_revenue.add_trace(go.Scatter(
                x=current_monthly['period'],
                y=current_monthly['price'],
                mode='lines+markers',
                name='Current Period',
                line={'color': '#1f77b4', 'width': 3},
                marker={'size': 6}
            ))

        if not previous_monthly.empty:
            fig_revenue.add_trace(go.Scatter(
                x=previous_monthly['period'],
                y=previous_monthly['price'],
                mode='lines+markers',
                name='Previous Period',
                line={'color': '#ff7f0e', 'width': 2, 'dash': 'dash'},
                marker={'size': 6}
            ))

        fig_revenue.update_layout(
            showlegend=True,
            height=350,
            margin={'l': 0, 'r': 0, 't': 30, 'b': 0},
            xaxis_title="Period",
            yaxis_title="Revenue",
            xaxis={'showgrid': True},
            yaxis={'showgrid': True, 'tickformat': '$,.0s'}
        )

        st.plotly_chart(fig_revenue, use_container_width=True)

    # Top Categories Chart
    with chart_col2:
        st.markdown("#### Top 10 Product Categories")

        # Filter product data for current period
        current_products = filter_data_by_date(
            data['sales_with_products'], start_datetime, end_datetime
        )

        if (not current_products.empty and
            'product_category_name' in current_products.columns):
            category_revenue = current_products.groupby(
                'product_category_name'
            )['price'].sum().reset_index()
            category_revenue = category_revenue.sort_values(
                'price', ascending=True
            ).tail(10)

            fig_categories = px.bar(
                category_revenue,
                x='price',
                y='product_category_name',
                orientation='h',
                color='price',
                color_continuous_scale='Blues',
                labels={'price': 'Revenue', 'product_category_name': 'Category'}
            )

            fig_categories.update_layout(
                showlegend=False,
                height=350,
                margin={'l': 0, 'r': 0, 't': 30, 'b': 0},
                coloraxis_showscale=False,
                xaxis={'tickformat': '$,.0s'}
            )

            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("Product category data not available for the selected period")

    # Second row of charts
    chart_col3, chart_col4 = st.columns(2)

    # Geographic Revenue Map
    with chart_col3:
        st.markdown("#### Revenue by State")

        # Filter geographic data for current period
        current_geography = filter_data_by_date(
            data['sales_with_geography'], start_datetime, end_datetime
        )

        if (not current_geography.empty and
            'customer_state' in current_geography.columns):
            state_revenue = current_geography.groupby(
                'customer_state'
            )['price'].sum().reset_index()
            state_revenue.columns = ['customer_state', 'revenue']

            fig_map = px.choropleth(
                state_revenue,
                locations='customer_state',
                color='revenue',
                locationmode='USA-states',
                scope='usa',
                color_continuous_scale='Blues',
                labels={'revenue': 'Revenue', 'customer_state': 'State'}
            )

            fig_map.update_layout(
                height=350,
                margin={'l': 0, 'r': 0, 't': 30, 'b': 0},
                geo={'showframe': False, 'showcoastlines': True}
            )

            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Geographic data not available for the selected period")

    # Delivery Time vs Satisfaction
    with chart_col4:
        st.markdown("#### Satisfaction vs Delivery Time")

        if (not current_data.empty and
            'delivery_days' in current_data.columns and
            'review_score' in current_data.columns):
            # Create delivery time buckets
            delivery_data = current_data.dropna(subset=['delivery_days', 'review_score']).copy()

            # Define delivery time buckets
            delivery_data['delivery_bucket'] = pd.cut(
                delivery_data['delivery_days'],
                bins=[0, 3, 7, 14, 30, float('inf')],
                labels=['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days']
            )

            # Calculate average review score by delivery bucket
            delivery_satisfaction = delivery_data.groupby(
                'delivery_bucket'
            )['review_score'].mean().reset_index()

            fig_satisfaction = px.bar(
                delivery_satisfaction,
                x='delivery_bucket',
                y='review_score',
                color='review_score',
                color_continuous_scale='RdYlGn',
                labels={'delivery_bucket': 'Delivery Time', 'review_score': 'Avg Review Score'}
            )

            fig_satisfaction.update_layout(
                showlegend=False,
                height=350,
                margin={'l': 0, 'r': 0, 't': 30, 'b': 0},
                coloraxis_showscale=False,
                yaxis={'range': [1, 5]}
            )

            st.plotly_chart(fig_satisfaction, use_container_width=True)
        else:
            st.info("Delivery and review data not available for the selected period")

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Row - 2 cards
    st.markdown("### Additional Metrics")

    bottom_col1, bottom_col2 = st.columns(2)

    # Average Delivery Time
    with bottom_col1:
        if 'delivery_days' in current_data.columns:
            avg_delivery = current_data['delivery_days'].mean()
            prev_avg_delivery = (previous_data['delivery_days'].mean()
                               if not previous_data.empty else avg_delivery)
            delivery_trend = (((avg_delivery - prev_avg_delivery) / prev_avg_delivery * 100)
                            if prev_avg_delivery != 0 else 0)

            st.markdown(f"""
            <div class="bottom-card">
                <h4>Average Delivery Time</h4>
                <div class="big-font">{avg_delivery:.1f} days</div>
                <div class="{get_trend_color(-delivery_trend)}">{format_percentage(delivery_trend)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <h4>Average Delivery Time</h4>
                <div>Data not available</div>
            </div>
            """, unsafe_allow_html=True)

    # Review Score
    with bottom_col2:
        if 'review_score' in current_data.columns:
            avg_review = current_data['review_score'].mean()
            prev_avg_review = (previous_data['review_score'].mean()
                             if not previous_data.empty else avg_review)
            review_trend = (((avg_review - prev_avg_review) / prev_avg_review * 100)
                          if prev_avg_review != 0 else 0)

            star_rating = "⭐" * int(round(avg_review))

            st.markdown(f"""
            <div class="bottom-card">
                <h4>Average Review Score</h4>
                <div class="big-font">{avg_review:.2f} {star_rating}</div>
                <div class="{get_trend_color(review_trend)}">{format_percentage(review_trend)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <h4>Average Review Score</h4>
                <div>Data not available</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
