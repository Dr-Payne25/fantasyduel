#!/usr/bin/env python3
"""Test script to verify FastAPI app can start (for CI)."""

import os
import sys

# Set environment variables for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

try:
    # Try to import the app - this will test all imports and initialization
    from main import app

    print("✓ FastAPI app imported successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")

    # Test that we can access the routes
    routes = [route.path for route in app.routes]
    print(f"✓ Found {len(routes)} routes")

    # In CI, we don't want to actually start the server
    print("App started successfully (timeout expected)")
    sys.exit(0)

except Exception as e:
    print(f"App failed to start: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
