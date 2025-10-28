#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API.

This script provides convenient commands to run tests with various options.
"""
import subprocess
import sys
from pathlib import Path


def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=Path(__file__).parent)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False


def run_tests():
    """Run all tests."""
    print("🧪 Running all tests...")
    return run_command("python -m pytest tests/ -v")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    print("📊 Running tests with coverage...")
    return run_command("python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html")


def run_specific_test(test_name):
    """Run a specific test."""
    print(f"🎯 Running specific test: {test_name}")
    return run_command(f"python -m pytest tests/ -v -k {test_name}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [command]")
        print("Commands:")
        print("  test          - Run all tests")
        print("  coverage      - Run tests with coverage")
        print("  specific TEST - Run specific test")
        print("  help          - Show this help")
        return
    
    command = sys.argv[1].lower()
    
    if command == "test":
        success = run_tests()
    elif command == "coverage":
        success = run_tests_with_coverage()
    elif command == "specific" and len(sys.argv) > 2:
        test_name = sys.argv[2]
        success = run_specific_test(test_name)
    elif command == "help":
        main()
        return
    else:
        print(f"Unknown command: {command}")
        main()
        return
    
    if success:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()