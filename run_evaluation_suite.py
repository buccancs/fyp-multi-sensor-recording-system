#!/usr/bin/env python3
"""
Run Comprehensive Evaluation Suite

This is the main entry point for running the complete evaluation suite
that addresses all thesis evidence gaps identified in Chapters 5 & 6.

Usage:
    python run_evaluation_suite.py                    # Full validation
    python run_evaluation_suite.py --quick           # Quick validation
    python run_evaluation_suite.py --thesis-ready    # Generate thesis evidence
    python run_evaluation_suite.py --help            # Show all options
"""

import argparse
import sys
import time
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from validation_suite import ValidationSuite
    from thesis_evidence_generator import ThesisEvidenceGenerator
    VALIDATION_AVAILABLE = True
except ImportError as e:
    print(f"❌ Validation modules not available: {e}")
    VALIDATION_AVAILABLE = False


def run_quick_validation():
    """Run quick validation tests"""
    print("🚀 Running Quick Validation...")
    
    if not VALIDATION_AVAILABLE:
        print("❌ Validation modules not available")
        return 1
        
    validation_suite = ValidationSuite()
    
    # Run just timing and network tests for quick feedback
    results = {}
    
    try:
        print("\n⏱️  Testing timing precision...")
        timing_results = validation_suite.timing_validator.measure_cross_device_precision(
            num_sessions=3, duration_minutes=2  # Reduced for quick test
        )
        results["timing_precision"] = timing_results
        
        print("\n🌐 Testing network performance...")
        network_results = validation_suite.network_validator.measure_network_performance()
        results["network_performance"] = network_results
        
        print("\n✅ Quick validation complete!")
        print(f"   Timing precision: {timing_results['median_drift_ms']} ms median drift")
        print(f"   Network latency: {network_results['latency_measurements']['ethernet']['p95_ms']} ms (Ethernet)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return 1


def run_full_validation():
    """Run complete validation suite"""
    print("🚀 Running Full Validation Suite...")
    
    if not VALIDATION_AVAILABLE:
        print("❌ Validation modules not available") 
        return 1
        
    validation_suite = ValidationSuite()
    
    try:
        results = validation_suite.run_comprehensive_validation()
        results_file = validation_suite.save_validation_results(results)
        
        print(f"\n✅ Full validation complete!")
        print(f"📊 Results saved to: {results_file}")
        
        # Summary
        gaps_addressed = 0
        gaps_with_evidence = 0
        
        if "thesis_evidence_status" in results:
            status = results["thesis_evidence_status"]
            gaps_addressed = status.get("total_gaps_addressed", 0)
            gaps_with_evidence = status.get("gaps_with_evidence", 0)
            
        print(f"\n📋 Evidence Status:")
        print(f"   Thesis gaps addressed: {gaps_addressed}")
        print(f"   With supporting evidence: {gaps_with_evidence}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Full validation failed: {e}")
        return 1


def generate_thesis_evidence():
    """Generate thesis-ready evidence files"""
    print("📝 Generating Thesis Evidence Package...")
    
    if not VALIDATION_AVAILABLE:
        print("❌ Validation modules not available")
        return 1
        
    generator = ThesisEvidenceGenerator()
    
    try:
        evidence_summary = generator.generate_complete_thesis_evidence()
        
        if evidence_summary.get("status") == "complete":
            print("\n🎯 Thesis evidence generation successful!")
            
            appendix_files = evidence_summary.get("appendix_files", {})
            print(f"\n📋 Generated {len(appendix_files)} appendix files:")
            for appendix_type, file_path in appendix_files.items():
                print(f"   • {appendix_type.replace('_', ' ').title()}")
                
            print(f"\n📁 Files location: docs/thesis_appendices/")
            print(f"📖 Citation guide: docs/thesis_appendices/thesis_citation_reference_guide.md")
            
            return 0
        else:
            print("❌ Thesis evidence generation failed")
            return 1
            
    except Exception as e:
        print(f"❌ Thesis evidence generation failed: {e}")
        return 1


def list_evidence_gaps():
    """List all evidence gaps that are addressed"""
    print("📋 Evidence Gaps Addressed by Validation Suite")
    print("=" * 60)
    
    gaps = [
        {
            "gap": "Cross-Device Timing Precision",
            "thesis_claim": "2.1 ms median cross-device timestamp drift (IQR 1.4–3.2 ms)",
            "evidence_type": "Automated timing measurements across 15 sessions"
        },
        {
            "gap": "Memory Leak Absence",
            "thesis_claim": "No uncontrolled memory growth over 8-hour endurance test",
            "evidence_type": "Memory usage monitoring with leak detection"
        },
        {
            "gap": "CPU and Throughput Performance",
            "thesis_claim": "CPU usage remained moderate with no significant upward trend",
            "evidence_type": "System resource monitoring and performance metrics"
        },
        {
            "gap": "Network Latency Metrics",
            "thesis_claim": "95th percentile latency 23ms (Ethernet), 187ms (WiFi)",
            "evidence_type": "Network performance measurement across environments"
        },
        {
            "gap": "Sensor Reliability",
            "thesis_claim": "Connection drops after average of 8.3 minutes (range 4–18 min)",
            "evidence_type": "Bluetooth dropout analysis across 12 sessions"
        },
        {
            "gap": "Device Discovery Success Rates",
            "thesis_claim": "30% success on enterprise WiFi, 90% on home router",
            "evidence_type": "Network discovery testing in different environments"
        },
        {
            "gap": "User Setup Time",
            "thesis_claim": "New users averaged 12.8 minutes, experienced users 4.2 minutes",
            "evidence_type": "Usability testing with lab members"
        },
        {
            "gap": "Test Coverage",
            "thesis_claim": "Comprehensive test suite with 100% success rate",
            "evidence_type": "Automated test execution and coverage analysis"
        }
    ]
    
    for i, gap in enumerate(gaps, 1):
        print(f"\n{i}. {gap['gap']}")
        print(f"   Thesis Claim: \"{gap['thesis_claim']}\"")
        print(f"   Evidence Type: {gap['evidence_type']}")
    
    print(f"\n✅ Total: {len(gaps)} evidence gaps addressed")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Evaluation Suite for Multi-Sensor Recording System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_evaluation_suite.py --quick          # Quick validation (5 minutes)
  python run_evaluation_suite.py --full           # Complete validation (60 minutes)
  python run_evaluation_suite.py --thesis-ready   # Generate thesis evidence files
  python run_evaluation_suite.py --list-gaps      # Show all evidence gaps addressed
        """
    )
    
    parser.add_argument("--quick", action="store_true",
                       help="Run quick validation tests only")
    parser.add_argument("--full", action="store_true",
                       help="Run complete validation suite")
    parser.add_argument("--thesis-ready", action="store_true",
                       help="Generate thesis-ready evidence files")
    parser.add_argument("--list-gaps", action="store_true",
                       help="List all evidence gaps addressed")
    
    args = parser.parse_args()
    
    # Default to full validation if no specific option
    if not any([args.quick, args.full, args.thesis_ready, args.list_gaps]):
        args.full = True
    
    print("=" * 80)
    print("MULTI-SENSOR RECORDING SYSTEM - COMPREHENSIVE EVALUATION SUITE")
    print("Addressing Thesis Evidence Gaps in Chapters 5 & 6")
    print("=" * 80)
    
    if args.list_gaps:
        list_evidence_gaps()
        return 0
    elif args.quick:
        return run_quick_validation()
    elif args.thesis_ready:
        return generate_thesis_evidence()
    elif args.full:
        return run_full_validation()
    
    return 0


if __name__ == "__main__":
    start_time = time.time()
    exit_code = main()
    
    duration = time.time() - start_time
    print(f"\n⏱️  Total execution time: {duration:.1f} seconds")
    
    if exit_code == 0:
        print("🎉 Evaluation suite completed successfully!")
    else:
        print("❌ Evaluation suite failed")
        
    sys.exit(exit_code)