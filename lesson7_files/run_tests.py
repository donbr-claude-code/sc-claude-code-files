#!/usr/bin/env python3
"""
Test runner script for Streamlit dashboard testing.

This script provides a convenient way to run different test suites
and manage the testing process.
"""

import argparse
import subprocess
import sys
import time
import requests
from pathlib import Path


def check_streamlit_server(url="http://localhost:8502", timeout=30):
    """Check if Streamlit server is running."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            time.sleep(1)
    return False


def start_streamlit_server():
    """Start Streamlit server in background."""
    print("Starting Streamlit server...")
    process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "dashboard.py", "--server.port=8502", "--server.headless=true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for server to start
    if check_streamlit_server():
        print("✓ Streamlit server started successfully")
        return process
    else:
        process.terminate()
        raise RuntimeError("Failed to start Streamlit server")


def run_tests(test_type="all", verbose=False, browser="chromium"):
    """Run the specified test suite."""
    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")

    # Add browser-specific args if needed
    if browser != "chromium":
        # Note: This would require additional setup for other browsers
        print(f"Note: Browser selection ({browser}) not implemented, using default")

    if test_type == "core":
        cmd.append("tests/test_dashboard_core.py")
    elif test_type == "interactions":
        cmd.append("tests/test_dashboard_interactions.py")
    elif test_type == "visual":
        cmd.append("tests/test_dashboard_visual.py")
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        return False

    print(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run Streamlit dashboard tests")
    parser.add_argument(
        "--type",
        choices=["all", "core", "interactions", "visual", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser to use for testing"
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Don't start Streamlit server (assume it's already running)"
    )

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not Path("dashboard.py").exists():
        print("Error: dashboard.py not found. Please run from the project root.")
        sys.exit(1)

    # Check if server is already running
    server_process = None
    if not args.no_server:
        if check_streamlit_server():
            print("✓ Streamlit server already running")
        else:
            try:
                server_process = start_streamlit_server()
            except RuntimeError as e:
                print(f"Error: {e}")
                sys.exit(1)

    try:
        # Run tests
        success = run_tests(args.type, args.verbose, args.browser)

        if success:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)

    finally:
        # Cleanup
        if server_process:
            print("Stopping Streamlit server...")
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    main()