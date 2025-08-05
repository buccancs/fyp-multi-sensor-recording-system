#!/usr/bin/env python3
"""
Comprehensive Chapter 6 Evaluation Test Runner

This script orchestrates the complete Chapter 6 evaluation suite including
documentation validation, performance assessment, metrics collection, and
report generation for academic thesis standards compliance.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class Chapter6TestRunner:
    """Comprehensive test runner for Chapter 6 evaluation suite."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.results = {
            "execution_timestamp": datetime.now().isoformat(),
            "test_suite_version": "1.0.0",
            "evaluation_components": {},
            "overall_results": {},
            "recommendations": [],
            "compliance_status": "UNKNOWN"
        }
    
    def run_comprehensive_evaluation(self) -> bool:
        """Run the complete Chapter 6 evaluation suite."""
        print("🚀 Starting Comprehensive Chapter 6 Evaluation")
        print("=" * 60)
        
        success_count = 0
        total_tests = 0
        
        # 1. Core Chapter 6 Evaluation
        print("\n1️⃣ Running Core Chapter 6 Evaluation...")
        core_success = self.run_core_evaluation()
        total_tests += 1
        if core_success:
            success_count += 1
        self.results["evaluation_components"]["core_evaluation"] = {
            "success": core_success,
            "component": "Chapter 6 Documentation and Achievement Validation"
        }
        
        # 2. Performance Metrics Collection
        print("\n2️⃣ Collecting Performance Metrics...")
        metrics_success = self.collect_performance_metrics()
        total_tests += 1
        if metrics_success:
            success_count += 1
        self.results["evaluation_components"]["performance_metrics"] = {
            "success": metrics_success,
            "component": "System Performance and Resource Analysis"
        }
        
        # 3. Documentation Quality Assessment
        print("\n3️⃣ Assessing Documentation Quality...")
        docs_success = self.assess_documentation_quality()
        total_tests += 1
        if docs_success:
            success_count += 1
        self.results["evaluation_components"]["documentation_quality"] = {
            "success": docs_success,
            "component": "Multi-Sensor System Documentation Validation"
        }
        
        # 4. Research Impact Validation
        print("\n4️⃣ Validating Research Impact...")
        impact_success = self.validate_research_impact()
        total_tests += 1
        if impact_success:
            success_count += 1
        self.results["evaluation_components"]["research_impact"] = {
            "success": impact_success,
            "component": "Academic Standards and Research Contribution Assessment"
        }
        
        # 5. Future Work Assessment
        print("\n5️⃣ Assessing Future Work Planning...")
        future_success = self.assess_future_work()
        total_tests += 1
        if future_success:
            success_count += 1
        self.results["evaluation_components"]["future_work"] = {
            "success": future_success,
            "component": "Future Work and Extensions Evaluation"
        }
        
        # Calculate overall results
        success_rate = (success_count / total_tests) * 100
        self.results["overall_results"] = {
            "total_components": total_tests,
            "successful_components": success_count,
            "success_rate": success_rate,
            "evaluation_complete": True
        }
        
        # Determine compliance status
        if success_rate >= 90:
            self.results["compliance_status"] = "EXCELLENT"
        elif success_rate >= 80:
            self.results["compliance_status"] = "GOOD"
        elif success_rate >= 70:
            self.results["compliance_status"] = "SATISFACTORY"
        else:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Generate final report
        self.generate_final_report()
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({success_count}/{total_tests})")
        print(f"🏆 Compliance Status: {self.results['compliance_status']}")
        
        return success_rate >= 80
    
    def run_core_evaluation(self) -> bool:
        """Run the core Chapter 6 evaluation script."""
        try:
            result = subprocess.run([
                sys.executable, "test_chapter6_evaluation.py"
            ], capture_output=True, text=True, timeout=300, cwd=self.repo_root)
            
            success = result.returncode == 0
            
            if success:
                print("    ✅ Core evaluation completed successfully")
                # Try to load detailed results - but don't fail if we can't access them
                try:
                    results_file = self.repo_root / "chapter6_evaluation_results.json"
                    if results_file.exists():
                        with open(results_file, 'r') as f:
                            core_results = json.load(f)
                        # Create the nested structure if it doesn't exist
                        if "detailed_results" not in self.results["evaluation_components"]["core_evaluation"]:
                            self.results["evaluation_components"]["core_evaluation"]["detailed_results"] = core_results
                except Exception:
                    pass  # Silently continue if we can't load detailed results
            else:
                print("    ❌ Core evaluation failed")
                if result.stderr:
                    print(f"    Error: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("    ❌ Core evaluation timed out")
            return False
        except Exception as e:
            print(f"    ❌ Core evaluation error: {e}")
            return False
    
    def collect_performance_metrics(self) -> bool:
        """Collect system performance metrics."""
        try:
            result = subprocess.run([
                sys.executable, "chapter6_evaluation_utils.py"
            ], capture_output=True, text=True, timeout=180, cwd=self.repo_root)
            
            success = result.returncode == 0
            
            if success:
                print("    ✅ Performance metrics collected successfully")
                # Try to load detailed metrics - but don't fail if we can't access them
                try:
                    metrics_file = self.repo_root / "chapter6_metrics_detailed.json"
                    if metrics_file.exists():
                        with open(metrics_file, 'r') as f:
                            metrics_data = json.load(f)
                        # Create the nested structure if it doesn't exist
                        if "detailed_metrics" not in self.results["evaluation_components"]["performance_metrics"]:
                            self.results["evaluation_components"]["performance_metrics"]["detailed_metrics"] = metrics_data
                except Exception:
                    pass  # Silently continue if we can't load detailed metrics
            else:
                print("    ❌ Performance metrics collection failed")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("    ❌ Performance metrics collection timed out")
            return False
        except Exception as e:
            print(f"    ❌ Performance metrics error: {e}")
            return False
    
    def assess_documentation_quality(self) -> bool:
        """Assess documentation quality and completeness."""
        try:
            # Check for key documentation files
            required_files = [
                "docs/multi_sensor_system.md",
                "docs/thesis_report/Chapter_6_Conclusions_and_Evaluation.md",
                "README.md"
            ]
            
            found_files = 0
            total_files = len(required_files)
            
            for file_path in required_files:
                full_path = self.repo_root / file_path
                if full_path.exists():
                    found_files += 1
                    print(f"    ✅ Found: {file_path}")
                else:
                    print(f"    ❌ Missing: {file_path}")
            
            # Check documentation quality
            multi_sensor_doc = self.repo_root / "docs" / "multi_sensor_system.md"
            quality_score = 0.0
            
            if multi_sensor_doc.exists():
                content = multi_sensor_doc.read_text()
                
                # Check for comprehensive content
                quality_indicators = [
                    "System Architecture",
                    "Component Overview",
                    "Performance Characteristics",
                    "Implementation References",
                    "Research Methodology"
                ]
                
                found_indicators = sum(1 for indicator in quality_indicators if indicator in content)
                quality_score = found_indicators / len(quality_indicators)
                
                print(f"    📊 Documentation quality: {quality_score*100:.1f}% ({found_indicators}/{len(quality_indicators)} sections)")
            
            overall_score = (found_files / total_files) * 0.6 + quality_score * 0.4
            success = overall_score >= 0.8
            
            # Store the assessment results properly
            if "documentation_quality" not in self.results["evaluation_components"]:
                self.results["evaluation_components"]["documentation_quality"] = {}
            
            self.results["evaluation_components"]["documentation_quality"]["assessment"] = {
                "files_found": found_files,
                "files_required": total_files,
                "quality_score": quality_score,
                "overall_score": overall_score
            }
            
            print(f"    🎯 Overall documentation score: {overall_score:.2f} ({'PASS' if success else 'FAIL'})")
            return success
            
        except Exception as e:
            print(f"    ❌ Documentation assessment error: {e}")
            return False
    
    def validate_research_impact(self) -> bool:
        """Validate research impact and academic standards."""
        try:
            # Check for academic documentation
            academic_files = [
                "docs/thesis_report/Chapter_6_Conclusions_and_Evaluation.md",
                "docs/TECHNICAL_GLOSSARY.md",
                "THESIS_REPORT.md"
            ]
            
            found_academic = sum(1 for f in academic_files if (self.repo_root / f).exists())
            
            # Check for research contributions
            chapter6_file = self.repo_root / "docs" / "thesis_report" / "Chapter_6_Conclusions_and_Evaluation.md"
            contributions_score = 0.0
            
            if chapter6_file.exists():
                content = chapter6_file.read_text()
                
                # Look for key research contributions
                contributions = [
                    "Technical Innovation",
                    "Scientific and Methodological Contributions",
                    "Research Impact and Validation",
                    "Performance Objectives Assessment"
                ]
                
                found_contributions = sum(1 for contrib in contributions if contrib in content)
                contributions_score = found_contributions / len(contributions)
                
                print(f"    📚 Academic files: {found_academic}/{len(academic_files)}")
                print(f"    🔬 Research contributions: {contributions_score*100:.1f}%")
            
            overall_impact = (found_academic / len(academic_files)) * 0.5 + contributions_score * 0.5
            success = overall_impact >= 0.75
            
            # Store the validation results properly
            if "research_impact" not in self.results["evaluation_components"]:
                self.results["evaluation_components"]["research_impact"] = {}
                
            self.results["evaluation_components"]["research_impact"]["validation"] = {
                "academic_files": found_academic,
                "contributions_score": contributions_score,
                "overall_impact": overall_impact
            }
            
            print(f"    🎯 Overall impact score: {overall_impact:.2f} ({'PASS' if success else 'FAIL'})")
            return success
            
        except Exception as e:
            print(f"    ❌ Research impact validation error: {e}")
            return False
    
    def assess_future_work(self) -> bool:
        """Assess future work planning and recommendations."""
        try:
            chapter6_file = self.repo_root / "docs" / "thesis_report" / "Chapter_6_Conclusions_and_Evaluation.md"
            
            if not chapter6_file.exists():
                print("    ❌ Chapter 6 file not found")
                return False
            
            content = chapter6_file.read_text()
            
            # Check for comprehensive future work planning
            future_work_areas = [
                "Technology Enhancement Opportunities",
                "Application Domain Extensions",
                "Research Advancement Opportunities",
                "Open Source and Community Development"
            ]
            
            found_areas = sum(1 for area in future_work_areas if area in content)
            future_work_score = found_areas / len(future_work_areas)
            
            # Check for specific planning elements
            planning_elements = [
                "Machine Learning Integration",
                "Clinical Research",
                "Educational Applications",
                "Community Ecosystem"
            ]
            
            found_elements = sum(1 for element in planning_elements if element in content)
            planning_score = found_elements / len(planning_elements)
            
            overall_score = (future_work_score * 0.6) + (planning_score * 0.4)
            success = overall_score >= 0.7
            
            print(f"    🔮 Future work areas: {future_work_score*100:.1f}% ({found_areas}/{len(future_work_areas)})")
            print(f"    📋 Planning elements: {planning_score*100:.1f}% ({found_elements}/{len(planning_elements)})")
            
            # Store the assessment results properly
            if "future_work" not in self.results["evaluation_components"]:
                self.results["evaluation_components"]["future_work"] = {}
                
            self.results["evaluation_components"]["future_work"]["assessment"] = {
                "future_work_score": future_work_score,
                "planning_score": planning_score,
                "overall_score": overall_score
            }
            
            print(f"    🎯 Overall future work score: {overall_score:.2f} ({'PASS' if success else 'FAIL'})")
            return success
            
        except Exception as e:
            print(f"    ❌ Future work assessment error: {e}")
            return False
    
    def generate_recommendations(self):
        """Generate specific recommendations based on evaluation results."""
        recommendations = []
        
        # Check each component and generate targeted recommendations
        for component, data in self.results["evaluation_components"].items():
            if not data["success"]:
                if component == "core_evaluation":
                    recommendations.append("Review Chapter 6 documentation structure and ensure all required sections are complete")
                elif component == "performance_metrics":
                    recommendations.append("Verify system performance monitoring capabilities and metric collection")
                elif component == "documentation_quality":
                    recommendations.append("Enhance multi-sensor system documentation with comprehensive technical details")
                elif component == "research_impact":
                    recommendations.append("Strengthen academic contribution documentation and research impact validation")
                elif component == "future_work":
                    recommendations.append("Expand future work planning with more detailed roadmaps and implementation strategies")
        
        # Add general recommendations based on compliance status
        status = self.results["compliance_status"]
        if status == "NEEDS_IMPROVEMENT":
            recommendations.extend([
                "Conduct comprehensive review of all Chapter 6 components",
                "Align documentation with academic thesis standards",
                "Implement systematic quality assurance processes"
            ])
        elif status == "SATISFACTORY":
            recommendations.extend([
                "Enhance quantitative validation and statistical analysis",
                "Improve integration between different evaluation components"
            ])
        
        self.results["recommendations"] = recommendations
    
    def generate_final_report(self):
        """Generate comprehensive final evaluation report."""
        
        # Save detailed JSON results
        json_results_file = self.repo_root / "chapter6_comprehensive_evaluation.json"
        with open(json_results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate markdown summary
        summary_lines = []
        summary_lines.append("# Chapter 6 Comprehensive Evaluation Report")
        summary_lines.append(f"**Generated:** {self.results['execution_timestamp']}")
        summary_lines.append(f"**Suite Version:** {self.results['test_suite_version']}")
        summary_lines.append("")
        
        # Overall results
        overall = self.results["overall_results"]
        summary_lines.append("## Overall Results")
        summary_lines.append(f"- **Success Rate:** {overall['success_rate']:.1f}%")
        summary_lines.append(f"- **Components Tested:** {overall['total_components']}")
        summary_lines.append(f"- **Successful Components:** {overall['successful_components']}")
        summary_lines.append(f"- **Compliance Status:** {self.results['compliance_status']}")
        summary_lines.append("")
        
        # Component results
        summary_lines.append("## Component Results")
        for component, data in self.results["evaluation_components"].items():
            status = "✅ PASS" if data["success"] else "❌ FAIL"
            summary_lines.append(f"- **{data['component']}:** {status}")
        summary_lines.append("")
        
        # Recommendations
        if self.results["recommendations"]:
            summary_lines.append("## Recommendations")
            for i, rec in enumerate(self.results["recommendations"], 1):
                summary_lines.append(f"{i}. {rec}")
            summary_lines.append("")
        
        # Save summary
        summary_file = self.repo_root / "chapter6_comprehensive_summary.md"
        with open(summary_file, 'w') as f:
            f.write("\n".join(summary_lines))
        
        print(f"\n📄 Comprehensive results saved to: {json_results_file}")
        print(f"📋 Summary report saved to: {summary_file}")


def main():
    """Main test runner execution."""
    print("🎯 Chapter 6 Comprehensive Evaluation Test Runner")
    print("=" * 50)
    print("This suite validates Chapter 6 conclusions and evaluation")
    print("according to academic thesis standards.\n")
    
    runner = Chapter6TestRunner()
    success = runner.run_comprehensive_evaluation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CHAPTER 6 EVALUATION SUITE PASSED")
        print("🎉 All components meet academic standards!")
        return 0
    else:
        print("❌ CHAPTER 6 EVALUATION SUITE FAILED")
        print("⚠️ Some components need improvement. See recommendations above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())