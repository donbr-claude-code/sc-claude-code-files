"""
Pytest configuration and fixtures for Streamlit dashboard testing.
"""

import asyncio
import subprocess
import time
from typing import Generator
import pytest
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
import requests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def playwright() -> Generator[Playwright, None, None]:
    """Launch Playwright."""
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="session")
async def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """Launch browser."""
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create browser context."""
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create page."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture(scope="session")
def streamlit_server():
    """Start Streamlit server for testing."""
    # Start streamlit server
    process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "dashboard.py", "--server.port=8502", "--server.headless=true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for server to start
    max_attempts = 30
    for _ in range(max_attempts):
        try:
            response = requests.get("http://localhost:8502", timeout=1)
            if response.status_code == 200:
                break
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            time.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Streamlit server failed to start")

    yield "http://localhost:8502"

    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture
async def dashboard_page(page: Page, streamlit_server: str) -> Page:
    """Navigate to dashboard and wait for it to load."""
    await page.goto(streamlit_server)

    # Wait for dashboard to load - look for the main header
    await page.wait_for_selector("text=E-commerce Analytics Dashboard", timeout=30000)

    # Wait for data to load - look for KPI cards
    await page.wait_for_selector(".metric-card", timeout=15000)

    return page


class StreamlitHelpers:
    """Helper methods for interacting with Streamlit components."""

    @staticmethod
    async def get_metric_value(page: Page, metric_name: str) -> str:
        """Get the value of a specific metric card."""
        metric_card = page.locator(f".metric-card:has(h4:text('{metric_name}'))")
        big_font_element = metric_card.locator(".big-font")
        return await big_font_element.text_content()

    @staticmethod
    async def get_trend_indicator(page: Page, metric_name: str) -> str:
        """Get the trend indicator for a specific metric."""
        metric_card = page.locator(f".metric-card:has(h4:text('{metric_name}'))")
        trend_element = metric_card.locator(".trend-positive, .trend-negative")
        return await trend_element.text_content()

    @staticmethod
    async def set_date_input(page: Page, label: str, date: str) -> None:
        """Set a date input field."""
        # Find the date input by its label
        date_input = page.locator(f"label:has-text('{label}') + div input")
        await date_input.clear()
        await date_input.fill(date)
        await date_input.press("Enter")
        await page.wait_for_timeout(1000)  # Wait for Streamlit to process

    @staticmethod
    async def wait_for_charts_to_load(page: Page) -> None:
        """Wait for all Plotly charts to finish loading."""
        # Wait for plotly graphs to be present
        await page.wait_for_selector(".plotly-graph-div", timeout=10000)

        # Wait a bit more for charts to fully render
        await page.wait_for_timeout(2000)

    @staticmethod
    async def check_chart_exists(page: Page, chart_title: str) -> bool:
        """Check if a chart with given title exists."""
        chart_header = page.locator(f"h4:text('{chart_title}')")
        return await chart_header.is_visible()


@pytest.fixture
def streamlit_helpers():
    """Provide helper methods for Streamlit testing."""
    return StreamlitHelpers