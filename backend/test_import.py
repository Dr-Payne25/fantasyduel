#!/usr/bin/env python3
"""Test script to verify FastAPI app can be imported successfully."""

try:
    from main import app

    print("✓ FastAPI app imported successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    exit(1)
