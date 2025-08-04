#!/usr/bin/env python3
"""
Comprehensive Metrics Generation System - Multi-Sensor Recording System

This script orchestrates the generation of all metrics, reports, and benchmarks
for the multi-sensor recording system including:
- Performance benchmarks
- Test result summaries
- Validation reports
- Security assessments
- System analytics

Author: Multi-Sensor Recording System Team
Date: 2025-01-04
Version: 1.0
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('metrics_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class MetricsOrchestrator:
    """Orchestrates generation of all system metrics and reports"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.python_app_dir = self.project_root / "PythonApp"
        self.metrics_output_dir = self.project_root / "metrics_output"
        self.metrics_output_dir.mkdir(exist_ok=True)
        
        self.execution_start_time = datetime.now()
        self.results = {
            "execution_info": {
                "start_time": self.execution_start_time.isoformat(),
                "project_root": str(self.project_root),
                "metrics_output_dir": str(self.metrics_output_dir)
            },
            "metrics_generated": {},
            "errors": [],
            "summary": {}
        }
        
    async def generate_all_metrics(self) -> Dict[str, Any]:
        """Generate all metrics, reports, and benchmarks"""
        logger.info("="*80)
        logger.info("COMPREHENSIVE METRICS GENERATION - Multi-Sensor Recording System")
        logger.info("="*80)
        logger.info(f"Project Root: {self.project_root}")
        logger.info(f"Output Directory: {self.metrics_output_dir}")
        logger.info("="*80)
        
        try:
            # 1. Performance Benchmarks
            await self._generate_performance_benchmarks()
            
            # 2. Test Result Summaries
            await self._generate_test_summaries()
            
            # 3. Run Test Suites and Collect Metrics
            await self._run_test_suites()
            
            # 4. Generate Validation Reports
            await self._generate_validation_reports()
            
            # 5. Generate Security Reports
            await self._generate_security_reports()
            
            # 6. System Analytics
            await self._generate_system_analytics()
            
            # 7. Create Consolidated Dashboard
            await self._create_consolidated_dashboard()
            
            # Finalize results
            self._finalize_execution()
            
        except Exception as e:
            logger.error(f"Critical error in metrics generation: {e}")
            self.results["errors"].append({
                "type": "critical_error",
                "message": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            })
            
        return self.results
    
    async def _generate_performance_benchmarks(self):
        """Generate performance benchmarks"""
        logger.info("🔍 Generating Performance Benchmarks...")
        
        try:
            benchmark_script = self.python_app_dir / "src" / "production" / "performance_benchmark.py"
            
            if benchmark_script.exists():
                logger.info(f"  Running performance benchmark: {benchmark_script}")
                
                # Run the performance benchmark
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(benchmark_script),
                    cwd=str(self.python_app_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info("  ✅ Performance benchmarks completed successfully")
                    
                    # Look for generated reports
                    perf_reports_dir = self.python_app_dir / "performance_reports"
                    if perf_reports_dir.exists():
                        report_files = list(perf_reports_dir.glob("*.json"))
                        self.results["metrics_generated"]["performance_benchmarks"] = {
                            "status": "success",
                            "output_files": [str(f) for f in report_files],
                            "stdout": stdout.decode() if stdout else "",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.results["metrics_generated"]["performance_benchmarks"] = {
                            "status": "success",
                            "output_files": [],
                            "stdout": stdout.decode() if stdout else "",
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    logger.error(f"  ❌ Performance benchmarks failed: {stderr.decode()}")
                    self.results["errors"].append({
                        "type": "performance_benchmark_error",
                        "message": stderr.decode() if stderr else "Unknown error",
                        "stdout": stdout.decode() if stdout else "",
                        "return_code": process.returncode
                    })
            else:
                logger.warning(f"  ⚠️  Performance benchmark script not found: {benchmark_script}")
                self.results["errors"].append({
                    "type": "missing_script",
                    "message": f"Performance benchmark script not found: {benchmark_script}"
                })
                
        except Exception as e:
            logger.error(f"  ❌ Error generating performance benchmarks: {e}")
            self.results["errors"].append({
                "type": "performance_benchmark_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    async def _generate_test_summaries(self):
        """Generate comprehensive test summaries"""
        logger.info("🔍 Generating Test Summaries...")
        
        try:
            # Run comprehensive test summary
            summary_script = self.project_root / "comprehensive_test_summary.py"
            
            if summary_script.exists():
                logger.info(f"  Running comprehensive test summary: {summary_script}")
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(summary_script),
                    cwd=str(self.project_root),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info("  ✅ Comprehensive test summary completed")
                    self.results["metrics_generated"]["comprehensive_test_summary"] = {
                        "status": "success",
                        "stdout": stdout.decode() if stdout else "",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"  ❌ Comprehensive test summary failed: {stderr.decode()}")
                    self.results["errors"].append({
                        "type": "test_summary_error",
                        "message": stderr.decode() if stderr else "Unknown error",
                        "return_code": process.returncode
                    })
            
            # Run final summary creation
            final_summary_script = self.project_root / "create_final_summary.py"
            
            if final_summary_script.exists():
                logger.info(f"  Running final summary creation: {final_summary_script}")
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(final_summary_script),
                    cwd=str(self.project_root),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info("  ✅ Final summary creation completed")
                    self.results["metrics_generated"]["final_summary"] = {
                        "status": "success",
                        "stdout": stdout.decode() if stdout else "",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"  ❌ Final summary creation failed: {stderr.decode()}")
                    self.results["errors"].append({
                        "type": "final_summary_error",
                        "message": stderr.decode() if stderr else "Unknown error",
                        "return_code": process.returncode
                    })
                    
        except Exception as e:
            logger.error(f"  ❌ Error generating test summaries: {e}")
            self.results["errors"].append({
                "type": "test_summary_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    async def _run_test_suites(self):
        """Run available test suites and collect metrics"""
        logger.info("🔍 Running Test Suites and Collecting Metrics...")
        
        test_runners = [
            ("complete_test_suite", "run_complete_test_suite.py"),
            ("comprehensive_tests", "run_comprehensive_tests.py"),
            ("quick_recording_session", "run_quick_recording_session_test.py")
        ]
        
        for test_name, script_name in test_runners:
            try:
                script_path = self.python_app_dir / script_name
                
                if script_path.exists():
                    logger.info(f"  Running {test_name}: {script_name}")
                    
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, str(script_path),
                        cwd=str(self.python_app_dir),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        logger.info(f"    ✅ {test_name} completed successfully")
                        self.results["metrics_generated"][f"test_suite_{test_name}"] = {
                            "status": "success",
                            "stdout": stdout.decode() if stdout else "",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        logger.warning(f"    ⚠️  {test_name} completed with warnings/errors")
                        self.results["metrics_generated"][f"test_suite_{test_name}"] = {
                            "status": "completed_with_errors",
                            "stdout": stdout.decode() if stdout else "",
                            "stderr": stderr.decode() if stderr else "",
                            "return_code": process.returncode,
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    logger.warning(f"    ⚠️  Test script not found: {script_name}")
                    self.results["errors"].append({
                        "type": "missing_test_script",
                        "message": f"Test script not found: {script_name}"
                    })
                    
            except Exception as e:
                logger.error(f"    ❌ Error running {test_name}: {e}")
                self.results["errors"].append({
                    "type": "test_suite_exception",
                    "test_name": test_name,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                })
    
    async def _generate_validation_reports(self):
        """Generate validation reports"""
        logger.info("🔍 Generating Validation Reports...")
        
        try:
            # Run Phase 4 validator
            validator_script = self.python_app_dir / "src" / "production" / "phase4_validator.py"
            
            if validator_script.exists():
                logger.info(f"  Running Phase 4 validator: {validator_script}")
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(validator_script),
                    cwd=str(self.python_app_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                # Phase 4 validator might "fail" because features aren't implemented yet
                # but we still want to collect the report
                logger.info(f"  ✅ Phase 4 validation completed (exit code: {process.returncode})")
                self.results["metrics_generated"]["phase4_validation"] = {
                    "status": "completed",
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "return_code": process.returncode,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Look for generated validation reports
                validation_reports = list(self.python_app_dir.glob("phase4_validation_report_*.json"))
                if validation_reports:
                    self.results["metrics_generated"]["phase4_validation"]["report_files"] = [str(f) for f in validation_reports]
                    
            else:
                logger.warning(f"  ⚠️  Phase 4 validator script not found: {validator_script}")
                self.results["errors"].append({
                    "type": "missing_validator_script",
                    "message": f"Phase 4 validator script not found: {validator_script}"
                })
                
        except Exception as e:
            logger.error(f"  ❌ Error generating validation reports: {e}")
            self.results["errors"].append({
                "type": "validation_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    async def _generate_security_reports(self):
        """Generate security assessment reports"""
        logger.info("🔍 Generating Security Reports...")
        
        try:
            # Run security scanner
            security_script = self.python_app_dir / "src" / "production" / "security_scanner.py"
            
            if security_script.exists():
                logger.info(f"  Running security scanner: {security_script}")
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(security_script),
                    cwd=str(self.python_app_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                logger.info(f"  ✅ Security scan completed (exit code: {process.returncode})")
                self.results["metrics_generated"]["security_scan"] = {
                    "status": "completed",
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "return_code": process.returncode,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Look for generated security reports
                security_reports_dir = self.python_app_dir / "security_reports"
                if security_reports_dir.exists():
                    security_reports = list(security_reports_dir.glob("*.json"))
                    self.results["metrics_generated"]["security_scan"]["report_files"] = [str(f) for f in security_reports]
                    
            else:
                logger.warning(f"  ⚠️  Security scanner script not found: {security_script}")
                self.results["errors"].append({
                    "type": "missing_security_script",
                    "message": f"Security scanner script not found: {security_script}"
                })
                
        except Exception as e:
            logger.error(f"  ❌ Error generating security reports: {e}")
            self.results["errors"].append({
                "type": "security_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    async def _generate_system_analytics(self):
        """Generate system analytics and metrics"""
        logger.info("🔍 Generating System Analytics...")
        
        try:
            # Collect system information
            import platform
            import psutil
            
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free
                }
            }
            
            # Analyze project structure
            project_stats = self._analyze_project_structure()
            
            self.results["metrics_generated"]["system_analytics"] = {
                "status": "success",
                "system_info": system_info,
                "project_stats": project_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("  ✅ System analytics generated successfully")
            
        except Exception as e:
            logger.error(f"  ❌ Error generating system analytics: {e}")
            self.results["errors"].append({
                "type": "system_analytics_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure and generate statistics"""
        stats = {
            "total_files": 0,
            "file_types": {},
            "directories": [],
            "large_files": []
        }
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Skip .git and other hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                stats["directories"].append(root)
                
                for file in files:
                    if not file.startswith('.'):
                        stats["total_files"] += 1
                        
                        # Count file types
                        ext = Path(file).suffix.lower()
                        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                        
                        # Track large files (>1MB)
                        file_path = Path(root) / file
                        try:
                            file_size = file_path.stat().st_size
                            if file_size > 1024 * 1024:  # >1MB
                                stats["large_files"].append({
                                    "path": str(file_path.relative_to(self.project_root)),
                                    "size_mb": file_size / (1024 * 1024)
                                })
                        except:
                            pass  # Skip if can't get file size
                            
        except Exception as e:
            logger.warning(f"Error analyzing project structure: {e}")
            
        return stats
    
    async def _create_consolidated_dashboard(self):
        """Create consolidated metrics dashboard"""
        logger.info("🔍 Creating Consolidated Metrics Dashboard...")
        
        try:
            # Generate comprehensive dashboard
            dashboard = {
                "generation_info": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - self.execution_start_time).total_seconds(),
                    "project_root": str(self.project_root),
                    "generator_version": "1.0"
                },
                "metrics_summary": {
                    "total_metrics_generated": len(self.results["metrics_generated"]),
                    "successful_metrics": len([m for m in self.results["metrics_generated"].values() if m.get("status") == "success"]),
                    "total_errors": len(self.results["errors"]),
                    "error_types": list(set([e.get("type", "unknown") for e in self.results["errors"]]))
                },
                "generated_metrics": self.results["metrics_generated"],
                "errors_encountered": self.results["errors"],
                "available_reports": self._find_all_report_files(),
                "recommendations": self._generate_recommendations()
            }
            
            # Save dashboard to multiple formats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON dashboard
            dashboard_json = self.metrics_output_dir / f"comprehensive_metrics_dashboard_{timestamp}.json"
            with open(dashboard_json, 'w') as f:
                json.dump(dashboard, f, indent=2, default=str)
            
            # Markdown report
            dashboard_md = self.metrics_output_dir / f"comprehensive_metrics_report_{timestamp}.md"
            with open(dashboard_md, 'w') as f:
                f.write(self._generate_markdown_report(dashboard))
            
            logger.info(f"  ✅ Consolidated dashboard created:")
            logger.info(f"    JSON: {dashboard_json}")
            logger.info(f"    Markdown: {dashboard_md}")
            
            self.results["metrics_generated"]["consolidated_dashboard"] = {
                "status": "success",
                "dashboard_json": str(dashboard_json),
                "dashboard_markdown": str(dashboard_md),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"  ❌ Error creating consolidated dashboard: {e}")
            self.results["errors"].append({
                "type": "dashboard_exception",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
    
    def _find_all_report_files(self) -> Dict[str, List[str]]:
        """Find all generated report files"""
        report_locations = {
            "test_results": [],
            "performance_reports": [],
            "security_reports": [],
            "validation_reports": [],
            "metrics_output": []
        }
        
        # Test results
        test_results_dir = self.python_app_dir / "test_results"
        if test_results_dir.exists():
            report_locations["test_results"] = [str(f) for f in test_results_dir.glob("*")]
        
        # Performance reports
        perf_reports_dir = self.python_app_dir / "performance_reports"
        if perf_reports_dir.exists():
            report_locations["performance_reports"] = [str(f) for f in perf_reports_dir.glob("*")]
        
        # Security reports
        security_reports_dir = self.python_app_dir / "security_reports"
        if security_reports_dir.exists():
            report_locations["security_reports"] = [str(f) for f in security_reports_dir.glob("*")]
        
        # Validation reports
        validation_reports = list(self.python_app_dir.glob("phase4_validation_report_*.json"))
        report_locations["validation_reports"] = [str(f) for f in validation_reports]
        
        # Metrics output
        report_locations["metrics_output"] = [str(f) for f in self.metrics_output_dir.glob("*")]
        
        return report_locations
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics results"""
        recommendations = []
        
        successful_metrics = len([m for m in self.results["metrics_generated"].values() if m.get("status") == "success"])
        total_metrics = len(self.results["metrics_generated"])
        error_count = len(self.results["errors"])
        
        if successful_metrics == total_metrics and error_count == 0:
            recommendations.append("✅ All metrics generated successfully! System is performing well.")
        elif successful_metrics / total_metrics >= 0.8:
            recommendations.append("✅ Most metrics generated successfully. Review minor issues in error log.")
        else:
            recommendations.append("⚠️ Some metrics failed to generate. Review error log for issues.")
        
        if error_count > 0:
            error_types = list(set([e.get("type", "unknown") for e in self.results["errors"]]))
            recommendations.append(f"🔍 Found {error_count} errors of types: {', '.join(error_types)}")
        
        recommendations.append("📊 Review generated reports in the metrics_output directory")
        recommendations.append("🔄 Run metrics generation regularly to monitor system health")
        
        return recommendations
    
    def _generate_markdown_report(self, dashboard: Dict[str, Any]) -> str:
        """Generate markdown report from dashboard data"""
        md_content = f"""# Comprehensive Metrics Report - Multi-Sensor Recording System

**Generated:** {dashboard['generation_info']['timestamp']}  
**Duration:** {dashboard['generation_info']['duration_seconds']:.2f} seconds  
**Project:** {dashboard['generation_info']['project_root']}

## Executive Summary

- **Total Metrics Generated:** {dashboard['metrics_summary']['total_metrics_generated']}
- **Successful Metrics:** {dashboard['metrics_summary']['successful_metrics']}
- **Total Errors:** {dashboard['metrics_summary']['total_errors']}

## Generated Metrics

"""
        
        for metric_name, metric_data in dashboard['generated_metrics'].items():
            status_emoji = "✅" if metric_data.get("status") == "success" else "⚠️"
            md_content += f"### {status_emoji} {metric_name.replace('_', ' ').title()}\n"
            md_content += f"- **Status:** {metric_data.get('status', 'unknown')}\n"
            md_content += f"- **Timestamp:** {metric_data.get('timestamp', 'unknown')}\n"
            
            if 'report_files' in metric_data:
                md_content += f"- **Report Files:** {len(metric_data['report_files'])} files generated\n"
            
            md_content += "\n"
        
        if dashboard['errors_encountered']:
            md_content += "## Errors Encountered\n\n"
            for error in dashboard['errors_encountered']:
                md_content += f"- **{error.get('type', 'unknown')}:** {error.get('message', 'No message')}\n"
            md_content += "\n"
        
        md_content += "## Available Reports\n\n"
        for category, files in dashboard['available_reports'].items():
            if files:
                md_content += f"### {category.replace('_', ' ').title()}\n"
                for file in files[:10]:  # Limit to first 10 files
                    md_content += f"- {file}\n"
                if len(files) > 10:
                    md_content += f"- ... and {len(files) - 10} more files\n"
                md_content += "\n"
        
        md_content += "## Recommendations\n\n"
        for rec in dashboard['recommendations']:
            md_content += f"- {rec}\n"
        
        return md_content
    
    def _finalize_execution(self):
        """Finalize execution and generate summary"""
        end_time = datetime.now()
        duration = end_time - self.execution_start_time
        
        self.results["execution_info"]["end_time"] = end_time.isoformat()
        self.results["execution_info"]["duration_seconds"] = duration.total_seconds()
        
        # Generate summary
        successful_metrics = len([m for m in self.results["metrics_generated"].values() if m.get("status") == "success"])
        total_metrics = len(self.results["metrics_generated"])
        
        self.results["summary"] = {
            "total_metrics_attempted": total_metrics,
            "successful_metrics": successful_metrics,
            "failed_metrics": total_metrics - successful_metrics,
            "success_rate": (successful_metrics / total_metrics * 100) if total_metrics > 0 else 0,
            "total_errors": len(self.results["errors"]),
            "execution_duration_seconds": duration.total_seconds(),
            "overall_status": "success" if successful_metrics == total_metrics else "partial_success" if successful_metrics > 0 else "failed"
        }
        
        logger.info("="*80)
        logger.info("METRICS GENERATION SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Metrics Attempted: {total_metrics}")
        logger.info(f"Successful Metrics: {successful_metrics}")
        logger.info(f"Failed Metrics: {total_metrics - successful_metrics}")
        logger.info(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        logger.info(f"Total Errors: {len(self.results['errors'])}")
        logger.info(f"Execution Duration: {duration.total_seconds():.2f} seconds")
        logger.info(f"Overall Status: {self.results['summary']['overall_status'].upper()}")
        logger.info("="*80)


async def main():
    """Main entry point for comprehensive metrics generation"""
    print("=" * 80)
    print("COMPREHENSIVE METRICS GENERATION - Multi-Sensor Recording System")
    print("=" * 80)
    print()
    
    try:
        orchestrator = MetricsOrchestrator()
        results = await orchestrator.generate_all_metrics()
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = orchestrator.metrics_output_dir / f"metrics_generation_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("=" * 80)
        print("METRICS GENERATION COMPLETED")
        print("=" * 80)
        print(f"Results saved to: {results_file}")
        print(f"Overall Status: {results['summary']['overall_status'].upper()}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"Critical error in metrics generation: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = asyncio.run(main())
    sys.exit(0 if results and results.get("summary", {}).get("overall_status") == "success" else 1)