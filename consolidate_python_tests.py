#!/usr/bin/env python3
"""
Python Test Consolidation Script

This script consolidates all scattered Python test files into a unified, 
organized structure with proper categorization and comprehensive coverage.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Set
import re

def find_python_test_files(root_dir: Path) -> List[Path]:
    """Find all Python test files in the repository."""
    test_files = []
    
    # Search patterns for test files
    patterns = [
        "**/test_*.py",
        "**/*_test.py", 
        "**/test*.py",
        "**/conftest.py"
    ]
    
    for pattern in patterns:
        test_files.extend(root_dir.rglob(pattern))
    
    # Filter out __pycache__ and other non-test files
    filtered_files = []
    for file_path in test_files:
        if "__pycache__" not in str(file_path) and file_path.suffix == ".py":
            filtered_files.append(file_path)
    
    return filtered_files

def categorize_test_files(test_files: List[Path]) -> Dict[str, List[Path]]:
    """Categorize test files by their type and content."""
    categories = {
        "android": [],
        "gui": [],
        "system": [],
        "integration": [],
        "performance": [],
        "network": [],
        "hardware": [],
        "unit": [],
        "e2e": [],
        "misc": []
    }
    
    for file_path in test_files:
        content = ""
        try:
            content = file_path.read_text().lower()
        except:
            pass
        
        file_name = file_path.name.lower()
        file_content = content.lower()
        
        # Categorize based on filename and content
        if any(keyword in file_name for keyword in ["android", "appium", "espresso"]):
            categories["android"].append(file_path)
        elif any(keyword in file_name for keyword in ["gui", "ui", "visual", "qt", "compose"]):
            categories["gui"].append(file_path)
        elif any(keyword in file_name for keyword in ["system", "environment", "python_system"]):
            categories["system"].append(file_path)
        elif any(keyword in file_name for keyword in ["integration", "multi_device", "device_coordination"]):
            categories["integration"].append(file_path)
        elif any(keyword in file_name for keyword in ["performance", "endurance", "load", "benchmark"]):
            categories["performance"].append(file_path)
        elif any(keyword in file_name for keyword in ["network", "socket", "communication"]):
            categories["network"].append(file_path)
        elif any(keyword in file_name for keyword in ["hardware", "shimmer", "thermal", "camera"]):
            categories["hardware"].append(file_path)
        elif any(keyword in file_name for keyword in ["e2e", "end_to_end", "complete"]):
            categories["e2e"].append(file_path)
        elif any(keyword in file_content for keyword in ["unittest", "pytest", "def test_"]):
            categories["unit"].append(file_path)
        else:
            categories["misc"].append(file_path)
    
    return categories

def create_unified_test_structure(repo_root: Path) -> Path:
    """Create unified test structure directory."""
    unified_tests_dir = repo_root / "tests_unified_consolidated"
    
    # Remove existing directory if it exists
    if unified_tests_dir.exists():
        shutil.rmtree(unified_tests_dir)
    
    # Create structure
    unified_tests_dir.mkdir()
    
    # Create category directories
    categories = [
        "android",
        "gui", 
        "system",
        "integration",
        "performance",
        "network",
        "hardware",
        "unit",
        "e2e",
        "fixtures",
        "utils",
        "config"
    ]
    
    for category in categories:
        (unified_tests_dir / category).mkdir()
    
    return unified_tests_dir

def copy_and_organize_tests(test_files: Dict[str, List[Path]], unified_dir: Path, repo_root: Path):
    """Copy and organize test files into unified structure."""
    
    file_count = 0
    duplicate_names = {}
    
    for category, files in test_files.items():
        if not files:
            continue
            
        category_dir = unified_dir / category
        print(f"\\nProcessing {category} tests ({len(files)} files):")
        
        for file_path in files:
            try:
                # Handle duplicate filenames
                target_name = file_path.name
                if target_name in duplicate_names:
                    duplicate_names[target_name] += 1
                    base_name = file_path.stem
                    extension = file_path.suffix
                    target_name = f"{base_name}_{duplicate_names[target_name]}{extension}"
                else:
                    duplicate_names[target_name] = 1
                
                target_path = category_dir / target_name
                
                # Copy file
                shutil.copy2(file_path, target_path)
                print(f"  ✓ {file_path.name} -> {category}/{target_name}")
                file_count += 1
                
            except Exception as e:
                print(f"  ✗ Failed to copy {file_path.name}: {e}")
    
    return file_count

def create_master_test_runner(unified_dir: Path):
    """Create a master test runner for all consolidated tests."""
    
    runner_content = '''#!/usr/bin/env python3
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
    
    print(f"\\n🧪 Running {category} tests...")
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
    
    print("\\n📊 Test Results Summary:")
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
    
    print(f"\\n📈 Summary: {len(passed_categories)}/{len(categories)} categories passed")
    
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
'''
    
    runner_path = unified_dir / "run_all_tests.py"
    runner_path.write_text(runner_content)
    runner_path.chmod(0o755)  # Make executable
    
    return runner_path

def create_consolidated_readme(unified_dir: Path, stats: Dict):
    """Create comprehensive README for consolidated tests."""
    
    readme_content = f'''# Consolidated Test Suite

This directory contains all Python tests consolidated from across the repository into a unified, organized structure.

## Test Organization

### Test Categories

- **`android/`** - Android app integration and device tests ({stats.get("android", 0)} files)
- **`gui/`** - GUI and user interface tests ({stats.get("gui", 0)} files)
- **`system/`** - System and environment tests ({stats.get("system", 0)} files)
- **`integration/`** - Multi-component integration tests ({stats.get("integration", 0)} files)
- **`performance/`** - Performance, load, and endurance tests ({stats.get("performance", 0)} files)
- **`network/`** - Network communication tests ({stats.get("network", 0)} files)
- **`hardware/`** - Hardware integration tests ({stats.get("hardware", 0)} files)
- **`unit/`** - Unit tests for individual components ({stats.get("unit", 0)} files)
- **`e2e/`** - End-to-end workflow tests ({stats.get("e2e", 0)} files)
- **`fixtures/`** - Test fixtures and utilities ({stats.get("fixtures", 0)} files)
- **`utils/`** - Test utilities and helpers ({stats.get("utils", 0)} files)
- **`config/`** - Test configuration files ({stats.get("config", 0)} files)

### Total: {sum(stats.values())} test files

## Running Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run Specific Category
```bash
python run_all_tests.py --category android
python run_all_tests.py --category gui
python run_all_tests.py --category system
```

### List Available Categories
```bash
python run_all_tests.py --list-categories
```

### Using pytest directly
```bash
# Run all tests
pytest -v

# Run specific category
pytest android/ -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## Test Framework

- **pytest** - Primary testing framework
- **Robolectric** - Android unit testing
- **Appium** - Android UI testing
- **PyQt5 Testing** - GUI testing
- **asyncio** - Async test support
- **Mock/MagicMock** - Test doubles

## Coverage Goals

- **Unit Tests**: 95%+ line coverage
- **Integration Tests**: All component interactions
- **GUI Tests**: All user interaction paths
- **Android Tests**: All activities and workflows
- **Performance Tests**: All critical performance paths

## Test Structure Standards

Each test file should include:
- Comprehensive docstring describing test scope
- Setup and teardown methods
- Edge case and error condition testing
- Performance and resource usage validation
- Clear assertions with descriptive messages

## Continuous Integration

These tests are integrated into the CI/CD pipeline:
- **Fast Lane**: Unit and basic integration tests
- **Nightly**: Full test suite including performance tests
- **Release**: Complete validation including UI and E2E tests

## Contributing

When adding new tests:
1. Place in appropriate category directory
2. Follow existing naming conventions
3. Include comprehensive test coverage
4. Add appropriate fixtures and utilities
5. Update this README if adding new categories
'''
    
    readme_path = unified_dir / "README.md"
    readme_path.write_text(readme_content)
    
    return readme_path

def main():
    """Main consolidation function."""
    
    # Get repository root
    repo_root = Path(__file__).parent
    
    print("🔍 Python Test Consolidation")
    print("=" * 50)
    
    # Find all Python test files
    print("Finding Python test files...")
    test_files = find_python_test_files(repo_root)
    print(f"Found {len(test_files)} Python test files")
    
    # Categorize files
    print("\\nCategorizing test files...")
    categorized_files = categorize_test_files(test_files)
    
    stats = {}
    for category, files in categorized_files.items():
        count = len(files)
        if count > 0:
            print(f"  {category:12}: {count:3} files")
            stats[category] = count
    
    # Create unified structure
    print("\\nCreating unified test structure...")
    unified_dir = create_unified_test_structure(repo_root)
    print(f"Created: {unified_dir}")
    
    # Copy and organize files
    print("\\nCopying and organizing test files...")
    file_count = copy_and_organize_tests(categorized_files, unified_dir, repo_root)
    
    # Create master test runner
    print("\\nCreating master test runner...")
    runner_path = create_master_test_runner(unified_dir)
    print(f"Created: {runner_path}")
    
    # Create README
    print("\\nCreating consolidated README...")
    readme_path = create_consolidated_readme(unified_dir, stats)
    print(f"Created: {readme_path}")
    
    print("\\n✅ Python Test Consolidation Complete!")
    print("=" * 50)
    print(f"📁 Unified directory: {unified_dir}")
    print(f"📊 Total files consolidated: {file_count}")
    print(f"🏷️  Categories: {len([k for k, v in stats.items() if v > 0])}")
    print(f"🧪 Run tests: python {runner_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())