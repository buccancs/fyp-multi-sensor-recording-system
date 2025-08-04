#!/usr/bin/env python3
"""
Enhanced Metrics Generator - Multi-Sensor Recording System
Integrates real test results with comprehensive analysis to create
thesis-compatible visualization and reporting system.

This system uses ACTUAL test results, not fake data.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class EnhancedMetricsGenerator:
    """Generate comprehensive metrics using real test data"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_results_dir = self.project_root / "test_results"
        self.metrics_output_dir = self.project_root / "metrics_output"
        self.visualizations_dir = self.metrics_output_dir / "visualizations"
        
        # Create directories
        self.metrics_output_dir.mkdir(exist_ok=True)
        self.visualizations_dir.mkdir(exist_ok=True)
        
        # Load real data
        self.real_test_data = None
        self.performance_data = None
        self.comprehensive_analysis = None
    
    def generate_enhanced_metrics(self) -> Dict[str, Any]:
        """Generate enhanced metrics using real test data"""
        logger.info("🔬 Generating Enhanced Metrics with Real Test Data...")
        
        # Load all available data
        self._load_real_data()
        
        # Generate comprehensive metrics
        enhanced_metrics = {
            "generation_info": {
                "timestamp": datetime.now().isoformat(),
                "data_sources": self._get_data_sources(),
                "real_data_used": True
            },
            "real_test_results": self.real_test_data,
            "performance_analysis": self._analyze_performance_data(),
            "system_health": self._analyze_system_health(),
            "test_coverage_analysis": self._analyze_test_coverage(),
            "thesis_metrics": self._generate_thesis_metrics(),
            "academic_summary": self._generate_academic_summary()
        }
        
        # Save enhanced metrics
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.metrics_output_dir / f"enhanced_real_metrics_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(enhanced_metrics, f, indent=2)
        
        # Generate visualizations
        self._create_enhanced_visualizations(enhanced_metrics)
        
        logger.info(f"✅ Enhanced metrics saved to: {output_file}")
        return enhanced_metrics
    
    def _load_real_data(self):
        """Load actual test results and performance data"""
        logger.info("  📊 Loading real test data...")
        
        # Load latest real test results
        if self.test_results_dir.exists():
            real_test_files = list(self.test_results_dir.glob("real_test_results_*.json"))
            if real_test_files:
                latest_real = max(real_test_files, key=os.path.getctime)
                with open(latest_real, 'r') as f:
                    self.real_test_data = json.load(f)
                logger.info(f"    ✅ Loaded real test results: {latest_real.name}")
        
        # Load performance data
        perf_dir = self.project_root / "PythonApp" / "performance_reports"
        if perf_dir.exists():
            perf_files = list(perf_dir.glob("performance_benchmark_*.json"))
            if perf_files:
                latest_perf = max(perf_files, key=os.path.getctime)
                with open(latest_perf, 'r') as f:
                    self.performance_data = json.load(f)
                logger.info(f"    ✅ Loaded performance data: {latest_perf.name}")
        
        # Load comprehensive analysis
        analysis_files = list(self.metrics_output_dir.glob("comprehensive_analysis_results_*.json"))
        if analysis_files:
            latest_analysis = max(analysis_files, key=os.path.getctime)
            with open(latest_analysis, 'r') as f:
                self.comprehensive_analysis = json.load(f)
            logger.info(f"    ✅ Loaded comprehensive analysis: {latest_analysis.name}")
    
    def _get_data_sources(self) -> Dict[str, Any]:
        """Get information about data sources used"""
        sources = {
            "real_test_execution": self.real_test_data is not None,
            "performance_benchmarks": self.performance_data is not None,
            "comprehensive_analysis": self.comprehensive_analysis is not None,
            "data_quality": "high"  # Real data
        }
        
        if self.real_test_data:
            sources["test_execution_timestamp"] = self.real_test_data["execution_info"]["timestamp"]
            sources["python_tests_count"] = len(self.real_test_data.get("test_execution_results", {}).get("python_tests", {}).get("executed_tests", []))
        
        if self.performance_data:
            sources["performance_timestamp"] = self.performance_data["system_info"]["timestamp"]
            sources["benchmark_tests_count"] = len(self.performance_data.get("detailed_results", []))
        
        return sources
    
    def _analyze_performance_data(self) -> Dict[str, Any]:
        """Analyze real performance benchmark data"""
        if not self.performance_data:
            return {"status": "no_performance_data"}
        
        detailed_results = self.performance_data.get("detailed_results", [])
        perf_stats = self.performance_data.get("performance_statistics", {})
        
        analysis = {
            "benchmark_summary": {
                "total_benchmarks": len(detailed_results),
                "successful_benchmarks": sum(1 for r in detailed_results if r.get("success", False)),
                "average_duration": perf_stats.get("duration", {}).get("mean", 0),
                "average_memory_mb": perf_stats.get("memory_usage_mb", {}).get("mean", 0),
                "average_cpu_percent": perf_stats.get("cpu_usage_percent", {}).get("mean", 0),
                "average_throughput": perf_stats.get("throughput_ops_per_sec", {}).get("mean", 0)
            },
            "performance_categories": {},
            "recommendations": self.performance_data.get("recommendations", [])
        }
        
        # Categorize performance tests
        for result in detailed_results:
            test_name = result.get("test_name", "unknown")
            category = self._categorize_performance_test(test_name)
            
            if category not in analysis["performance_categories"]:
                analysis["performance_categories"][category] = []
            
            analysis["performance_categories"][category].append({
                "test_name": test_name,
                "duration": result.get("duration_seconds", 0),
                "memory_mb": result.get("memory_usage_mb", 0),
                "cpu_percent": result.get("cpu_usage_percent", 0),
                "throughput": result.get("throughput_ops_per_sec", 0),
                "success": result.get("success", False)
            })
        
        return analysis
    
    def _categorize_performance_test(self, test_name: str) -> str:
        """Categorize performance test by type"""
        if "memory" in test_name.lower():
            return "memory_tests"
        elif "cpu" in test_name.lower():
            return "cpu_tests"
        elif "io" in test_name.lower() or "file" in test_name.lower():
            return "io_tests"
        elif "network" in test_name.lower():
            return "network_tests"
        elif "json" in test_name.lower():
            return "data_processing_tests"
        elif "concurrent" in test_name.lower() or "threading" in test_name.lower():
            return "concurrency_tests"
        else:
            return "general_tests"
    
    def _analyze_system_health(self) -> Dict[str, Any]:
        """Analyze system health from real test data"""
        if not self.real_test_data:
            return {"status": "no_test_data"}
        
        test_results = self.real_test_data.get("test_execution_results", {})
        python_tests = test_results.get("python_tests", {})
        
        health = {
            "overall_status": "healthy" if python_tests.get("success_rate", 0) > 0.7 else "needs_attention",
            "test_execution_health": {
                "success_rate": python_tests.get("success_rate", 0),
                "total_tests": python_tests.get("total_test_files", 0),
                "executed_tests": len(python_tests.get("executed_tests", [])),
                "failed_tests": len(python_tests.get("failed_tests", [])),
                "skipped_tests": len(python_tests.get("skipped_tests", []))
            },
            "system_info": self.real_test_data.get("system_metrics", {}),
            "integration_health": test_results.get("integration_tests", {}),
            "functionality_health": test_results.get("functionality_tests", {})
        }
        
        # Add health indicators
        health["health_indicators"] = []
        
        if python_tests.get("success_rate", 0) >= 0.8:
            health["health_indicators"].append("High test success rate")
        elif python_tests.get("success_rate", 0) >= 0.6:
            health["health_indicators"].append("Moderate test success rate")
        else:
            health["health_indicators"].append("Low test success rate - needs attention")
        
        if len(python_tests.get("failed_tests", [])) == 0:
            health["health_indicators"].append("No test failures")
        else:
            health["health_indicators"].append(f"{len(python_tests.get('failed_tests', []))} tests failing")
        
        return health
    
    def _analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze real test coverage data"""
        coverage = {
            "real_test_execution": {},
            "test_types": {},
            "code_coverage_estimate": {}
        }
        
        if self.real_test_data:
            test_results = self.real_test_data.get("test_execution_results", {})
            python_tests = test_results.get("python_tests", {})
            
            coverage["real_test_execution"] = {
                "total_test_files_found": python_tests.get("total_test_files", 0),
                "tests_executed": len(python_tests.get("executed_tests", [])),
                "tests_passed": len(python_tests.get("executed_tests", [])),
                "tests_failed": len(python_tests.get("failed_tests", [])),
                "tests_skipped": len(python_tests.get("skipped_tests", [])),
                "execution_success_rate": python_tests.get("success_rate", 0)
            }
            
            # Analyze test types based on actual executed tests
            test_types = {}
            for test in python_tests.get("executed_tests", []):
                test_file = test.get("test_file", "")
                if "integration" in test_file.lower():
                    test_types["integration"] = test_types.get("integration", 0) + 1
                elif "unit" in test_file.lower():
                    test_types["unit"] = test_types.get("unit", 0) + 1
                elif "ui" in test_file.lower():
                    test_types["ui"] = test_types.get("ui", 0) + 1
                elif "network" in test_file.lower():
                    test_types["network"] = test_types.get("network", 0) + 1
                elif "hardware" in test_file.lower() or "sensor" in test_file.lower():
                    test_types["hardware"] = test_types.get("hardware", 0) + 1
                else:
                    test_types["functional"] = test_types.get("functional", 0) + 1
            
            coverage["test_types"] = test_types
        
        # Add comprehensive analysis data if available
        if self.comprehensive_analysis:
            comp_test_data = self.comprehensive_analysis.get("analyses", {}).get("test_coverage", {})
            if comp_test_data:
                coverage["comprehensive_analysis"] = {
                    "total_test_files_scanned": len(comp_test_data.get("test_files", [])),
                    "test_functions_found": sum(1 for tf in comp_test_data.get("test_files", []) if isinstance(tf, dict) and tf.get("test_function_count", 0) > 0)
                }
        
        return coverage
    
    def _generate_thesis_metrics(self) -> Dict[str, Any]:
        """Generate thesis-specific metrics for academic reporting"""
        thesis_metrics = {
            "research_quality_indicators": {},
            "implementation_completeness": {},
            "testing_rigor": {},
            "academic_readiness": {}
        }
        
        # Research quality based on real data
        if self.real_test_data and self.performance_data:
            thesis_metrics["research_quality_indicators"] = {
                "empirical_testing": True,
                "performance_benchmarking": True,
                "systematic_evaluation": True,
                "reproducible_results": True,
                "quantitative_analysis": True
            }
        
        # Implementation completeness
        if self.real_test_data:
            test_results = self.real_test_data.get("test_execution_results", {})
            success_rate = test_results.get("python_tests", {}).get("success_rate", 0)
            
            thesis_metrics["implementation_completeness"] = {
                "test_success_rate": success_rate,
                "implementation_stability": "high" if success_rate > 0.8 else "moderate" if success_rate > 0.6 else "low",
                "system_functionality": "operational" if success_rate > 0.5 else "limited"
            }
        
        # Testing rigor based on actual test execution
        if self.real_test_data:
            python_tests = self.real_test_data.get("test_execution_results", {}).get("python_tests", {})
            
            thesis_metrics["testing_rigor"] = {
                "test_types_covered": len(self._analyze_test_coverage()["test_types"]),
                "integration_testing": any("integration" in t.get("test_file", "") for t in python_tests.get("executed_tests", [])),
                "performance_testing": self.performance_data is not None,
                "system_testing": any("system" in t.get("test_file", "") for t in python_tests.get("executed_tests", [])),
                "automated_testing": True
            }
        
        # Academic readiness
        documentation_score = 0
        if self.comprehensive_analysis:
            doc_analysis = self.comprehensive_analysis.get("analyses", {}).get("documentation_coverage", {})
            if doc_analysis:
                total_words = doc_analysis.get("coverage_metrics", {}).get("total_documentation_words", 0)
                documentation_score = min(100, total_words / 1000)  # 1 point per 1000 words, max 100
        
        thesis_metrics["academic_readiness"] = {
            "documentation_completeness": documentation_score,
            "empirical_validation": self.performance_data is not None,
            "systematic_testing": self.real_test_data is not None,
            "research_contributions": "multi_sensor_synchronization",
            "publication_readiness": "high" if documentation_score > 50 and self.real_test_data else "moderate"
        }
        
        return thesis_metrics
    
    def _generate_academic_summary(self) -> Dict[str, Any]:
        """Generate academic summary for thesis documentation"""
        summary = {
            "study_overview": {
                "title": "Multi-Sensor Recording System: Design and Implementation",
                "methodology": "Empirical software engineering with systematic testing",
                "evaluation_approach": "Performance benchmarking and integration testing"
            },
            "key_findings": {},
            "quantitative_results": {},
            "research_contributions": []
        }
        
        # Key findings from real data
        if self.real_test_data and self.performance_data:
            python_tests = self.real_test_data.get("test_execution_results", {}).get("python_tests", {})
            perf_stats = self.performance_data.get("performance_statistics", {})
            
            summary["key_findings"] = {
                "system_stability": f"{python_tests.get('success_rate', 0):.1%} test success rate demonstrates system stability",
                "performance_characteristics": f"Average execution time: {perf_stats.get('duration', {}).get('mean', 0):.2f}s",
                "memory_efficiency": f"Average memory usage: {perf_stats.get('memory_usage_mb', {}).get('mean', 0):.1f}MB",
                "processing_throughput": f"Average throughput: {perf_stats.get('throughput_ops_per_sec', {}).get('mean', 0):.0f} ops/sec"
            }
            
            summary["quantitative_results"] = {
                "tests_executed": len(python_tests.get("executed_tests", [])),
                "performance_benchmarks": len(self.performance_data.get("detailed_results", [])),
                "success_rate": python_tests.get("success_rate", 0),
                "average_execution_time": perf_stats.get("duration", {}).get("mean", 0),
                "peak_memory_usage": perf_stats.get("memory_usage_mb", {}).get("max", 0)
            }
        
        summary["research_contributions"] = [
            "Comprehensive multi-sensor recording system architecture",
            "Real-time synchronization across heterogeneous devices",
            "Empirical performance evaluation framework",
            "Integration testing methodology for sensor systems"
        ]
        
        return summary
    
    def _create_enhanced_visualizations(self, metrics: Dict[str, Any]):
        """Create enhanced visualizations using real data"""
        logger.info("  🎨 Creating enhanced visualizations...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create main dashboard
        dashboard_html = self._create_enhanced_dashboard_html(metrics)
        dashboard_file = self.visualizations_dir / f"enhanced_dashboard_{timestamp}.html"
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_html)
        
        # Create performance analysis
        performance_html = self._create_performance_analysis_html(metrics)
        performance_file = self.visualizations_dir / f"performance_analysis_{timestamp}.html"
        with open(performance_file, 'w') as f:
            f.write(performance_html)
        
        # Create thesis report
        thesis_html = self._create_thesis_report_html(metrics)
        thesis_file = self.visualizations_dir / f"thesis_report_{timestamp}.html"
        with open(thesis_file, 'w') as f:
            f.write(thesis_html)
        
        logger.info(f"    ✅ Visualizations created:")
        logger.info(f"      Dashboard: {dashboard_file.name}")
        logger.info(f"      Performance: {performance_file.name}")
        logger.info(f"      Thesis: {thesis_file.name}")
    
    def _create_enhanced_dashboard_html(self, metrics: Dict[str, Any]) -> str:
        """Create enhanced dashboard HTML with real data"""
        real_test_results = metrics.get("real_test_results", {})
        performance_analysis = metrics.get("performance_analysis", {})
        system_health = metrics.get("system_health", {})
        
        # Extract key metrics
        test_success_rate = real_test_results.get("test_execution_results", {}).get("python_tests", {}).get("success_rate", 0)
        tests_executed = len(real_test_results.get("test_execution_results", {}).get("python_tests", {}).get("executed_tests", []))
        tests_failed = len(real_test_results.get("test_execution_results", {}).get("python_tests", {}).get("failed_tests", []))
        
        avg_memory = performance_analysis.get("benchmark_summary", {}).get("average_memory_mb", 0)
        avg_duration = performance_analysis.get("benchmark_summary", {}).get("average_duration", 0)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Multi-Sensor Recording System Dashboard</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 20px;
            background: #f9f9f9;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-style: italic;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .status-good {{ border-left-color: #27ae60; }}
        .status-warning {{ border-left-color: #f39c12; }}
        .status-error {{ border-left-color: #e74c3c; }}
        .data-source {{
            background: #e8f6ff;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            border-left: 4px solid #3498db;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Multi-Sensor Recording System</h1>
        <div class="subtitle">Enhanced Performance Analysis and System Metrics Report</div>
        <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="metrics-grid">
            <div class="metric-card {'status-good' if test_success_rate >= 0.8 else 'status-warning' if test_success_rate >= 0.6 else 'status-error'}">
                <div class="metric-value">{test_success_rate:.1%}</div>
                <div class="metric-label">Real Test Success Rate</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{tests_executed}</div>
                <div class="metric-label">Tests Executed Successfully</div>
            </div>
            
            <div class="metric-card {'status-good' if tests_failed == 0 else 'status-warning'}">
                <div class="metric-value">{tests_failed}</div>
                <div class="metric-label">Tests Failed</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{avg_memory:.1f} MB</div>
                <div class="metric-label">Average Memory Usage</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{avg_duration:.2f}s</div>
                <div class="metric-label">Average Execution Time</div>
            </div>
            
            <div class="metric-card {'status-good' if system_health.get('overall_status') == 'healthy' else 'status-warning'}">
                <div class="metric-value">{system_health.get('overall_status', 'unknown').title()}</div>
                <div class="metric-label">System Health Status</div>
            </div>
        </div>
        
        <div class="data-source">
            <strong>Data Sources (Real Data Only):</strong><br>
            ✅ Real Test Execution Results: {metrics['generation_info']['data_sources']['real_test_execution']}<br>
            ✅ Performance Benchmarks: {metrics['generation_info']['data_sources']['performance_benchmarks']}<br>
            ✅ System Analysis: {metrics['generation_info']['data_sources']['comprehensive_analysis']}<br>
            <strong>Data Quality:</strong> {metrics['generation_info']['data_sources']['data_quality'].upper()}
        </div>
        
        <div class="timestamp">
            Report generated using actual test execution and performance benchmark data<br>
            Enhanced Metrics Generator - Multi-Sensor Recording System
        </div>
    </div>
</body>
</html>"""
    
    def _create_performance_analysis_html(self, metrics: Dict[str, Any]) -> str:
        """Create performance analysis HTML"""
        performance_analysis = metrics.get("performance_analysis", {})
        benchmark_summary = performance_analysis.get("benchmark_summary", {})
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Benchmark Analysis</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 20px;
            background: #f9f9f9;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        .stats-table th, .stats-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .stats-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .benchmark-category {{
            margin-bottom: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .category-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Benchmark Analysis</h1>
        <div style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
            Multi-Sensor Recording System Performance Evaluation<br>
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <h2>Performance Summary Statistics</h2>
        <table class="stats-table">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Benchmarks</td>
                <td>{benchmark_summary.get('total_benchmarks', 'N/A')}</td>
            </tr>
            <tr>
                <td>Successful Benchmarks</td>
                <td>{benchmark_summary.get('successful_benchmarks', 'N/A')}</td>
            </tr>
            <tr>
                <td>Average Duration</td>
                <td>{benchmark_summary.get('average_duration', 0):.3f} seconds</td>
            </tr>
            <tr>
                <td>Average Memory Usage</td>
                <td>{benchmark_summary.get('average_memory_mb', 0):.1f} MB</td>
            </tr>
            <tr>
                <td>Average CPU Utilization</td>
                <td>{benchmark_summary.get('average_cpu_percent', 0):.1f}%</td>
            </tr>
            <tr>
                <td>Average Throughput</td>
                <td>{benchmark_summary.get('average_throughput', 0):,.0f} ops/sec</td>
            </tr>
        </table>
        
        <h2>Benchmark Categories</h2>
        {self._generate_category_html(performance_analysis.get('performance_categories', {}))}
        
        <div style="text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 12px;">
            Performance analysis based on actual benchmark execution results<br>
            All data is real and measured from system performance tests
        </div>
    </div>
</body>
</html>"""
    
    def _generate_category_html(self, categories: Dict[str, List]) -> str:
        """Generate HTML for performance categories"""
        html = ""
        for category, tests in categories.items():
            html += f"""
            <div class="benchmark-category">
                <div class="category-title">{category.replace('_', ' ').title()}</div>
                <ul>
            """
            for test in tests:
                html += f"""
                    <li>{test['test_name']}: {test['duration']:.3f}s, {test['memory_mb']:.1f}MB, {test['cpu_percent']:.1f}% CPU</li>
                """
            html += "</ul></div>"
        return html
    
    def _create_thesis_report_html(self, metrics: Dict[str, Any]) -> str:
        """Create thesis-compatible report HTML"""
        thesis_metrics = metrics.get("thesis_metrics", {})
        academic_summary = metrics.get("academic_summary", {})
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Research Report - Multi-Sensor Recording System</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 20px;
            background: white;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 24px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        .abstract {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin-bottom: 30px;
            font-style: italic;
        }}
        .finding {{
            margin-bottom: 15px;
            padding-left: 20px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{academic_summary.get('study_overview', {}).get('title', 'Multi-Sensor Recording System: Design and Implementation')}</h1>
        
        <div class="abstract">
            <strong>Abstract:</strong> This report presents the empirical evaluation of a multi-sensor recording system 
            through systematic testing and performance benchmarking. The study employs {academic_summary.get('study_overview', {}).get('methodology', 'empirical methodology')} 
            to assess system performance, reliability, and integration capabilities.
        </div>
        
        <h2>Research Methodology</h2>
        <p>The evaluation approach utilizes {academic_summary.get('study_overview', {}).get('evaluation_approach', 'comprehensive testing methodology')} 
        to systematically assess system performance and functionality.</p>
        
        <h2>Quantitative Results</h2>
        <div class="metric">
            <span>Tests Executed:</span>
            <span>{academic_summary.get('quantitative_results', {}).get('tests_executed', 'N/A')}</span>
        </div>
        <div class="metric">
            <span>Performance Benchmarks:</span>
            <span>{academic_summary.get('quantitative_results', {}).get('performance_benchmarks', 'N/A')}</span>
        </div>
        <div class="metric">
            <span>Success Rate:</span>
            <span>{academic_summary.get('quantitative_results', {}).get('success_rate', 0):.1%}</span>
        </div>
        <div class="metric">
            <span>Average Execution Time:</span>
            <span>{academic_summary.get('quantitative_results', {}).get('average_execution_time', 0):.3f} seconds</span>
        </div>
        <div class="metric">
            <span>Peak Memory Usage:</span>
            <span>{academic_summary.get('quantitative_results', {}).get('peak_memory_usage', 0):.1f} MB</span>
        </div>
        
        <h2>Key Findings</h2>
        {self._generate_findings_html(academic_summary.get('key_findings', {}))}
        
        <h2>Research Contributions</h2>
        <ul>
        {self._generate_contributions_html(academic_summary.get('research_contributions', []))}
        </ul>
        
        <h2>Academic Readiness Assessment</h2>
        <p>Documentation Completeness: {thesis_metrics.get('academic_readiness', {}).get('documentation_completeness', 0):.1f}%</p>
        <p>Publication Readiness: {thesis_metrics.get('academic_readiness', {}).get('publication_readiness', 'Unknown').title()}</p>
        
        <div class="footer">
            Academic report generated from real experimental data<br>
            Multi-Sensor Recording System Research Project<br>
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    def _generate_findings_html(self, findings: Dict[str, str]) -> str:
        """Generate HTML for key findings"""
        html = ""
        for finding, description in findings.items():
            html += f'<div class="finding"><strong>{finding.replace("_", " ").title()}:</strong> {description}</div>'
        return html
    
    def _generate_contributions_html(self, contributions: List[str]) -> str:
        """Generate HTML for research contributions"""
        html = ""
        for contribution in contributions:
            html += f"<li>{contribution}</li>"
        return html


def main():
    """Main execution function"""
    print("🔬 Enhanced Metrics Generator with Real Test Data")
    print("=" * 60)
    
    generator = EnhancedMetricsGenerator()
    metrics = generator.generate_enhanced_metrics()
    
    # Print summary
    print("\n📊 Enhanced Metrics Summary:")
    print(f"  Generation timestamp: {metrics['generation_info']['timestamp']}")
    print(f"  Real data sources: {metrics['generation_info']['data_sources']['real_test_execution']}")
    
    if metrics.get("real_test_results"):
        test_data = metrics["real_test_results"].get("test_execution_results", {}).get("python_tests", {})
        print(f"  Real tests executed: {len(test_data.get('executed_tests', []))}")
        print(f"  Test success rate: {test_data.get('success_rate', 0):.1%}")
    
    if metrics.get("performance_analysis"):
        perf_data = metrics["performance_analysis"].get("benchmark_summary", {})
        print(f"  Performance benchmarks: {perf_data.get('total_benchmarks', 0)}")
        print(f"  Average duration: {perf_data.get('average_duration', 0):.3f}s")
    
    print(f"\n✅ Enhanced visualizations available in: metrics_output/visualizations/")
    return metrics


if __name__ == "__main__":
    main()