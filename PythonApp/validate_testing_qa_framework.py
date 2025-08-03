#!/usr/bin/env python3
"""
Testing and QA Framework Document Validation

This script validates the structure and completeness of the consolidated
Testing and QA Framework document.

Author: Multi-Sensor Recording System Team
Date: 2025-01-03
"""

import json
import re
from pathlib import Path


def validate_testing_qa_document():
    """Validate the Testing and QA Framework document structure."""
    
    doc_path = Path(__file__).parent.parent / "docs" / "TESTING_QA_FRAMEWORK.md"
    
    print("🔍 Testing and QA Framework Document Validation")
    print("=" * 60)
    
    if not doc_path.exists():
        print("❌ Document not found:", doc_path)
        return False
    
    content = doc_path.read_text()
    
    # Required sections
    required_sections = [
        "Overview",
        "Framework Architecture", 
        "Testing Strategy",
        "Test Execution Guide",
        "Example Report Structures",
        "Quality Assurance Processes",
        "Performance Monitoring",
        "Best Practices",
        "Troubleshooting"
    ]
    
    validation_results = {
        "document_found": True,
        "required_sections": {},
        "example_reports": {},
        "code_blocks": 0,
        "mermaid_diagrams": 0,
        "json_examples": 0,
        "bash_examples": 0,
        "total_lines": len(content.split('\n')),
        "word_count": len(content.split())
    }
    
    print(f"📄 Document found: {doc_path}")
    print(f"📊 Total lines: {validation_results['total_lines']}")
    print(f"📝 Word count: {validation_results['word_count']}")
    print()
    
    # Check required sections
    print("🔍 Checking required sections:")
    for section in required_sections:
        section_pattern = rf"#+\s*{re.escape(section)}"
        if re.search(section_pattern, content, re.IGNORECASE):
            validation_results["required_sections"][section] = True
            print(f"  ✅ {section}")
        else:
            validation_results["required_sections"][section] = False
            print(f"  ❌ {section}")
    
    print()
    
    # Check for example report structures
    print("📋 Checking example report structures:")
    report_types = [
        "Test Execution Summary Report",
        "Performance Benchmark Report", 
        "Network Resilience Test Report",
        "Quality Assurance Report",
        "Integration Test Report"
    ]
    
    for report_type in report_types:
        if report_type.lower() in content.lower():
            validation_results["example_reports"][report_type] = True
            print(f"  ✅ {report_type}")
        else:
            validation_results["example_reports"][report_type] = False
            print(f"  ❌ {report_type}")
    
    print()
    
    # Count code blocks and examples
    validation_results["code_blocks"] = len(re.findall(r'```', content)) // 2
    validation_results["mermaid_diagrams"] = len(re.findall(r'```mermaid', content))
    validation_results["json_examples"] = len(re.findall(r'```json', content))
    validation_results["bash_examples"] = len(re.findall(r'```bash', content))
    
    print("📊 Content analysis:")
    print(f"  📦 Code blocks: {validation_results['code_blocks']}")
    print(f"  🎨 Mermaid diagrams: {validation_results['mermaid_diagrams']}")
    print(f"  📄 JSON examples: {validation_results['json_examples']}")
    print(f"  🖥️  Bash examples: {validation_results['bash_examples']}")
    
    print()
    
    # Check for table of contents
    has_toc = "table of contents" in content.lower()
    print(f"📋 Table of Contents: {'✅' if has_toc else '❌'}")
    
    # Check for internal links
    internal_links = len(re.findall(r'\[.*?\]\(#.*?\)', content))
    print(f"🔗 Internal links: {internal_links}")
    
    print()
    
    # Overall assessment
    required_sections_complete = all(validation_results["required_sections"].values())
    example_reports_complete = all(validation_results["example_reports"].values())
    sufficient_content = validation_results["word_count"] > 3000
    has_examples = validation_results["json_examples"] >= 3 and validation_results["bash_examples"] >= 5
    
    overall_score = sum([
        required_sections_complete,
        example_reports_complete, 
        sufficient_content,
        has_examples,
        has_toc
    ])
    
    print("🎯 Overall Assessment:")
    print(f"  📋 Required sections complete: {'✅' if required_sections_complete else '❌'}")
    print(f"  📊 Example reports complete: {'✅' if example_reports_complete else '❌'}")
    print(f"  📝 Sufficient content: {'✅' if sufficient_content else '❌'}")
    print(f"  💻 Has practical examples: {'✅' if has_examples else '❌'}")
    print(f"  🗂️  Has table of contents: {'✅' if has_toc else '❌'}")
    print()
    print(f"📈 Quality Score: {overall_score}/5")
    
    if overall_score >= 4:
        print("🎉 Document quality: EXCELLENT")
        status = "EXCELLENT"
    elif overall_score >= 3:
        print("✅ Document quality: GOOD") 
        status = "GOOD"
    else:
        print("⚠️  Document quality: NEEDS IMPROVEMENT")
        status = "NEEDS_IMPROVEMENT"
    
    # Save validation results
    results_path = Path(__file__).parent / "test_results" / "testing_qa_validation.json"
    results_path.parent.mkdir(exist_ok=True)
    
    validation_results.update({
        "validation_timestamp": "2025-01-03T15:00:00.000Z",
        "overall_score": overall_score,
        "quality_status": status,
        "has_toc": has_toc,
        "internal_links": internal_links
    })
    
    with open(results_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"💾 Validation results saved to: {results_path}")
    
    return overall_score >= 4


if __name__ == "__main__":
    success = validate_testing_qa_document()
    exit(0 if success else 1)