#!/usr/bin/env python3
"""
Simple evaluation suite runner

Runs basic system validation without complex evidence generation.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from validation_suite import SystemValidator


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    
    print("Running basic system validation...")
    
    validator = SystemValidator()
    results = validator.run_basic_validation()
    results_file = validator.save_results(results)
    
    summary = results['summary']
    print(f"\nValidation complete:")
    print(f"  Tests run: {summary['total_tests']}")
    print(f"  Tests passed: {summary['passed_tests']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")
    print(f"  Results: {results_file}")
    
    return 0 if summary['passed_tests'] > 0 else 1


if __name__ == "__main__":
    exit(main())