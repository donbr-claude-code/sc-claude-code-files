"""
Core dashboard validation tests for the Streamlit e-commerce dashboard.
"""

import pytest
from playwright.async_api import Page
from tests.conftest import StreamlitHelpers


@pytest.mark.ui
class TestDashboardCore:
    """Test core dashboard functionality and layout."""

    async def test_dashboard_loads_successfully(self, dashboard_page: Page):
        """Test that the dashboard loads and displays main elements."""
        # Check main title
        assert await dashboard_page.locator("text=E-commerce Analytics Dashboard").is_visible()

        # Check KPI section header
        assert await dashboard_page.locator("text=Key Performance Indicators").is_visible()

        # Check analytics section header
        assert await dashboard_page.locator("text=Analytics Overview").is_visible()

    async def test_kpi_cards_present(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that all KPI cards are present and display values."""
        expected_metrics = [
            "Total Revenue",
            "Period Growth",
            "Average Order Value",
            "Total Orders"
        ]

        for metric in expected_metrics:
            # Check that metric card exists
            metric_card = dashboard_page.locator(f".metric-card:has(h4:text('{metric}'))")
            assert await metric_card.is_visible(), f"{metric} card should be visible"

            # Check that it has a value
            value = await streamlit_helpers.get_metric_value(dashboard_page, metric)
            assert value is not None and value.strip() != "", f"{metric} should have a value"

    async def test_kpi_values_format(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that KPI values are properly formatted."""
        # Test revenue format (should contain $ and potentially K/M suffix)
        revenue_value = await streamlit_helpers.get_metric_value(dashboard_page, "Total Revenue")
        assert "$" in revenue_value, "Revenue should be formatted as currency"

        # Test AOV format (should be currency without K/M suffix typically)
        aov_value = await streamlit_helpers.get_metric_value(dashboard_page, "Average Order Value")
        assert "$" in aov_value, "AOV should be formatted as currency"

        # Test orders format (should be a number, possibly with commas)
        orders_value = await streamlit_helpers.get_metric_value(dashboard_page, "Total Orders")
        # Remove commas and check if it's numeric
        orders_numeric = orders_value.replace(",", "")
        assert orders_numeric.isdigit(), "Orders should be numeric"

        # Test growth format (should be percentage)
        growth_value = await streamlit_helpers.get_metric_value(dashboard_page, "Period Growth")
        assert "%" in growth_value, "Growth should be formatted as percentage"

    async def test_trend_indicators_present(self, dashboard_page: Page):
        """Test that trend indicators are present and properly styled."""
        trend_elements = dashboard_page.locator(".trend-positive, .trend-negative")
        trend_count = await trend_elements.count()

        # Should have at least some trend indicators
        assert trend_count > 0, "Should have trend indicators"

        # Check that trend indicators contain proper symbols
        for i in range(trend_count):
            trend_text = await trend_elements.nth(i).text_content()
            assert any(symbol in trend_text for symbol in ["↗", "↘", "+", "-"]), \
                f"Trend indicator should contain directional symbols: {trend_text}"

    async def test_date_inputs_present(self, dashboard_page: Page):
        """Test that date input controls are present."""
        # Check for start date input
        start_date_input = dashboard_page.locator("label:has-text('Start Date')")
        assert await start_date_input.is_visible(), "Start date input should be visible"

        # Check for end date input
        end_date_input = dashboard_page.locator("label:has-text('End Date')")
        assert await end_date_input.is_visible(), "End date input should be visible"

    async def test_chart_sections_present(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that all expected chart sections are present."""
        expected_charts = [
            "Revenue Trend",
            "Top 10 Product Categories",
            "Revenue by State",
            "Satisfaction vs Delivery Time"
        ]

        # Wait for charts to load
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        for chart_title in expected_charts:
            chart_exists = await streamlit_helpers.check_chart_exists(dashboard_page, chart_title)
            assert chart_exists, f"Chart '{chart_title}' should be present"

    async def test_plotly_charts_render(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that Plotly charts are properly rendered."""
        # Wait for charts to load
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Check that plotly graphs are present
        plotly_graphs = dashboard_page.locator(".plotly-graph-div")
        graph_count = await plotly_graphs.count()

        # Should have multiple charts (at least 3-4)
        assert graph_count >= 3, f"Should have at least 3 charts, found {graph_count}"

        # Check that graphs have content (not empty)
        for i in range(graph_count):
            graph = plotly_graphs.nth(i)
            # Check if graph has svg content (indicates it rendered)
            svg_content = await graph.locator("svg").count()
            assert svg_content > 0, f"Chart {i} should have SVG content"

    async def test_additional_metrics_section(self, dashboard_page: Page):
        """Test the additional metrics section at the bottom."""
        # Check section header
        assert await dashboard_page.locator("text=Additional Metrics").is_visible()

        # Check for delivery time card
        delivery_card = dashboard_page.locator(".bottom-card:has(h4:text('Average Delivery Time'))")
        assert await delivery_card.is_visible(), "Average delivery time card should be visible"

        # Check for review score card
        review_card = dashboard_page.locator(".bottom-card:has(h4:text('Average Review Score'))")
        assert await review_card.is_visible(), "Average review score card should be visible"

    async def test_responsive_layout(self, dashboard_page: Page):
        """Test that the dashboard maintains proper layout structure."""
        # Check that columns are properly structured
        # KPI row should have 4 columns
        kpi_section = dashboard_page.locator("text=Key Performance Indicators").locator("../following-sibling::div").first

        # Charts section should have proper grid layout
        charts_section = dashboard_page.locator("text=Analytics Overview").locator("../following-sibling::div").first

        # Additional metrics should have 2 columns
        additional_section = dashboard_page.locator("text=Additional Metrics").locator("../following-sibling::div").first

        # These sections should exist and be visible
        assert await kpi_section.is_visible(), "KPI section should be visible"
        assert await charts_section.is_visible(), "Charts section should be visible"
        assert await additional_section.is_visible(), "Additional metrics section should be visible"

    async def test_no_error_messages(self, dashboard_page: Page):
        """Test that no error messages are displayed on the dashboard."""
        # Check for common Streamlit error indicators
        error_elements = dashboard_page.locator(".stAlert, .stException, .stError")
        error_count = await error_elements.count()

        if error_count > 0:
            # If there are errors, print them for debugging
            for i in range(error_count):
                error_text = await error_elements.nth(i).text_content()
                print(f"Error found: {error_text}")

        assert error_count == 0, "Dashboard should not display any error messages"

    async def test_css_styling_applied(self, dashboard_page: Page):
        """Test that custom CSS styling is properly applied."""
        # Check that metric cards have the expected styling class
        metric_cards = dashboard_page.locator(".metric-card")
        metric_count = await metric_cards.count()
        assert metric_count >= 4, "Should have at least 4 metric cards"

        # Check that big-font class is applied
        big_font_elements = dashboard_page.locator(".big-font")
        big_font_count = await big_font_elements.count()
        assert big_font_count >= 4, "Should have big-font styling applied to metrics"

        # Check that trend classes exist
        trend_elements = dashboard_page.locator(".trend-positive, .trend-negative")
        trend_count = await trend_elements.count()
        assert trend_count > 0, "Should have trend styling applied"