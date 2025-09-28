"""
Business Metrics Module for E-commerce Analysis

This module contains all business metric calculations including revenue,
order metrics, product performance, and customer experience analytics.
"""

from typing import Optional, Dict

import pandas as pd
import numpy as np


class BusinessMetrics:
    """Calculates various business metrics for e-commerce data."""

    def __init__(self, sales_data: pd.DataFrame):
        """
        Initialize with sales data.

        Args:
            sales_data: DataFrame containing merged sales data
        """
        self.sales_data = sales_data

    def calculate_total_revenue(self,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> float:
        """
        Calculate total revenue for a given period.

        Args:
            start_date: Start date for calculation (YYYY-MM-DD format)
            end_date: End date for calculation (YYYY-MM-DD format)

        Returns:
            Total revenue in the period
        """
        data = self._filter_by_date(self.sales_data, start_date, end_date)
        return data['price'].sum()

    def calculate_revenue_by_period(self,
                                   period: str = 'month',
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate revenue aggregated by time period.

        Args:
            period: Time period for aggregation ('day', 'week', 'month', 'quarter', 'year')
            start_date: Start date for calculation
            end_date: End date for calculation

        Returns:
            DataFrame with revenue by period
        """
        data = self._filter_by_date(self.sales_data, start_date, end_date)

        # Map period to pandas frequency
        period_map = {
            'day': 'D',
            'week': 'W',
            'month': 'M',
            'quarter': 'Q',
            'year': 'Y'
        }

        freq = period_map.get(period, 'M')

        # Create period column
        data_copy = data.copy()
        data_copy['period'] = data_copy['order_purchase_timestamp'].dt.to_period(freq)

        # Aggregate revenue
        revenue_by_period = data_copy.groupby('period')['price'].agg([
            ('revenue', 'sum'),
            ('order_count', 'count'),
            ('avg_order_value', 'mean')
        ]).reset_index()

        # Convert period to timestamp for easier plotting
        revenue_by_period['period'] = revenue_by_period['period'].dt.to_timestamp()

        return revenue_by_period

    def calculate_yoy_growth(self,
                           current_year: int,
                           previous_year: int,
                           metric: str = 'revenue') -> Dict:
        """
        Calculate year-over-year growth metrics.

        Args:
            current_year: Current year for comparison
            previous_year: Previous year for comparison
            metric: Metric to calculate ('revenue', 'orders', 'avg_order_value')

        Returns:
            Dictionary with YoY metrics
        """
        current_data = self.sales_data[self.sales_data['year'] == current_year]
        previous_data = self.sales_data[self.sales_data['year'] == previous_year]

        if metric == 'revenue':
            current_value = current_data['price'].sum()
            previous_value = previous_data['price'].sum()
        elif metric == 'orders':
            current_value = current_data['order_id'].nunique()
            previous_value = previous_data['order_id'].nunique()
        elif metric == 'avg_order_value':
            current_value = current_data.groupby('order_id')['price'].sum().mean()
            previous_value = previous_data.groupby('order_id')['price'].sum().mean()
        else:
            raise ValueError(f"Unknown metric: {metric}")

        growth_rate = (((current_value - previous_value) / previous_value * 100)
                      if previous_value else 0)

        return {
            'current_year': current_year,
            'previous_year': previous_year,
            'current_value': current_value,
            'previous_value': previous_value,
            'absolute_change': current_value - previous_value,
            'growth_rate': growth_rate,
            'metric': metric
        }

    def calculate_mom_growth(self,
                           year: int,
                           smoothing: bool = False) -> pd.DataFrame:
        """
        Calculate month-over-month growth for a given year.

        Args:
            year: Year to analyze
            smoothing: Apply 3-month moving average if True

        Returns:
            DataFrame with monthly metrics and growth rates
        """
        year_data = self.sales_data[self.sales_data['year'] == year].copy()

        monthly_metrics = year_data.groupby('month').agg({
            'price': 'sum',
            'order_id': 'nunique'
        }).rename(columns={'price': 'revenue', 'order_id': 'order_count'})

        # Calculate MoM growth
        monthly_metrics['revenue_mom_growth'] = monthly_metrics['revenue'].pct_change() * 100
        monthly_metrics['orders_mom_growth'] = monthly_metrics['order_count'].pct_change() * 100

        # Calculate average order value
        monthly_metrics['avg_order_value'] = (
            monthly_metrics['revenue'] / monthly_metrics['order_count']
        )

        if smoothing:
            # Apply 3-month moving average
            monthly_metrics['revenue_ma3'] = monthly_metrics['revenue'].rolling(window=3).mean()
            monthly_metrics['revenue_ma3_growth'] = (
                monthly_metrics['revenue_ma3'].pct_change() * 100
            )

        return monthly_metrics.reset_index()

    def calculate_product_performance(self,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None,
                                     top_n: int = 10) -> pd.DataFrame:
        """
        Calculate product category performance metrics.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            top_n: Number of top categories to return

        Returns:
            DataFrame with product performance metrics
        """
        if 'product_category_name' not in self.sales_data.columns:
            raise ValueError(
                "Product category information not available in sales data"
            )

        data = self._filter_by_date(self.sales_data, start_date, end_date)

        category_metrics = data.groupby('product_category_name').agg({
            'price': ['sum', 'mean', 'count'],
            'order_id': 'nunique',
            'product_id': 'nunique'
        })

        # Flatten column names
        category_metrics.columns = [
            'revenue', 'avg_price', 'items_sold',
            'order_count', 'unique_products'
        ]

        # Calculate additional metrics
        category_metrics['revenue_share'] = (
            category_metrics['revenue'] / category_metrics['revenue'].sum() * 100
        )
        category_metrics['avg_items_per_order'] = (
            category_metrics['items_sold'] / category_metrics['order_count']
        )

        # Sort by revenue and get top N
        category_metrics = category_metrics.sort_values('revenue', ascending=False).head(top_n)

        return category_metrics.reset_index()

    def calculate_geographic_performance(self,
                                        start_date: Optional[str] = None,
                                        end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate sales performance by geographic region.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            DataFrame with geographic performance metrics
        """
        if 'customer_state' not in self.sales_data.columns:
            raise ValueError(
                "Geographic information not available in sales data"
            )

        data = self._filter_by_date(self.sales_data, start_date, end_date)

        state_metrics = data.groupby('customer_state').agg({
            'price': 'sum',
            'order_id': 'nunique',
            'customer_id': 'nunique'
        }).rename(columns={
            'price': 'revenue',
            'order_id': 'order_count',
            'customer_id': 'unique_customers'
        })

        # Calculate additional metrics
        state_metrics['avg_order_value'] = (
            state_metrics['revenue'] / state_metrics['order_count']
        )
        state_metrics['revenue_per_customer'] = (
            state_metrics['revenue'] / state_metrics['unique_customers']
        )
        state_metrics['revenue_share'] = (
            state_metrics['revenue'] / state_metrics['revenue'].sum() * 100
        )

        return state_metrics.sort_values('revenue', ascending=False).reset_index()

    def calculate_delivery_performance(self,
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> Dict:
        """
        Calculate delivery performance metrics.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary with delivery performance metrics
        """
        if 'delivery_days' not in self.sales_data.columns:
            return {
                'error': ('Delivery information not available. '
                         'Ensure data includes delivered orders.')
            }

        data = self._filter_by_date(self.sales_data, start_date, end_date)
        data_with_delivery = data.dropna(subset=['delivery_days'])

        if data_with_delivery.empty:
            return {
                'error': 'No delivery data available for the specified period'
            }

        # Calculate delivery metrics
        metrics = {
            'avg_delivery_days': data_with_delivery['delivery_days'].mean(),
            'median_delivery_days': data_with_delivery['delivery_days'].median(),
            'min_delivery_days': data_with_delivery['delivery_days'].min(),
            'max_delivery_days': data_with_delivery['delivery_days'].max(),
            'std_delivery_days': data_with_delivery['delivery_days'].std(),
            'total_orders_delivered': len(data_with_delivery['order_id'].unique())
        }

        # Delivery time distribution
        delivery_distribution = self._categorize_delivery_speed(data_with_delivery)
        metrics['delivery_distribution'] = delivery_distribution

        # On-time delivery (assuming estimated date exists)
        if 'order_estimated_delivery_date' in data.columns:
            data_copy = data.copy()
            data_copy['on_time'] = (
                data_copy['order_delivered_customer_date'] <=
                data_copy['order_estimated_delivery_date']
            )
            metrics['on_time_rate'] = (
                data_copy['on_time'].mean() * 100
                if not data_copy['on_time'].isna().all() else None
            )

        return metrics

    def calculate_review_metrics(self,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> Dict:
        """
        Calculate customer review metrics.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary with review metrics
        """
        if 'review_score' not in self.sales_data.columns:
            return {'error': 'Review data not available in sales data'}

        data = self._filter_by_date(self.sales_data, start_date, end_date)
        data_with_reviews = data.dropna(subset=['review_score'])

        if data_with_reviews.empty:
            return {'error': 'No review data available for the specified period'}

        # Get unique orders with reviews
        order_reviews = data_with_reviews.drop_duplicates(subset=['order_id'])

        metrics = {
            'avg_review_score': order_reviews['review_score'].mean(),
            'median_review_score': order_reviews['review_score'].median(),
            'total_reviews': len(order_reviews),
            'review_distribution': (
                order_reviews['review_score'].value_counts().sort_index().to_dict()
            ),
            'pct_5_star': (order_reviews['review_score'] == 5).mean() * 100,
            'pct_4_5_star': (order_reviews['review_score'] >= 4).mean() * 100,
            'pct_1_2_star': (order_reviews['review_score'] <= 2).mean() * 100
        }

        # Correlation with delivery time if available
        if 'delivery_days' in data_with_reviews.columns:
            unique_orders = data_with_reviews.drop_duplicates(subset=['order_id'])
            correlation = unique_orders[['delivery_days', 'review_score']].corr().iloc[0, 1]
            metrics['delivery_review_correlation'] = correlation

        return metrics

    def calculate_order_metrics(self,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict:
        """
        Calculate comprehensive order metrics.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary with order metrics
        """
        data = self._filter_by_date(self.sales_data, start_date, end_date)

        # Order-level aggregation
        order_summary = data.groupby('order_id').agg({
            'price': 'sum',
            'order_item_id': 'count',
            'product_id': 'nunique'
        }).rename(columns={
            'price': 'order_value',
            'order_item_id': 'items_count',
            'product_id': 'unique_products'
        })

        metrics = {
            'total_orders': len(order_summary),
            'total_revenue': order_summary['order_value'].sum(),
            'avg_order_value': order_summary['order_value'].mean(),
            'median_order_value': order_summary['order_value'].median(),
            'avg_items_per_order': order_summary['items_count'].mean(),
            'avg_unique_products_per_order': order_summary['unique_products'].mean(),
            'order_value_std': order_summary['order_value'].std(),
            'min_order_value': order_summary['order_value'].min(),
            'max_order_value': order_summary['order_value'].max()
        }

        # Order status distribution if available
        if 'order_status' in data.columns:
            status_dist = data.drop_duplicates(subset=['order_id'])['order_status'].value_counts()
            metrics['order_status_distribution'] = status_dist.to_dict()
            metrics['order_status_percentages'] = (status_dist / status_dist.sum() * 100).to_dict()

        return metrics

    def _filter_by_date(self,
                       data: pd.DataFrame,
                       start_date: Optional[str],
                       end_date: Optional[str]) -> pd.DataFrame:
        """
        Filter DataFrame by date range.

        Args:
            data: DataFrame to filter
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Filtered DataFrame
        """
        filtered_data = data.copy()

        if start_date:
            start_dt = pd.to_datetime(start_date)
            filtered_data = filtered_data[
                filtered_data['order_purchase_timestamp'] >= start_dt
            ]

        if end_date:
            end_dt = pd.to_datetime(end_date)
            filtered_data = filtered_data[
                filtered_data['order_purchase_timestamp'] <= end_dt
            ]

        return filtered_data

    def _categorize_delivery_speed(self, data: pd.DataFrame) -> Dict:
        """
        Categorize delivery times into speed categories.

        Args:
            data: DataFrame with delivery_days column

        Returns:
            Dictionary with delivery speed distribution
        """
        conditions = [
            (data['delivery_days'] <= 3),
            (data['delivery_days'] <= 7),
            (data['delivery_days'] <= 14),
            (data['delivery_days'] > 14)
        ]

        categories = ['1-3 days', '4-7 days', '8-14 days', '15+ days']

        data_copy = data.copy()
        data_copy['delivery_category'] = np.select(conditions, categories, default='Unknown')

        # Get unique orders for distribution
        unique_orders = data_copy.drop_duplicates(subset=['order_id'])
        distribution = unique_orders['delivery_category'].value_counts()

        return {
            'counts': distribution.to_dict(),
            'percentages': (distribution / distribution.sum() * 100).to_dict()
        }
