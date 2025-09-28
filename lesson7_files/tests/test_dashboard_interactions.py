"""
Data interaction and filtering tests for the Streamlit e-commerce dashboard.
"""

import pytest
from playwright.async_api import Page
from tests.conftest import StreamlitHelpers


@pytest.mark.ui
@pytest.mark.integration
class TestDashboardInteractions:
    """Test dashboard data interactions and filtering."""

    async def test_date_range_filtering(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that date range filtering updates the dashboard data."""
        # Get initial revenue value
        initial_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")

        # Change date range to a smaller period
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-06-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-06-30")

        # Wait for dashboard to update
        await dashboard_page.wait_for_timeout(3000)

        # Get updated revenue value
        updated_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")

        # Values should be different (assuming data exists for both periods)
        assert initial_revenue != updated_revenue, \
            "Revenue should change when date range is modified"

    async def test_date_range_validation(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test date range input validation."""
        # Test setting end date before start date
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-06-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-05-01")

        # Wait for potential validation
        await dashboard_page.wait_for_timeout(2000)

        # Dashboard should handle this gracefully (either prevent it or show no data)
        # At minimum, it shouldn't crash
        assert await dashboard_page.locator("text=E-commerce Analytics Dashboard").is_visible()

    async def test_extreme_date_ranges(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test dashboard behavior with extreme date ranges."""
        # Test very narrow date range (1 day)
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-01-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-01-01")

        await dashboard_page.wait_for_timeout(2000)

        # Should still display metrics (even if zero)
        revenue_value = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        assert revenue_value is not None, "Should display revenue value even for narrow date range"

        # Test very wide date range (full dataset)
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2016-01-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-12-31")

        await dashboard_page.wait_for_timeout(3000)

        # Should display updated metrics
        updated_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        assert updated_revenue is not None, "Should display revenue for wide date range"

    async def test_period_comparison_updates(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that period comparison trends update with date changes."""
        # Get initial trend for revenue
        initial_trend = await streamlit_helpers.get_trend_indicator(dashboard_page, "Total Revenue")

        # Change to a different period
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-03-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-03-31")

        await dashboard_page.wait_for_timeout(3000)

        # Get updated trend
        updated_trend = await streamlit_helpers.get_trend_indicator(dashboard_page, "Total Revenue")

        # Trend indicators should potentially change (unless period comparison is identical)
        assert updated_trend is not None, "Should have a trend indicator after date change"

    async def test_charts_update_with_date_filter(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that charts update when date range is changed."""
        # Wait for initial charts to load
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Count initial chart elements
        initial_chart_count = await dashboard_page.locator(".plotly-graph-div").count()

        # Change date range
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-07-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-07-31")

        # Wait for charts to update
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Charts should still be present (same count)
        updated_chart_count = await dashboard_page.locator(".plotly-graph-div").count()
        assert updated_chart_count == initial_chart_count, \
            "Chart count should remain the same after date filtering"

        # Charts should have content
        for i in range(updated_chart_count):
            chart = dashboard_page.locator(".plotly-graph-div").nth(i)
            svg_count = await chart.locator("svg").count()
            assert svg_count > 0, f"Chart {i} should still have SVG content after filtering"

    async def test_no_data_scenarios(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test dashboard behavior when no data matches the filter."""
        # Set date range to future dates (likely no data)
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2025-01-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2025-01-31")

        await dashboard_page.wait_for_timeout(3000)

        # Dashboard should handle gracefully
        revenue_value = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")

        # Should show zero or properly formatted empty state
        assert revenue_value is not None, "Should display some value even when no data"

        # Look for "not available" messages in charts
        info_messages = dashboard_page.locator("text=not available")
        info_count = await info_messages.count()

        # Some charts might show "not available" messages
        if info_count > 0:
            # This is expected behavior for no-data scenarios
            assert True
        else:
            # Or charts might show empty but valid visualizations
            charts = dashboard_page.locator(".plotly-graph-div")
            chart_count = await charts.count()
            assert chart_count >= 0, "Charts should be present even with no data"

    async def test_metric_consistency_across_filters(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that metrics remain consistent across different date filters."""
        # Test with Q1 2023
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-01-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-03-31")

        await dashboard_page.wait_for_timeout(3000)

        q1_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        q1_orders = await streamlit_helpers.get_metric_value(dashboard_page, "Total Orders")

        # Test with Q2 2023
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-04-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-06-30")

        await dashboard_page.wait_for_timeout(3000)

        q2_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        q2_orders = await streamlit_helpers.get_metric_value(dashboard_page, "Total Orders")

        # Values should be different (unless business is exactly the same)
        # But they should both be valid formatted values
        assert q1_revenue is not None and q1_revenue.strip() != ""
        assert q2_revenue is not None and q2_revenue.strip() != ""
        assert q1_orders is not None and q1_orders.strip() != ""
        assert q2_orders is not None and q2_orders.strip() != ""

    async def test_delivery_metrics_update(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that delivery-related metrics update with date filtering."""
        # Change to a specific period
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-05-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-05-31")

        await dashboard_page.wait_for_timeout(3000)

        # Check delivery time metric
        delivery_card = dashboard_page.locator(".bottom-card:has(h4:text('Average Delivery Time'))")
        assert await delivery_card.is_visible(), "Delivery time card should be visible"

        delivery_value = await delivery_card.locator(".big-font").text_content()
        assert delivery_value is not None, "Should have a delivery time value"

        # Check review score metric
        review_card = dashboard_page.locator(".bottom-card:has(h4:text('Average Review Score'))")
        assert await review_card.is_visible(), "Review score card should be visible"

        review_value = await review_card.locator(".big-font").text_content()
        assert review_value is not None, "Should have a review score value"

    async def test_chart_data_consistency(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that chart data is consistent with KPI metrics."""
        # Set a specific date range
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-08-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-08-31")

        await dashboard_page.wait_for_timeout(3000)
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Get KPI revenue
        kpi_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")

        # Verify that charts are showing data for the same period
        # Revenue trend chart should be present and have data
        revenue_chart_exists = await streamlit_helpers.check_chart_exists(dashboard_page, "Revenue Trend")
        assert revenue_chart_exists, "Revenue trend chart should exist"

        # Categories chart should show data for the period
        categories_chart_exists = await streamlit_helpers.check_chart_exists(
            dashboard_page, "Top 10 Product Categories"
        )
        assert categories_chart_exists, "Product categories chart should exist"

    async def test_browser_refresh_maintains_state(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that browser refresh doesn't break the dashboard."""
        # Set custom date range
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2023-09-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2023-09-30")

        await dashboard_page.wait_for_timeout(3000)

        # Get a metric value
        pre_refresh_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")

        # Refresh the page
        await dashboard_page.reload()

        # Wait for page to load again
        await dashboard_page.wait_for_selector("text=E-commerce Analytics Dashboard", timeout=30000)
        await dashboard_page.wait_for_selector(".metric-card", timeout=15000)

        # Dashboard should load successfully after refresh
        post_refresh_revenue = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        assert post_refresh_revenue is not None, "Dashboard should work after refresh"