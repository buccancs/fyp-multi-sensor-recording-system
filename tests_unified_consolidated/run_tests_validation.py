#!/usr/bin/env python3
"""
Master Test Runner for Consolidated Test Suite (Validation Mode)

This script validates the consolidated test structure and provides
basic test organization verification.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def list_categories():
    """List available test categories."""
    categories = [d.name for d in Path(__file__).parent.iterdir() if d.is_dir() and not d.name.startswith('.')]
    print("Available test categories:")
    for category in sorted(categories):
        test_files = list((Path(__file__).parent / category).glob("*.py"))
        print(f"  - {category}: {len(test_files)} files")
    return categories

def run_category_tests(category: str, verbose: bool = True):
    """Validate tests for a specific category."""
    category_dir = Path(__file__).parent / category
    if not category_dir.exists():
        print(f"Category directory not found: {category}")
        return False
    
    test_files = list(category_dir.glob("*.py"))
    print(f"\n🧪 Found {len(test_files)} test files in {category}")
    
    if test_files and verbose:
        print("Test files:")
        for test_file in test_files:
            print(f"  - {test_file.name}")
    
    # For validation, just check files exist
    return len(test_files) > 0

def run_all_tests(categories: list = None):
    """Validate all consolidated tests."""
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
    
    print("🚀 Consolidated Test Suite Validation")
    print("=" * 50)
    
    results = {}
    for category in categories:
        if (Path(__file__).parent / category).exists():
            results[category] = run_category_tests(category)
        else:
            results[category] = False
    
    print("\n📊 Test Structure Summary:")
    print("=" * 50)
    
    total_categories = len(categories)
    valid_categories = sum(1 for success in results.values() if success)
    
    for category, valid in results.items():
        status = "✅ VALID" if valid else "❌ MISSING"
        print(f"{category:20} {status}")
    
    print(f"\n📈 Summary: {valid_categories}/{total_categories} categories found")
    
    if valid_categories >= 7:  # Most categories should be present
        print("🎉 Test structure is properly organized!")
        return True
    else:
        missing = [cat for cat, valid in results.items() if not valid]
        print(f"❌ Missing categories: {', '.join(missing)}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate consolidated test suite")
    parser.add_argument("--category", help="Validate specific category only")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    
    args = parser.parse_args()
    
    if args.list_categories:
        list_categories()
        return 0
    
    if args.category:
        success = run_category_tests(args.category)
        return 0 if success else 1
    
    success = run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())