#!/usr/bin/env python3
"""Simple test to debug the evaluation suite."""

import asyncio
import sys
from pathlib import Path

# Add the evaluation suite to Python path
sys.path.insert(0, str(Path(__file__).parent))

from evaluation_suite.foundation.pc_tests import CalibrationSystemTest
from evaluation_suite.framework.test_results import TestResult

async def test_simple():
    """Test a single component to see what happens."""
    
    # Create test instance
    test = CalibrationSystemTest(
        name="simple_calibration_test",
        description="Simple test to debug issues"
    )
    
    # Setup test environment
    test_env = {}
    await test.setup(test_env)
    
    # Execute test
    try:
        result = await test.execute(test_env)
        print(f"Test result: {result}")
        print(f"Success: {result.success}")
        print(f"Status: {result.status}")
        if result.error_message:
            print(f"Error: {result.error_message}")
        print(f"Custom metrics: {result.custom_metrics}")
    except Exception as e:
        print(f"Exception during test execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await test.cleanup(test_env)

if __name__ == "__main__":
    asyncio.run(test_simple())