#!/usr/bin/env python3
"""Test script to verify FastAPI app can be imported successfully."""

import sys

try:
    from main import app

    print("✓ FastAPI app imported successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    print("✓ All imports successful")
    sys.exit(0)
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
