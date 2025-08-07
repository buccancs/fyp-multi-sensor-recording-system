#!/usr/bin/env python3
"""
Quality Dashboard Generator
Generates a comprehensive quality dashboard from collected metrics
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_quality_dashboard():
    """Generate complete quality dashboard"""
    
    # Collect all quality metrics
    quality_data = {
        'timestamp': datetime.now().isoformat(),
        'commit_sha': os.environ.get('GITHUB_SHA', 'unknown'),
        'branch': os.environ.get('GITHUB_REF_NAME', 'unknown'),
        'python_metrics': {},
        'kotlin_metrics': {},
        'overall_score': 0
    }
    
    # Process Python metrics
    python_reports = Path('downloaded-reports/python-quality-reports')
    if python_reports.exists():
        quality_data['python_metrics'] = collect_python_metrics(python_reports)
    
    # Process Kotlin metrics 
    kotlin_reports = Path('downloaded-reports/kotlin-quality-reports')
    if kotlin_reports.exists():
        quality_data['kotlin_metrics'] = collect_kotlin_metrics(kotlin_reports)
    
    # Calculate overall quality score
    quality_data['overall_score'] = calculate_quality_score(
        quality_data['python_metrics'], 
        quality_data['kotlin_metrics']
    )
    
    # Generate dashboard files
    generate_dashboard_html(quality_data)
    generate_metrics_json(quality_data)
    
    return quality_data['overall_score']

def collect_python_metrics(reports_path):
    """Collect Python quality metrics from reports"""
    metrics = {}
    
    # Pylint report
    pylint_file = reports_path / 'pylint-report.json'
    if pylint_file.exists():
        with open(pylint_file) as f:
            metrics['pylint'] = json.load(f)
    
    # Complexity metrics
    complexity_path = reports_path / 'complexity'
    if complexity_path.exists():
        metrics['complexity'] = {}
        for complexity_file in complexity_path.glob('*.json'):
            with open(complexity_file) as f:
                metrics['complexity'][complexity_file.stem] = json.load(f)
    
    # Security report
    security_file = reports_path / 'security-report.json'
    if security_file.exists():
        with open(security_file) as f:
            metrics['security'] = json.load(f)
            
    return metrics

def collect_kotlin_metrics(reports_path):
    """Collect Kotlin quality metrics from reports"""
    metrics = {}
    
    # Complexity metrics
    complexity_file = reports_path / 'complexity-metrics.json'
    if complexity_file.exists():
        with open(complexity_file) as f:
            metrics['complexity'] = json.load(f)
            
    return metrics

def calculate_quality_score(python_metrics, kotlin_metrics):
    """Calculate overall quality score (0-10)"""
    score = 10.0  # Start with perfect score
    
    # Python penalties
    if 'complexity' in python_metrics:
        complexity = python_metrics['complexity']
        if 'cyclomatic-complexity' in complexity:
            # Penalty for high complexity functions
            high_complexity_count = len([
                f for f in complexity['cyclomatic-complexity'].get('results', [])
                if f.get('complexity', 0) > 15
            ])
            score -= min(high_complexity_count * 0.5, 3.0)
    
    if 'security' in python_metrics:
        security = python_metrics['security']
        if 'results' in security:
            # Penalty for security issues
            security_issues = len(security['results'])
            score -= min(security_issues * 0.3, 2.0)
    
    # Kotlin penalties  
    if 'complexity' in kotlin_metrics:
        complexity = kotlin_metrics['complexity']
        if not complexity.get('threshold_compliant', True):
            score -= 1.0
            
    return max(score, 0.0)

def generate_dashboard_html(quality_data):
    """Generate HTML dashboard"""
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .score { font-size: 24px; font-weight: bold; }
        .good { color: green; }
        .warning { color: orange; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Code Quality Dashboard</h1>
    <div class="metric">
        <h2>Overall Quality Score</h2>
        <div class="score {score_class}">{score:.1f}/10</div>
        <p>Generated: {timestamp}</p>
        <p>Commit: {commit_sha}</p>
        <p>Branch: {branch}</p>
    </div>
    
    <div class="metric">
        <h2>Python Metrics</h2>
        <pre>{python_summary}</pre>
    </div>
    
    <div class="metric">
        <h2>Kotlin Metrics</h2>
        <pre>{kotlin_summary}</pre>
    </div>
</body>
</html>
"""
    
    score = quality_data['overall_score']
    score_class = 'good' if score >= 8 else 'warning' if score >= 6 else 'error'
    
    html_content = html_template.format(
        score=score,
        score_class=score_class,
        timestamp=quality_data['timestamp'],
        commit_sha=quality_data['commit_sha'],
        branch=quality_data['branch'],
        python_summary=json.dumps(quality_data['python_metrics'], indent=2),
        kotlin_summary=json.dumps(quality_data['kotlin_metrics'], indent=2)
    )
    
    with open('quality-dashboard.html', 'w') as f:
        f.write(html_content)

def generate_metrics_json(quality_data):
    """Generate JSON metrics file"""
    with open('quality-metrics.json', 'w') as f:
        json.dump(quality_data, f, indent=2)

if __name__ == '__main__':
    score = generate_quality_dashboard()
    
    # Set output for GitHub Actions
    print(f"::set-output name=quality_score::{score:.1f}")
    
    # Fail if quality is too low
    if score < 6.0:
        print("::error::Code quality score is below acceptable threshold (6.0)")
        exit(1)