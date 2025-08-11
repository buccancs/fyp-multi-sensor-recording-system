#!/usr/bin/env python3
"""
REAL System Validation Suite - NO FAKE DATA

This suite runs ONLY real system tests with absolutely NO simulation, 
mocking, or fabricated data. All evidence comes from genuine test execution.

STRICT POLICY:
❌ NO FAKE DATA
❌ NO SIMULATION  
❌ NO MOCKING
❌ NO FABRICATED RESULTS
✅ REAL TESTS ONLY
✅ GENUINE SYSTEM BEHAVIOR ONLY
✅ AUTHENTIC DIAGNOSTIC DATA ONLY
"""

import json
import logging
import os
import subprocess
import sys
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import REAL system validator - NO FAKE DATA
from real_system_validation import RealSystemValidator

class ValidationSuite:
    """
    REAL System Validation Suite - NO FAKE DATA
    
    This validates the system using ONLY real tests with absolutely no 
    simulation, mocking, or fabricated data of any kind.
    """
    
    def __init__(self):
        self.setup_logging()
        self.real_validator = RealSystemValidator()
        
    def setup_logging(self):
        """Setup logging for real validation only"""
        log_dir = Path("results/real_validation_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"real_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("REAL VALIDATION SUITE - NO FAKE DATA POLICY")
        
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation using ONLY real system tests"""
        self.logger.info("=" * 80)
        self.logger.info("COMPREHENSIVE REAL SYSTEM VALIDATION")
        self.logger.info("STRICT NO FAKE DATA POLICY")
        self.logger.info("=" * 80)
        
        # Delegate to real system validator
        return self.real_validator.run_real_system_validation()
        
    def save_validation_results(self, results: Dict[str, Any]) -> str:
        """Save real validation results"""
        return self.real_validator.save_validation_results(results)


def main():
    """Main entry point for REAL validation suite"""
    print("=" * 80)
    print("MULTI-SENSOR RECORDING SYSTEM - REAL VALIDATION SUITE")
    print("Using Actual Test Execution - No Fake Data")
    print("=" * 80)
    
    validation_suite = ValidationSuite()
    
    try:
        # Run comprehensive validation with real tests
        results = validation_suite.run_comprehensive_validation()
        
        # Save results
        results_file = validation_suite.save_validation_results(results)
        
        print(f"\n✅ Real validation complete!")
        print(f"📊 Results: {results_file}")
        print(f"📁 Evidence files: results/appendix_evidence/")
        print(f"📝 Logs: results/validation_logs/")
        
        # Display summary
        if "evidence_status" in results:
            status = results["evidence_status"] 
            print(f"\n📋 Evidence Quality:")
            print(f"   Approach: {status.get('validation_approach', 'Unknown')}")
            print(f"   Fake Data Used: {status.get('fake_data_used', 'Unknown')}")
            print(f"   Real Tests Executed: {status.get('real_tests_executed', 'Unknown')}")
            print(f"   Evidence Quality: {status.get('evidence_quality', 'Unknown')}")
            
        # Check if actual tests were successful
        if "actual_test_execution" in results:
            test_data = results["actual_test_execution"]
            if test_data.get("success", False):
                print(f"\n🎉 ACTUAL TESTS PASSED - GENUINE EVIDENCE GENERATED!")
            else:
                print(f"\n⚠️  Some actual tests failed - evidence quality may be limited")
                print(f"    Check test output for details")
            
    except Exception as e:
        print(f"\n❌ Real validation failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())