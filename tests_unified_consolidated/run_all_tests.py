#!/usr/bin/env python3
"""
Master Test Runner for Consolidated Test Suite

This script runs all consolidated tests with proper categorization,
reporting, and coverage analysis.
"""

import pytest
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_category_tests(category: str, verbose: bool = True):
    """Run tests for a specific category."""
    category_dir = Path(__file__).parent / category
    if not category_dir.exists():
        print(f"Category directory not found: {category}")
        return False
    
    args = [str(category_dir)]
    if verbose:
        args.extend(["-v", "--tb=short"])
    
    print(f"\n🧪 Running {category} tests...")
    result = pytest.main(args)
    return result == 0

def run_all_tests(categories: list = None):
    """Run all consolidated tests."""
    if categories is None:
        categories = [
            "android",
            "gui", 
            "system",
            "integration",
            "performance", 
            "network",
            "hardware",
            "unit",
            "e2e"
        ]
    
    print("🚀 Starting Consolidated Test Suite")
    print("=" * 50)
    
    results = {}
    for category in categories:
        results[category] = run_category_tests(category)
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    passed_categories = []
    failed_categories = []
    
    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{category:20} {status}")
        
        if passed:
            passed_categories.append(category)
        else:
            failed_categories.append(category)
    
    print(f"\n📈 Summary: {len(passed_categories)}/{len(categories)} categories passed")
    
    if failed_categories:
        print(f"❌ Failed categories: {', '.join(failed_categories)}")
        return False
    else:
        print("🎉 All test categories passed!")
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run consolidated test suite")
    parser.add_argument("--category", help="Run specific category only")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    
    args = parser.parse_args()
    
    if args.list_categories:
        categories = [d.name for d in Path(__file__).parent.iterdir() if d.is_dir()]
        print("Available test categories:")
        for category in sorted(categories):
            print(f"  - {category}")
        return 0
    
    if args.category:
        success = run_category_tests(args.category)
        return 0 if success else 1
    
    success = run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
