#!/usr/bin/env python3
"""
Simple Metrics Visualizer - Multi-Sensor Recording System

A lightweight visualizer that works without external dependencies,
creating basic HTML visualizations for metrics data.

Author: Multi-Sensor Recording System Team
Date: 2025-01-04
Version: 1.0
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


class SimpleMetricsVisualizer:
    """Simple HTML-based visualizer for metrics data"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.metrics_output_dir = self.project_root / "metrics_output"
        self.performance_reports_dir = self.project_root / "PythonApp" / "performance_reports"
        self.visualizations_dir = self.metrics_output_dir / "visualizations"
        self.visualizations_dir.mkdir(exist_ok=True)
        
        self.performance_data = None
        self.metrics_data = None
    
    def create_visualizations(self) -> Dict[str, Any]:
        """Create simple HTML visualizations"""
        logger.info("🎨 Creating simple HTML visualizations...")
        
        results = {
            "visualization_info": {
                "start_time": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "output_directory": str(self.visualizations_dir)
            },
            "generated_files": [],
            "errors": []
        }
        
        try:
            # Load data
            self._load_data()
            
            # Create performance dashboard
            if self.performance_data:
                self._create_performance_dashboard(results)
            
            # Create metrics overview
            if self.metrics_data:
                self._create_metrics_overview(results)
            
            # Create comprehensive dashboard
            self._create_main_dashboard(results)
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            results["errors"].append(str(e))
        
        results["visualization_info"]["end_time"] = datetime.now().isoformat()
        return results
    
    def _load_data(self):
        """Load available metrics data"""
        # Load performance data
        perf_files = list(self.performance_reports_dir.glob("performance_benchmark_*.json")) if self.performance_reports_dir.exists() else []
        if perf_files:
            latest_perf = max(perf_files, key=os.path.getctime)
            with open(latest_perf, 'r') as f:
                self.performance_data = json.load(f)
            logger.info(f"  📊 Loaded performance data: {latest_perf.name}")
        
        # Load metrics data
        metrics_files = list(self.metrics_output_dir.glob("comprehensive_metrics_dashboard_*.json")) if self.metrics_output_dir.exists() else []
        if metrics_files:
            latest_metrics = max(metrics_files, key=os.path.getctime)
            with open(latest_metrics, 'r') as f:
                self.metrics_data = json.load(f)
            logger.info(f"  📋 Loaded metrics data: {latest_metrics.name}")
    
    def _create_performance_dashboard(self, results: Dict[str, Any]):
        """Create performance visualization dashboard"""
        logger.info("  📈 Creating performance dashboard...")
        
        detailed_results = self.performance_data.get('detailed_results', [])
        perf_stats = self.performance_data.get('performance_statistics', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Benchmark Dashboard</title>
    <style>
        {self._get_base_css()}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .bar-chart {{
            display: flex;
            align-items: flex-end;
            height: 200px;
            margin: 20px 0;
            border-bottom: 2px solid #ddd;
            border-left: 2px solid #ddd;
        }}
        .bar {{
            margin: 0 2px;
            background: linear-gradient(45deg, #1f77b4, #87ceeb);
            border-radius: 4px 4px 0 0;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            color: white;
            font-size: 10px;
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
            position: relative;
            flex: 1;
            min-width: 60px;
        }}
        .bar-label {{
            position: absolute;
            bottom: -25px;
            transform: rotate(-45deg);
            transform-origin: center;
            font-size: 10px;
            color: #666;
            white-space: nowrap;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Performance Benchmark Dashboard</h1>
            <p>Multi-Sensor Recording System Performance Analysis</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Average Duration</h3>
                <div class="stat-value">{perf_stats.get('duration', {}).get('mean', 0):.2f}s</div>
            </div>
            <div class="stat-card">
                <h3>Average Memory</h3>
                <div class="stat-value">{perf_stats.get('memory_usage_mb', {}).get('mean', 0):.1f}MB</div>
            </div>
            <div class="stat-card">
                <h3>Average CPU</h3>
                <div class="stat-value">{perf_stats.get('cpu_usage_percent', {}).get('mean', 0):.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Average Throughput</h3>
                <div class="stat-value">{perf_stats.get('throughput_ops_per_sec', {}).get('mean', 0):,.0f}</div>
                <small>ops/sec</small>
            </div>
        </div>
        
        {self._create_performance_charts_html(detailed_results)}
        
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        dashboard_path = self.visualizations_dir / "performance_dashboard.html"
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
        
        results["generated_files"].append(str(dashboard_path))
        logger.info(f"    ✅ Performance dashboard saved: {dashboard_path}")
    
    def _create_performance_charts_html(self, detailed_results: List[Dict]) -> str:
        """Create HTML charts for performance data"""
        if not detailed_results:
            return "<p>No performance data available</p>"
        
        # Duration chart
        max_duration = max([r.get('duration_seconds', 0) for r in detailed_results])
        duration_chart = '<div class="chart-container"><h3>Test Duration (seconds)</h3><div class="bar-chart">'
        
        for result in detailed_results:
            duration = result.get('duration_seconds', 0)
            height = (duration / max_duration * 180) if max_duration > 0 else 0
            test_name = result.get('test_name', '').replace('_', ' ')
            
            duration_chart += f'''
            <div class="bar" style="height: {height}px;">
                <span>{duration:.2f}s</span>
                <div class="bar-label">{test_name}</div>
            </div>
            '''
        
        duration_chart += '</div></div>'
        
        # Memory chart
        max_memory = max([r.get('memory_usage_mb', 0) for r in detailed_results])
        memory_chart = '<div class="chart-container"><h3>Memory Usage (MB)</h3><div class="bar-chart">'
        
        for result in detailed_results:
            memory = result.get('memory_usage_mb', 0)
            height = (memory / max_memory * 180) if max_memory > 0 else 0
            test_name = result.get('test_name', '').replace('_', ' ')
            
            memory_chart += f'''
            <div class="bar" style="height: {height}px; background: linear-gradient(45deg, #ff7f0e, #ffb347);">
                <span>{memory:.1f}MB</span>
                <div class="bar-label">{test_name}</div>
            </div>
            '''
        
        memory_chart += '</div></div>'
        
        return duration_chart + memory_chart
    
    def _create_metrics_overview(self, results: Dict[str, Any]):
        """Create metrics overview dashboard"""
        logger.info("  📊 Creating metrics overview...")
        
        metrics_summary = self.metrics_data.get('metrics_summary', {})
        generated_metrics = self.metrics_data.get('generated_metrics', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metrics Overview Dashboard</title>
    <style>
        {self._get_base_css()}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-item {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #1f77b4;
        }}
        .metric-item.success {{
            border-left-color: #28a745;
        }}
        .metric-item.warning {{
            border-left-color: #ffc107;
        }}
        .metric-item.error {{
            border-left-color: #dc3545;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-success {{ background-color: #28a745; }}
        .status-warning {{ background-color: #ffc107; }}
        .status-error {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Metrics Overview Dashboard</h1>
            <p>Comprehensive metrics analysis for Multi-Sensor Recording System</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Metrics</h3>
                <div class="stat-value">{metrics_summary.get('total_metrics_generated', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Successful</h3>
                <div class="stat-value">{metrics_summary.get('successful_metrics', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="stat-value">{(metrics_summary.get('successful_metrics', 0) / max(metrics_summary.get('total_metrics_generated', 1), 1) * 100):.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Total Errors</h3>
                <div class="stat-value">{metrics_summary.get('total_errors', 0)}</div>
            </div>
        </div>
        
        <h2>📋 Generated Metrics</h2>
        <div class="metrics-grid">
            {self._create_metrics_list_html(generated_metrics)}
        </div>
        
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        overview_path = self.visualizations_dir / "metrics_overview.html"
        with open(overview_path, 'w') as f:
            f.write(html_content)
        
        results["generated_files"].append(str(overview_path))
        logger.info(f"    ✅ Metrics overview saved: {overview_path}")
    
    def _create_metrics_list_html(self, generated_metrics: Dict[str, Any]) -> str:
        """Create HTML list of generated metrics"""
        html = ""
        
        for metric_name, metric_data in generated_metrics.items():
            status = metric_data.get('status', 'unknown')
            timestamp = metric_data.get('timestamp', 'N/A')
            
            if status == 'success':
                css_class = 'success'
                indicator_class = 'status-success'
                status_icon = '✅'
            elif status in ['completed_with_errors', 'completed']:
                css_class = 'warning'
                indicator_class = 'status-warning'
                status_icon = '⚠️'
            else:
                css_class = 'error'
                indicator_class = 'status-error'
                status_icon = '❌'
            
            display_name = metric_name.replace('_', ' ').title()
            
            html += f'''
            <div class="metric-item {css_class}">
                <h4>{status_icon} {display_name}</h4>
                <p><span class="status-indicator {indicator_class}"></span>Status: {status}</p>
                <small>Timestamp: {timestamp}</small>
            </div>
            '''
        
        return html if html else "<p>No metrics data available</p>"
    
    def _create_main_dashboard(self, results: Dict[str, Any]):
        """Create main comprehensive dashboard"""
        logger.info("  🌐 Creating main dashboard...")
        
        dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Sensor Recording System - Metrics Dashboard</title>
    <style>
        {self._get_base_css()}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .dashboard-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        .dashboard-card:hover {{
            transform: translateY(-5px);
        }}
        .dashboard-card h3 {{
            color: #1f77b4;
            margin-bottom: 15px;
        }}
        .dashboard-link {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #1f77b4, #87ceeb);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin-top: 15px;
            transition: transform 0.3s ease;
        }}
        .dashboard-link:hover {{
            transform: scale(1.05);
        }}
        .feature-list {{
            text-align: left;
            margin: 15px 0;
        }}
        .feature-list li {{
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }}
        .feature-list li:before {{
            content: "📊";
            position: absolute;
            left: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Multi-Sensor Recording System</h1>
            <p>Comprehensive Metrics & Visualization Dashboard</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h3>📈 Performance Metrics</h3>
                <p>Detailed performance benchmarks, memory usage, CPU utilization, and throughput analysis.</p>
                <ul class="feature-list">
                    <li>Test execution times</li>
                    <li>Memory usage patterns</li>
                    <li>CPU utilization</li>
                    <li>Throughput analysis</li>
                </ul>
                <a href="./performance_dashboard.html" class="dashboard-link">View Performance Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h3>📊 Metrics Overview</h3>
                <p>Comprehensive overview of all generated metrics with success rates and status indicators.</p>
                <ul class="feature-list">
                    <li>Metrics generation status</li>
                    <li>Success rate analysis</li>
                    <li>Error tracking</li>
                    <li>Timeline information</li>
                </ul>
                <a href="./metrics_overview.html" class="dashboard-link">View Metrics Overview</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🎯 Quick Stats</h3>
                <p>Key performance indicators and system health metrics at a glance.</p>
                <div class="stats-grid">
                    {self._create_quick_stats_html()}
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3>📁 Data Sources</h3>
                <p>Information about available data sources and generated reports.</p>
                <ul class="feature-list">
                    <li>Performance data: {"✅ Available" if self.performance_data else "❌ Not found"}</li>
                    <li>Metrics data: {"✅ Available" if self.metrics_data else "❌ Not found"}</li>
                    <li>Generated files: {len(results["generated_files"])}</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Available Visualizations</h2>
            <div class="file-list">
                {self._create_files_list_html(results["generated_files"])}
            </div>
        </div>
        
        <div class="timestamp">
            Dashboard generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        main_dashboard_path = self.visualizations_dir / "index.html"
        with open(main_dashboard_path, 'w') as f:
            f.write(dashboard_html)
        
        results["generated_files"].append(str(main_dashboard_path))
        logger.info(f"    ✅ Main dashboard saved: {main_dashboard_path}")
    
    def _create_quick_stats_html(self) -> str:
        """Create quick stats HTML"""
        if self.performance_data:
            perf_stats = self.performance_data.get('performance_statistics', {})
            benchmark_summary = self.performance_data.get('benchmark_summary', {})
            
            return f'''
            <div class="stat-card">
                <h4>Success Rate</h4>
                <div class="stat-value">{benchmark_summary.get('success_rate', 0) * 100:.1f}%</div>
            </div>
            <div class="stat-card">
                <h4>Avg Memory</h4>
                <div class="stat-value">{perf_stats.get('memory_usage_mb', {}).get('mean', 0):.1f}MB</div>
            </div>
            '''
        else:
            return '<p>No performance data available</p>'
    
    def _create_files_list_html(self, files: List[str]) -> str:
        """Create files list HTML"""
        if not files:
            return '<p>No visualization files generated yet.</p>'
        
        html = ""
        for file_path in files:
            file_name = Path(file_path).name
            html += f'''
            <div class="file-item">
                <a href="./{file_name}" target="_blank">📄 {file_name}</a>
            </div>
            '''
        
        return html
    
    def _get_base_css(self) -> str:
        """Get base CSS styles"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #f8f9fa;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #1f77b4;
        }
        .header h1 {
            color: #1f77b4;
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.2em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stat-card h3, .stat-card h4 {
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }
        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .file-list {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .file-item {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .file-item:last-child {
            border-bottom: none;
        }
        .file-item a {
            color: #1f77b4;
            text-decoration: none;
            font-weight: 500;
        }
        .file-item a:hover {
            text-decoration: underline;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        """


def main():
    """Main entry point for simple visualization"""
    print("=" * 80)
    print("SIMPLE METRICS VISUALIZER - Multi-Sensor Recording System")
    print("=" * 80)
    
    try:
        visualizer = SimpleMetricsVisualizer()
        results = visualizer.create_visualizations()
        
        print(f"✅ Generated {len(results['generated_files'])} visualization files:")
        for file_path in results['generated_files']:
            print(f"   📄 {file_path}")
        
        if results['errors']:
            print(f"\n⚠️  Encountered {len(results['errors'])} errors:")
            for error in results['errors']:
                print(f"   ❌ {error}")
        
        main_dashboard = visualizer.visualizations_dir / "index.html"
        if main_dashboard.exists():
            print(f"\n🌐 Main dashboard available at: {main_dashboard}")
            print("   Open this file in your web browser to view all visualizations")
        
        print("=" * 80)
        return results
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        return None


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results and results['generated_files'] else 1)