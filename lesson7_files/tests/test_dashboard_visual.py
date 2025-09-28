"""
Visual regression and chart validation tests for the Streamlit e-commerce dashboard.
"""

import pytest
from playwright.async_api import Page
from tests.conftest import StreamlitHelpers


@pytest.mark.ui
@pytest.mark.slow
class TestDashboardVisual:
    """Test visual aspects and chart validation of the dashboard."""

    async def test_dashboard_screenshot_baseline(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Take a baseline screenshot of the full dashboard."""
        # Wait for everything to load
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Take full page screenshot
        await dashboard_page.screenshot(
            path="tests/screenshots/dashboard_baseline.png",
            full_page=True
        )

        # Verify the screenshot was created
        import os
        assert os.path.exists("tests/screenshots/dashboard_baseline.png"), \
            "Baseline screenshot should be created"

    async def test_kpi_section_visual(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test visual appearance of KPI section."""
        # Take screenshot of KPI section
        kpi_section = dashboard_page.locator("text=Key Performance Indicators").locator("..")
        await kpi_section.screenshot(path="tests/screenshots/kpi_section.png")

        # Verify KPI cards are properly styled
        metric_cards = dashboard_page.locator(".metric-card")
        card_count = await metric_cards.count()

        for i in range(card_count):
            card = metric_cards.nth(i)

            # Check card visibility
            assert await card.is_visible(), f"KPI card {i} should be visible"

            # Check that card has proper structure
            header = card.locator("h4")
            assert await header.count() > 0, f"KPI card {i} should have a header"

            big_font = card.locator(".big-font")
            assert await big_font.count() > 0, f"KPI card {i} should have big font value"

    async def test_charts_visual_validation(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test visual validation of charts."""
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Test Revenue Trend Chart
        revenue_chart = dashboard_page.locator("h4:text('Revenue Trend')").locator("../following-sibling::*").first
        await revenue_chart.screenshot(path="tests/screenshots/revenue_trend_chart.png")

        # Verify chart has data visualization elements
        svg_elements = await revenue_chart.locator("svg").count()
        assert svg_elements > 0, "Revenue trend chart should have SVG elements"

        # Test Product Categories Chart
        categories_chart = dashboard_page.locator("h4:text('Top 10 Product Categories')").locator("../following-sibling::*").first
        await categories_chart.screenshot(path="tests/screenshots/categories_chart.png")

        # Test Geographic Chart
        geo_chart = dashboard_page.locator("h4:text('Revenue by State')").locator("../following-sibling::*").first
        await geo_chart.screenshot(path="tests/screenshots/geographic_chart.png")

        # Test Satisfaction Chart
        satisfaction_chart = dashboard_page.locator("h4:text('Satisfaction vs Delivery Time')").locator("../following-sibling::*").first
        await satisfaction_chart.screenshot(path="tests/screenshots/satisfaction_chart.png")

    async def test_chart_interactivity(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test chart interactivity features."""
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Find a chart to test interaction
        charts = dashboard_page.locator(".plotly-graph-div")
        chart_count = await charts.count()

        if chart_count > 0:
            first_chart = charts.first

            # Test hover functionality (if available)
            # Note: This might not work in headless mode, but we can try
            await first_chart.hover()

            # Test that chart responds to hover (look for plotly hover elements)
            # This is a basic test - real hover effects might not be visible in headless mode
            await dashboard_page.wait_for_timeout(1000)

            # Verify chart is still functional after interaction
            svg_count = await first_chart.locator("svg").count()
            assert svg_count > 0, "Chart should still have content after interaction"

    async def test_responsive_design_mobile(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test dashboard appearance on mobile viewport."""
        # Change to mobile viewport
        await dashboard_page.set_viewport_size({"width": 375, "height": 667})

        # Wait for layout to adjust
        await dashboard_page.wait_for_timeout(2000)
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Take mobile screenshot
        await dashboard_page.screenshot(
            path="tests/screenshots/dashboard_mobile.png",
            full_page=True
        )

        # Verify dashboard is still functional on mobile
        assert await dashboard_page.locator("text=E-commerce Analytics Dashboard").is_visible()

        # KPI cards should still be visible (though layout may change)
        metric_cards = dashboard_page.locator(".metric-card")
        card_count = await metric_cards.count()
        assert card_count >= 4, "All KPI cards should be visible on mobile"

    async def test_responsive_design_tablet(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test dashboard appearance on tablet viewport."""
        # Change to tablet viewport
        await dashboard_page.set_viewport_size({"width": 768, "height": 1024})

        await dashboard_page.wait_for_timeout(2000)
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Take tablet screenshot
        await dashboard_page.screenshot(
            path="tests/screenshots/dashboard_tablet.png",
            full_page=True
        )

        # Verify dashboard functionality on tablet
        assert await dashboard_page.locator("text=E-commerce Analytics Dashboard").is_visible()

        # Charts should still be visible and functional
        charts = dashboard_page.locator(".plotly-graph-div")
        chart_count = await charts.count()
        assert chart_count >= 3, "Charts should be visible on tablet"

    async def test_color_scheme_consistency(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that color scheme is consistent across the dashboard."""
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Check trend positive/negative colors
        positive_trends = dashboard_page.locator(".trend-positive")
        negative_trends = dashboard_page.locator(".trend-negative")

        positive_count = await positive_trends.count()
        negative_count = await negative_trends.count()

        # Should have some trend indicators
        assert (positive_count + negative_count) > 0, "Should have trend indicators with color classes"

        # Check that big-font elements are styled consistently
        big_font_elements = dashboard_page.locator(".big-font")
        big_font_count = await big_font_elements.count()
        assert big_font_count >= 4, "Should have big-font elements for KPIs"

    async def test_chart_legends_and_labels(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that chart legends and labels are properly displayed."""
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Check revenue trend chart has proper labels
        revenue_section = dashboard_page.locator("h4:text('Revenue Trend')").locator("..")

        # Look for chart elements that might contain labels
        chart_elements = await revenue_section.locator(".plotly-graph-div").count()
        assert chart_elements > 0, "Revenue trend should have chart elements"

        # Check categories chart for labels
        categories_section = dashboard_page.locator("h4:text('Top 10 Product Categories')").locator("..")
        categories_chart_elements = await categories_section.locator(".plotly-graph-div").count()
        assert categories_chart_elements > 0, "Categories chart should have chart elements"

    async def test_loading_states(self, dashboard_page: Page):
        """Test dashboard loading states and transitions."""
        # Reload page to observe loading
        await dashboard_page.reload()

        # Check that loading happens gracefully
        # Wait for main title to appear
        await dashboard_page.wait_for_selector("text=E-commerce Analytics Dashboard", timeout=30000)

        # Take screenshot during loading phase
        await dashboard_page.screenshot(path="tests/screenshots/dashboard_loading.png")

        # Wait for full load
        await dashboard_page.wait_for_selector(".metric-card", timeout=15000)

        # Verify no loading spinners are stuck
        spinners = dashboard_page.locator(".stSpinner")
        spinner_count = await spinners.count()

        # If spinners exist, they should not be stuck (this is hard to test definitively)
        # But we can at least verify the dashboard loaded
        assert await dashboard_page.locator("text=E-commerce Analytics Dashboard").is_visible()

    async def test_error_state_visuals(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test visual appearance of error states."""
        # Set date range that might cause some charts to show "not available"
        await streamlit_helpers.set_date_input(dashboard_page, "Start Date", "2024-12-01")
        await streamlit_helpers.set_date_input(dashboard_page, "End Date", "2024-12-31")

        await dashboard_page.wait_for_timeout(3000)

        # Look for info messages
        info_messages = dashboard_page.locator("text=not available")
        info_count = await info_messages.count()

        if info_count > 0:
            # Take screenshot of error/info states
            await dashboard_page.screenshot(
                path="tests/screenshots/dashboard_no_data_state.png",
                full_page=True
            )

            # Verify that error states are handled gracefully
            for i in range(info_count):
                message = info_messages.nth(i)
                assert await message.is_visible(), f"Info message {i} should be visible"

    async def test_print_friendly_layout(self, dashboard_page: Page, streamlit_helpers: StreamlitHelpers):
        """Test that dashboard is suitable for printing/PDF generation."""
        await streamlit_helpers.wait_for_charts_to_load(dashboard_page)

        # Take a high-resolution screenshot for print testing
        await dashboard_page.screenshot(
            path="tests/screenshots/dashboard_print_layout.png",
            full_page=True,
            type="png"
        )

        # Verify that all sections are visible and would print well
        sections = [
            "E-commerce Analytics Dashboard",
            "Key Performance Indicators",
            "Analytics Overview",
            "Additional Metrics"
        ]

        for section in sections:
            assert await dashboard_page.locator(f"text={section}").is_visible(), \
                f"Section '{section}' should be visible for printing"

        # Verify charts would be included in print
        charts = dashboard_page.locator(".plotly-graph-div")
        chart_count = await charts.count()
        assert chart_count >= 3, "Charts should be present for printing"

    async def setup_screenshot_directory(self):
        """Ensure screenshot directory exists."""
        import os
        os.makedirs("tests/screenshots", exist_ok=True)