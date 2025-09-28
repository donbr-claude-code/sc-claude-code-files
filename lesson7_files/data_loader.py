"""
Data Loading and Processing Module for E-commerce Analysis

This module handles all data loading, cleaning, and preprocessing operations
for the e-commerce datasets.
"""

from typing import Optional, Dict
import warnings
import pandas as pd

warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


class DataLoader:
    """Handles loading and processing of e-commerce datasets."""

    def __init__(self, data_path: str = 'ecommerce_data'):
        """
        Initialize DataLoader with path to data directory.

        Args:
            data_path: Path to directory containing CSV files
        """
        self.data_path = data_path
        self._datasets = {}

    def load_orders(self) -> pd.DataFrame:
        """
        Load and process orders dataset.

        Returns:
            DataFrame with processed order data
        """
        orders = pd.read_csv(f'{self.data_path}/orders_dataset.csv')

        # Convert timestamp columns to datetime
        date_columns = [
            'order_purchase_timestamp',
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]

        for col in date_columns:
            orders[col] = pd.to_datetime(orders[col], errors='coerce')

        # Add year and month columns for easier filtering
        orders['year'] = orders['order_purchase_timestamp'].dt.year
        orders['month'] = orders['order_purchase_timestamp'].dt.month

        self._datasets['orders'] = orders
        return orders

    def load_order_items(self) -> pd.DataFrame:
        """
        Load and process order items dataset.

        Returns:
            DataFrame with processed order items data
        """
        order_items = pd.read_csv(f'{self.data_path}/order_items_dataset.csv')
        order_items['shipping_limit_date'] = pd.to_datetime(
            order_items['shipping_limit_date'],
            errors='coerce'
        )

        self._datasets['order_items'] = order_items
        return order_items

    def load_products(self) -> pd.DataFrame:
        """
        Load and process products dataset.

        Returns:
            DataFrame with processed products data
        """
        products = pd.read_csv(f'{self.data_path}/products_dataset.csv')
        self._datasets['products'] = products
        return products

    def load_customers(self) -> pd.DataFrame:
        """
        Load and process customers dataset.

        Returns:
            DataFrame with processed customers data
        """
        customers = pd.read_csv(f'{self.data_path}/customers_dataset.csv')
        self._datasets['customers'] = customers
        return customers

    def load_reviews(self) -> pd.DataFrame:
        """
        Load and process reviews dataset.

        Returns:
            DataFrame with processed reviews data
        """
        reviews = pd.read_csv(f'{self.data_path}/order_reviews_dataset.csv')
        reviews['review_creation_date'] = pd.to_datetime(
            reviews['review_creation_date'],
            errors='coerce'
        )
        reviews['review_answer_timestamp'] = pd.to_datetime(
            reviews['review_answer_timestamp'],
            errors='coerce'
        )

        self._datasets['reviews'] = reviews
        return reviews

    def load_payments(self) -> pd.DataFrame:
        """
        Load and process payments dataset.

        Returns:
            DataFrame with processed payments data
        """
        payments = pd.read_csv(f'{self.data_path}/order_payments_dataset.csv')
        self._datasets['payments'] = payments
        return payments

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all datasets at once.

        Returns:
            Dictionary containing all loaded datasets
        """
        self.load_orders()
        self.load_order_items()
        self.load_products()
        self.load_customers()
        self.load_reviews()
        self.load_payments()

        return self._datasets

    def create_sales_data(self,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         status_filter: str = 'delivered') -> pd.DataFrame:
        """
        Create merged sales dataset with configurable filters.

        Args:
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
            status_filter: Order status to filter ('delivered', 'all', or specific status)

        Returns:
            DataFrame with merged and filtered sales data
        """
        # Ensure datasets are loaded
        if 'orders' not in self._datasets:
            self.load_orders()
        if 'order_items' not in self._datasets:
            self.load_order_items()

        orders = self._datasets['orders'].copy()
        order_items = self._datasets['order_items'].copy()

        # Merge orders with order items
        sales_data = pd.merge(
            left=order_items[['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']],
            right=orders[['order_id', 'customer_id', 'order_status',
                         'order_purchase_timestamp', 'order_delivered_customer_date',
                         'year', 'month']],
            on='order_id',
            how='left'
        )

        # Apply status filter
        if status_filter != 'all':
            sales_data = sales_data[sales_data['order_status'] == status_filter].copy()

        # Apply date filters
        if start_date:
            start_dt = pd.to_datetime(start_date)
            sales_data = sales_data[sales_data['order_purchase_timestamp'] >= start_dt]

        if end_date:
            end_dt = pd.to_datetime(end_date)
            sales_data = sales_data[sales_data['order_purchase_timestamp'] <= end_dt]

        # Add delivery time calculation for delivered orders
        if status_filter == 'delivered':
            sales_data['order_delivered_customer_date'] = pd.to_datetime(
                sales_data['order_delivered_customer_date']
            )
            sales_data['delivery_days'] = (
                sales_data['order_delivered_customer_date'] -
                sales_data['order_purchase_timestamp']
            ).dt.days

        return sales_data

    def create_sales_with_products(self,
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Create sales data merged with product information.

        Args:
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)

        Returns:
            DataFrame with sales and product data
        """
        sales_data = self.create_sales_data(start_date, end_date)

        if 'products' not in self._datasets:
            self.load_products()

        products = self._datasets['products']

        sales_with_products = pd.merge(
            left=sales_data,
            right=products[['product_id', 'product_category_name']],
            on='product_id',
            how='left'
        )

        return sales_with_products

    def create_sales_with_geography(self,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Create sales data merged with customer geographic information.

        Args:
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)

        Returns:
            DataFrame with sales and geographic data
        """
        sales_data = self.create_sales_data(start_date, end_date)

        if 'customers' not in self._datasets:
            self.load_customers()

        customers = self._datasets['customers']

        sales_with_geography = pd.merge(
            left=sales_data,
            right=customers[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='left'
        )

        return sales_with_geography

    def filter_by_date_range(self,
                            df: pd.DataFrame,
                            date_column: str,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Filter any DataFrame by date range.

        Args:
            df: DataFrame to filter
            date_column: Name of the date column to filter on
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)

        Returns:
            Filtered DataFrame
        """
        df_filtered = df.copy()

        # Ensure date column is datetime
        df_filtered[date_column] = pd.to_datetime(df_filtered[date_column])

        if start_date:
            start_dt = pd.to_datetime(start_date)
            df_filtered = df_filtered[df_filtered[date_column] >= start_dt]

        if end_date:
            end_dt = pd.to_datetime(end_date)
            df_filtered = df_filtered[df_filtered[date_column] <= end_dt]

        return df_filtered

    def get_date_range_info(self, df: pd.DataFrame, date_column: str) -> Dict:
        """
        Get information about the date range in a DataFrame.

        Args:
            df: DataFrame to analyze
            date_column: Name of the date column

        Returns:
            Dictionary with date range information
        """
        dates = pd.to_datetime(df[date_column].dropna())

        return {
            'min_date': dates.min(),
            'max_date': dates.max(),
            'date_range_days': (dates.max() - dates.min()).days,
            'unique_dates': len(dates.dt.date.unique()),
            'unique_months': len(dates.dt.to_period('M').unique()),
            'unique_years': sorted(dates.dt.year.unique().tolist())
        }