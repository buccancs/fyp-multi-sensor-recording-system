#!/usr/bin/env python3
"""
Chapter 3 Requirements Unified Test Runner with JSON Logging and Mermaid Visualizations
Executes the consolidated test suite and generates comprehensive results in a single JSON file
with unified Mermaid diagram documentation.
"""

import sys
import os
import time
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path


def capture_test_execution():
    """Execute the unified test suite and capture comprehensive results"""
    
    print("=" * 80)
    print("Chapter 3 Requirements - Unified Test Execution with JSON Logging")
    print("=" * 80)
    
    # Initialize execution metadata
    start_time = datetime.now()
    execution_metadata = {
        "start_time": start_time.isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "working_directory": os.getcwd(),
        "test_file": "test_chapter3_unified.py",
        "diagrams_file": "chapter3_mermaid_diagrams.md"
    }
    
    print(f"🚀 Starting unified test execution at {start_time.strftime('%H:%M:%S')}")
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print()
    
    # Execute the unified test suite
    print("🧪 Executing Chapter 3 unified test suite...")
    test_start = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "test_chapter3_unified.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        test_end = time.time()
        test_duration = test_end - test_start
        
        # Parse test results from output
        stdout_lines = result.stdout.split('\n')
        
        # Extract test execution summary
        tests_run = 0
        tests_failed = 0
        tests_passed = 0
        success_rate = 0.0
        
        for line in stdout_lines:
            if "Tests Run:" in line:
                tests_run = int(line.split(":")[-1].strip())
            elif "Failures:" in line:
                tests_failed = int(line.split(":")[-1].strip())
            elif "Success Rate:" in line:
                success_rate = float(line.split(":")[-1].strip().replace('%', ''))
        
        tests_passed = tests_run - tests_failed
        
        # Determine overall status
        overall_status = "PASSED" if result.returncode == 0 else "FAILED"
        
        # Create comprehensive test execution results
        test_execution_results = {
            "unified_test_suite": {
                "file": "test_chapter3_unified.py",
                "status": overall_status,
                "duration": test_duration,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "success_rate": success_rate,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        }
        
        print(f"✅ Test execution completed in {test_duration:.2f} seconds")
        print(f"📊 Results: {tests_passed}/{tests_run} tests passed ({success_rate:.1f}% success rate)")
        
    except subprocess.TimeoutExpired:
        test_end = time.time()
        test_duration = test_end - test_start
        
        test_execution_results = {
            "unified_test_suite": {
                "file": "test_chapter3_unified.py",
                "status": "TIMEOUT",
                "duration": test_duration,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "success_rate": 0.0,
                "stdout": "",
                "stderr": "Test execution timed out after 120 seconds",
                "returncode": -1
            }
        }
        
        print("❌ Test execution timed out")
        
    except Exception as e:
        test_end = time.time()
        test_duration = test_end - test_start
        
        test_execution_results = {
            "unified_test_suite": {
                "file": "test_chapter3_unified.py",
                "status": "ERROR",
                "duration": test_duration,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "success_rate": 0.0,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
        }
        
        print(f"❌ Test execution error: {e}")
    
    # Complete execution metadata
    end_time = datetime.now()
    execution_metadata.update({
        "end_time": end_time.isoformat(),
        "total_duration": (end_time - start_time).total_seconds()
    })
    
    # Create comprehensive logging events
    logging_events = [
        {
            "timestamp": start_time.isoformat(),
            "level": "INFO",
            "category": "execution_start",
            "message": "Chapter 3 unified test execution started",
            "metadata": {
                "test_file": "test_chapter3_unified.py",
                "diagrams_file": "chapter3_mermaid_diagrams.md"
            }
        },
        {
            "timestamp": datetime.fromtimestamp(test_start).isoformat(),
            "level": "INFO",
            "category": "test_execution",
            "message": "Unified test suite execution started",
            "metadata": {
                "test_framework": "unittest",
                "external_dependencies": "none"
            }
        },
        {
            "timestamp": datetime.fromtimestamp(test_end).isoformat(),
            "level": "INFO" if overall_status == "PASSED" else "ERROR",
            "category": "test_completion",
            "message": f"Unified test suite execution completed with status: {overall_status}",
            "metadata": {
                "duration": test_duration,
                "tests_run": tests_run,
                "success_rate": success_rate
            }
        },
        {
            "timestamp": end_time.isoformat(),
            "level": "INFO",
            "category": "execution_complete",
            "message": "Chapter 3 unified test execution completed",
            "metadata": {
                "total_duration": execution_metadata["total_duration"],
                "files_generated": ["chapter3_unified_results.json", "chapter3_mermaid_diagrams.md"]
            }
        }
    ]
    
    # Create file generation metadata
    file_outputs = {
        "unified_json_results": {
            "filename": "chapter3_unified_results.json",
            "description": "Consolidated JSON file containing all test results, execution metadata, and logging events",
            "size_bytes": 0,  # Will be updated after file creation
            "timestamp": end_time.isoformat()
        },
        "unified_mermaid_diagrams": {
            "filename": "chapter3_mermaid_diagrams.md",
            "description": "Unified Markdown file containing all Mermaid visualizations for test results",
            "size_bytes": os.path.getsize("chapter3_mermaid_diagrams.md") if os.path.exists("chapter3_mermaid_diagrams.md") else 0,
            "timestamp": end_time.isoformat()
        }
    }
    
    # Create analysis and insights
    analysis = {
        "test_coverage": {
            "functional_requirements": ["FR-001", "FR-002", "FR-003", "FR-010", "FR-011", "FR-012"],
            "non_functional_requirements": ["NFR-001", "NFR-002", "NFR-003"],
            "use_cases": ["UC-001", "UC-002", "UC-003"],
            "integration_tests": ["system_integration_comprehensive"]
        },
        "performance_metrics": {
            "execution_rate": tests_run / test_duration if test_duration > 0 else 0,
            "average_test_duration": test_duration / tests_run if tests_run > 0 else 0,
            "framework_efficiency": "high" if success_rate >= 95 else "medium" if success_rate >= 80 else "low"
        },
        "quality_assessment": {
            "test_reliability": "high" if overall_status == "PASSED" else "low",
            "requirements_validation": "complete" if success_rate == 100 else "partial",
            "dependency_status": "minimal - unittest only"
        }
    }
    
    # Compile comprehensive unified results
    unified_results = {
        "execution_metadata": execution_metadata,
        "test_execution": test_execution_results,
        "logging_events": logging_events,
        "file_outputs": file_outputs,
        "analysis": analysis,
        "mermaid_diagrams": {
            "source_file": "chapter3_mermaid_diagrams.md",
            "diagrams_included": [
                "test_execution_timeline",
                "requirements_coverage_map",
                "test_results_distribution",
                "performance_metrics_analysis",
                "test_files_status",
                "requirements_traceability_matrix",
                "test_architecture_overview"
            ]
        }
    }
    
    # Save unified results to JSON
    results_filename = "chapter3_unified_results.json"
    with open(results_filename, 'w') as f:
        json.dump(unified_results, f, indent=2, ensure_ascii=False)
    
    # Update file size in results
    file_size = os.path.getsize(results_filename)
    unified_results["file_outputs"]["unified_json_results"]["size_bytes"] = file_size
    
    # Re-save with updated file size
    with open(results_filename, 'w') as f:
        json.dump(unified_results, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print("📄 UNIFIED RESULTS AND VISUALIZATIONS GENERATED")
    print("=" * 80)
    print(f"📋 JSON Results: {results_filename} ({file_size / 1024:.2f}KB)")
    print(f"📊 Mermaid Diagrams: chapter3_mermaid_diagrams.md")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Total Duration: {execution_metadata['total_duration']:.2f} seconds")
    print()
    
    if overall_status == "PASSED":
        print("🎉 ALL TESTS PASSED! Chapter 3 requirements validation successful.")
    else:
        print("❌ Some tests failed. Check results for details.")
    
    print("=" * 80)
    
    return overall_status == "PASSED"


if __name__ == "__main__":
    """Run Chapter 3 unified test suite with comprehensive logging and visualization"""
    success = capture_test_execution()
    sys.exit(0 if success else 1)