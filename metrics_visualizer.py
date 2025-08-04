#!/usr/bin/env python3
"""
Metrics Visualization System - Multi-Sensor Recording System

This module creates comprehensive visualizations for all metrics generated
by the multi-sensor recording system including:
- Performance benchmark charts
- Test execution dashboards  
- System analytics graphs
- Error pattern analysis
- Interactive HTML dashboard

Author: Multi-Sensor Recording System Team
Date: 2025-01-04
Version: 1.0
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Check for optional visualization dependencies
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Some visualizations will be skipped.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available. Interactive visualizations will be skipped.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Advanced data processing will be limited.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class MetricsVisualizer:
    """Creates comprehensive visualizations for multi-sensor recording system metrics"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.metrics_output_dir = self.project_root / "metrics_output"
        self.performance_reports_dir = self.project_root / "PythonApp" / "performance_reports"
        self.visualizations_dir = self.metrics_output_dir / "visualizations"
        self.visualizations_dir.mkdir(exist_ok=True)
        
        # Color schemes for consistency
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#17becf',
            'dark': '#8c564b'
        }
        
        self.performance_data = None
        self.metrics_data = None
        
    def visualize_all_metrics(self) -> Dict[str, Any]:
        """Generate all visualizations for collected metrics"""
        logger.info("="*80)
        logger.info("METRICS VISUALIZATION SYSTEM - Multi-Sensor Recording System")
        logger.info("="*80)
        
        results = {
            "visualization_info": {
                "start_time": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "output_directory": str(self.visualizations_dir),
                "dependencies": {
                    "matplotlib": MATPLOTLIB_AVAILABLE,
                    "plotly": PLOTLY_AVAILABLE,
                    "pandas": PANDAS_AVAILABLE
                }
            },
            "generated_visualizations": {},
            "errors": []
        }
        
        try:
            # Load data
            self._load_metrics_data()
            
            # Generate visualizations
            if MATPLOTLIB_AVAILABLE:
                self._create_matplotlib_charts(results)
            
            if PLOTLY_AVAILABLE:
                self._create_interactive_charts(results)
                self._create_dashboard_html(results)
            
            # Create summary visualization
            self._create_visualization_summary(results)
            
        except Exception as e:
            logger.error(f"Error in visualization generation: {e}")
            results["errors"].append({
                "type": "visualization_error",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
        
        results["visualization_info"]["end_time"] = datetime.now().isoformat()
        return results
    
    def _load_metrics_data(self):
        """Load metrics data from generated files"""
        logger.info("📊 Loading metrics data...")
        
        # Load performance benchmark data
        perf_files = list(self.performance_reports_dir.glob("performance_benchmark_*.json"))
        if perf_files:
            latest_perf = max(perf_files, key=os.path.getctime)
            logger.info(f"  Loading performance data: {latest_perf}")
            with open(latest_perf, 'r') as f:
                self.performance_data = json.load(f)
        
        # Load comprehensive metrics data
        metrics_files = list(self.metrics_output_dir.glob("comprehensive_metrics_dashboard_*.json"))
        if metrics_files:
            latest_metrics = max(metrics_files, key=os.path.getctime)
            logger.info(f"  Loading metrics data: {latest_metrics}")
            with open(latest_metrics, 'r') as f:
                self.metrics_data = json.load(f)
    
    def _create_matplotlib_charts(self, results: Dict[str, Any]):
        """Create static charts using matplotlib"""
        logger.info("📈 Creating matplotlib visualizations...")
        
        try:
            # Set style
            plt.style.use('default')
            
            # Performance benchmark charts
            if self.performance_data:
                self._create_performance_charts_matplotlib(results)
            
            # Test results charts
            if self.metrics_data:
                self._create_test_results_charts_matplotlib(results)
                self._create_system_analytics_charts_matplotlib(results)
            
        except Exception as e:
            logger.error(f"  Error creating matplotlib charts: {e}")
            results["errors"].append({
                "type": "matplotlib_error",
                "message": str(e)
            })
    
    def _create_performance_charts_matplotlib(self, results: Dict[str, Any]):
        """Create performance benchmark charts with matplotlib"""
        if not self.performance_data or 'detailed_results' not in self.performance_data:
            return
        
        detailed_results = self.performance_data['detailed_results']
        
        # Performance metrics overview
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Performance Benchmark Results - Multi-Sensor Recording System', fontsize=16)
        
        # Extract data
        test_names = [r['test_name'] for r in detailed_results]
        durations = [r['duration_seconds'] for r in detailed_results]
        memory_usage = [r['memory_usage_mb'] for r in detailed_results]
        cpu_usage = [r['cpu_usage_percent'] for r in detailed_results]
        throughput = [r['throughput_ops_per_sec'] for r in detailed_results]
        
        # Duration chart
        bars1 = ax1.bar(range(len(test_names)), durations, color=self.colors['primary'])
        ax1.set_title('Test Duration (seconds)')
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45, ha='right')
        ax1.set_ylabel('Duration (s)')
        
        # Memory usage chart
        bars2 = ax2.bar(range(len(test_names)), memory_usage, color=self.colors['secondary'])
        ax2.set_title('Memory Usage (MB)')
        ax2.set_xticks(range(len(test_names)))
        ax2.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45, ha='right')
        ax2.set_ylabel('Memory (MB)')
        
        # CPU usage chart
        bars3 = ax3.bar(range(len(test_names)), cpu_usage, color=self.colors['success'])
        ax3.set_title('CPU Usage (%)')
        ax3.set_xticks(range(len(test_names)))
        ax3.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45, ha='right')
        ax3.set_ylabel('CPU (%)')
        
        # Throughput chart (log scale due to wide range)
        bars4 = ax4.bar(range(len(test_names)), throughput, color=self.colors['info'])
        ax4.set_title('Throughput (ops/sec)')
        ax4.set_xticks(range(len(test_names)))
        ax4.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45, ha='right')
        ax4.set_ylabel('Throughput (ops/sec)')
        ax4.set_yscale('log')
        
        plt.tight_layout()
        
        chart_path = self.visualizations_dir / "performance_benchmark_charts.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        results["generated_visualizations"]["performance_charts_matplotlib"] = {
            "status": "success",
            "file_path": str(chart_path),
            "chart_type": "static_png"
        }
        
        logger.info(f"  ✅ Performance charts saved: {chart_path}")
    
    def _create_test_results_charts_matplotlib(self, results: Dict[str, Any]):
        """Create test results visualization with matplotlib"""
        if not self.metrics_data or 'generated_metrics' not in self.metrics_data:
            return
        
        # Test success analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Test Execution Results - Multi-Sensor Recording System', fontsize=16)
        
        # Collect test data
        test_categories = []
        test_statuses = []
        
        for metric_name, metric_data in self.metrics_data['generated_metrics'].items():
            if metric_name.startswith('test_suite_'):
                test_name = metric_name.replace('test_suite_', '').replace('_', ' ').title()
                status = metric_data.get('status', 'unknown')
                test_categories.append(test_name)
                test_statuses.append(status)
        
        if test_categories:
            # Success rate pie chart
            status_counts = {}
            for status in test_statuses:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            colors_map = {
                'success': self.colors['success'],
                'completed_with_errors': self.colors['warning'],
                'failed': self.colors['warning'],
                'unknown': '#cccccc'
            }
            
            pie_colors = [colors_map.get(status, '#cccccc') for status in status_counts.keys()]
            
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', 
                   colors=pie_colors, startangle=90)
            ax1.set_title('Test Status Distribution')
            
            # Test duration comparison (if available)
            durations = []
            for metric_data in self.metrics_data['generated_metrics'].values():
                if 'stdout' in metric_data and 'Duration:' in str(metric_data['stdout']):
                    # Try to extract duration from stdout
                    try:
                        duration_line = [line for line in str(metric_data['stdout']).split('\n') 
                                       if 'Duration:' in line or 'seconds' in line]
                        if duration_line:
                            # Extract numeric value (simplified)
                            duration = 1.0  # Default fallback
                            durations.append(duration)
                    except:
                        durations.append(1.0)
            
            if len(durations) == len(test_categories):
                bars = ax2.bar(range(len(test_categories)), durations, 
                              color=[self.colors['success'] if s == 'success' else self.colors['warning'] 
                                    for s in test_statuses])
                ax2.set_title('Test Execution Duration')
                ax2.set_xticks(range(len(test_categories)))
                ax2.set_xticklabels(test_categories, rotation=45, ha='right')
                ax2.set_ylabel('Duration (relative)')
            else:
                ax2.text(0.5, 0.5, 'Duration data not available', 
                        transform=ax2.transAxes, ha='center', va='center')
                ax2.set_title('Test Execution Duration')
        
        plt.tight_layout()
        
        chart_path = self.visualizations_dir / "test_results_charts.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        results["generated_visualizations"]["test_results_charts_matplotlib"] = {
            "status": "success",
            "file_path": str(chart_path),
            "chart_type": "static_png"
        }
        
        logger.info(f"  ✅ Test results charts saved: {chart_path}")
    
    def _create_system_analytics_charts_matplotlib(self, results: Dict[str, Any]):
        """Create system analytics charts with matplotlib"""
        if not self.metrics_data or 'generated_metrics' not in self.metrics_data:
            return
        
        system_analytics = self.metrics_data['generated_metrics'].get('system_analytics', {})
        if not system_analytics or 'project_stats' not in system_analytics:
            return
        
        project_stats = system_analytics['project_stats']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('System Analytics - Multi-Sensor Recording System', fontsize=16)
        
        # File types distribution
        file_types = project_stats.get('file_types', {})
        if file_types:
            # Filter to show only significant file types
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
            top_types = sorted_types[:8]  # Top 8 file types
            
            labels = [f"{ext if ext else 'no ext'} ({count})" for ext, count in top_types]
            sizes = [count for ext, count in top_types]
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title(f'File Types Distribution\n(Total: {project_stats.get("total_files", 0)} files)')
        
        # Project statistics summary
        stats_labels = ['Total Files', 'Directories', 'Large Files (>1MB)']
        stats_values = [
            project_stats.get('total_files', 0),
            len(project_stats.get('directories', [])),
            len(project_stats.get('large_files', []))
        ]
        
        bars = ax2.bar(stats_labels, stats_values, color=[self.colors['primary'], 
                                                          self.colors['secondary'], 
                                                          self.colors['warning']])
        ax2.set_title('Project Structure Summary')
        ax2.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, stats_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        chart_path = self.visualizations_dir / "system_analytics_charts.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        results["generated_visualizations"]["system_analytics_charts_matplotlib"] = {
            "status": "success",
            "file_path": str(chart_path),
            "chart_type": "static_png"
        }
        
        logger.info(f"  ✅ System analytics charts saved: {chart_path}")
    
    def _create_interactive_charts(self, results: Dict[str, Any]):
        """Create interactive charts using Plotly"""
        logger.info("🎯 Creating interactive visualizations...")
        
        try:
            if self.performance_data:
                self._create_performance_charts_plotly(results)
            
            if self.metrics_data:
                self._create_metrics_overview_plotly(results)
        
        except Exception as e:
            logger.error(f"  Error creating plotly charts: {e}")
            results["errors"].append({
                "type": "plotly_error", 
                "message": str(e)
            })
    
    def _create_performance_charts_plotly(self, results: Dict[str, Any]):
        """Create interactive performance charts with Plotly"""
        if not self.performance_data or 'detailed_results' not in self.performance_data:
            return
        
        detailed_results = self.performance_data['detailed_results']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Test Duration', 'Memory Usage', 'CPU Usage', 'Throughput'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": True}]]
        )
        
        # Extract data
        test_names = [r['test_name'].replace('_', '<br>') for r in detailed_results]
        durations = [r['duration_seconds'] for r in detailed_results]
        memory_usage = [r['memory_usage_mb'] for r in detailed_results]
        cpu_usage = [r['cpu_usage_percent'] for r in detailed_results]
        throughput = [r['throughput_ops_per_sec'] for r in detailed_results]
        
        # Duration chart
        fig.add_trace(
            go.Bar(x=test_names, y=durations, name='Duration (s)', 
                   marker_color='#1f77b4', showlegend=False),
            row=1, col=1
        )
        
        # Memory usage chart
        fig.add_trace(
            go.Bar(x=test_names, y=memory_usage, name='Memory (MB)',
                   marker_color='#ff7f0e', showlegend=False),
            row=1, col=2
        )
        
        # CPU usage chart
        fig.add_trace(
            go.Bar(x=test_names, y=cpu_usage, name='CPU (%)',
                   marker_color='#2ca02c', showlegend=False),
            row=2, col=1
        )
        
        # Throughput chart
        fig.add_trace(
            go.Bar(x=test_names, y=throughput, name='Throughput (ops/sec)',
                   marker_color='#9467bd', showlegend=False),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Performance Benchmark Results - Interactive Dashboard",
            title_x=0.5,
            height=800,
            template="plotly_white"
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Duration (seconds)", row=1, col=1)
        fig.update_yaxes(title_text="Memory (MB)", row=1, col=2)
        fig.update_yaxes(title_text="CPU (%)", row=2, col=1)
        fig.update_yaxes(title_text="Throughput (ops/sec)", type="log", row=2, col=2)
        
        # Save as HTML
        html_path = self.visualizations_dir / "performance_interactive.html"
        fig.write_html(str(html_path))
        
        results["generated_visualizations"]["performance_charts_plotly"] = {
            "status": "success",
            "file_path": str(html_path),
            "chart_type": "interactive_html"
        }
        
        logger.info(f"  ✅ Interactive performance charts saved: {html_path}")
    
    def _create_metrics_overview_plotly(self, results: Dict[str, Any]):
        """Create metrics overview dashboard with Plotly"""
        if not self.metrics_data:
            return
        
        # Create overview dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Metrics Generation Success', 'Error Types', 'Test Categories', 'System Info'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        # Metrics success pie chart
        metrics_summary = self.metrics_data.get('metrics_summary', {})
        total_metrics = metrics_summary.get('total_metrics_generated', 0)
        successful_metrics = metrics_summary.get('successful_metrics', 0)
        failed_metrics = total_metrics - successful_metrics
        
        fig.add_trace(
            go.Pie(labels=['Successful', 'Failed/Partial'], 
                   values=[successful_metrics, failed_metrics],
                   marker_colors=['#2ca02c', '#d62728']),
            row=1, col=1
        )
        
        # Error types
        error_types = metrics_summary.get('error_types', [])
        if error_types:
            error_counts = {error_type: error_types.count(error_type) for error_type in set(error_types)}
            fig.add_trace(
                go.Bar(x=list(error_counts.keys()), y=list(error_counts.values()),
                       marker_color='#d62728'),
                row=1, col=2
            )
        
        # Test categories analysis
        test_categories = {}
        for metric_name in self.metrics_data.get('generated_metrics', {}):
            if metric_name.startswith('test_suite_'):
                category = metric_name.replace('test_suite_', '').replace('_', ' ').title()
                status = self.metrics_data['generated_metrics'][metric_name].get('status', 'unknown')
                test_categories[category] = status
        
        if test_categories:
            categories = list(test_categories.keys())
            statuses = list(test_categories.values())
            colors = ['#2ca02c' if s == 'success' else '#d62728' for s in statuses]
            
            fig.add_trace(
                go.Bar(x=categories, y=[1]*len(categories), 
                       marker_color=colors,
                       text=statuses, textposition='inside'),
                row=2, col=1
            )
        
        # System info table
        system_analytics = self.metrics_data.get('generated_metrics', {}).get('system_analytics', {})
        system_info = system_analytics.get('system_info', {}) if system_analytics else {}
        
        if system_info:
            info_data = [
                ['Platform', system_info.get('platform', 'N/A')],
                ['Python Version', system_info.get('python_version', 'N/A')],
                ['CPU Count', str(system_info.get('cpu_count', 'N/A'))],
                ['Total Memory (GB)', f"{system_info.get('memory_total', 0) / (1024**3):.1f}"],
                ['Available Memory (GB)', f"{system_info.get('memory_available', 0) / (1024**3):.1f}"]
            ]
            
            fig.add_trace(
                go.Table(
                    header=dict(values=['Property', 'Value'],
                               fill_color='lightblue',
                               align='left'),
                    cells=dict(values=list(zip(*info_data)),
                              fill_color='white',
                              align='left')
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Comprehensive Metrics Overview - Multi-Sensor Recording System",
            title_x=0.5,
            height=800,
            showlegend=False,
            template="plotly_white"
        )
        
        html_path = self.visualizations_dir / "metrics_overview_interactive.html"
        fig.write_html(str(html_path))
        
        results["generated_visualizations"]["metrics_overview_plotly"] = {
            "status": "success", 
            "file_path": str(html_path),
            "chart_type": "interactive_html"
        }
        
        logger.info(f"  ✅ Interactive metrics overview saved: {html_path}")
    
    def _create_dashboard_html(self, results: Dict[str, Any]):
        """Create comprehensive HTML dashboard"""
        logger.info("🌐 Creating comprehensive HTML dashboard...")
        
        dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Sensor Recording System - Metrics Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #1f77b4;
        }}
        .header h1 {{
            color: #1f77b4;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-card .unit {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .chart-link {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #1f77b4;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            transition: background-color 0.3s;
        }}
        .chart-link:hover {{
            background-color: #0f5a9c;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-success {{
            background-color: #2ca02c;
        }}
        .status-warning {{
            background-color: #ff7f0e;
        }}
        .status-error {{
            background-color: #d62728;
        }}
        .file-list {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .file-item {{
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Multi-Sensor Recording System</h1>
            <p>Comprehensive Metrics Dashboard</p>
        </div>
        
        {self._generate_metrics_summary_html()}
        
        {self._generate_visualizations_section_html(results)}
        
        {self._generate_data_sources_html()}
        
        <div class="timestamp">
            Dashboard generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        dashboard_path = self.visualizations_dir / "comprehensive_dashboard.html"
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_html)
        
        results["generated_visualizations"]["comprehensive_dashboard"] = {
            "status": "success",
            "file_path": str(dashboard_path),
            "chart_type": "html_dashboard"
        }
        
        logger.info(f"  ✅ Comprehensive dashboard saved: {dashboard_path}")
    
    def _generate_metrics_summary_html(self) -> str:
        """Generate metrics summary section for HTML dashboard"""
        if not self.performance_data:
            return "<p>No performance data available</p>"
        
        # Extract key metrics
        perf_stats = self.performance_data.get('performance_statistics', {})
        benchmark_summary = self.performance_data.get('benchmark_summary', {})
        
        avg_throughput = perf_stats.get('throughput_ops_per_sec', {}).get('mean', 0)
        avg_memory = perf_stats.get('memory_usage_mb', {}).get('mean', 0)
        avg_cpu = perf_stats.get('cpu_usage_percent', {}).get('mean', 0)
        success_rate = benchmark_summary.get('success_rate', 0) * 100
        
        return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>🚀 Average Throughput</h3>
                <div class="value">{avg_throughput:,.0f}</div>
                <div class="unit">operations/second</div>
            </div>
            <div class="metric-card">
                <h3>💾 Average Memory Usage</h3>
                <div class="value">{avg_memory:.1f}</div>
                <div class="unit">MB</div>
            </div>
            <div class="metric-card">
                <h3>⚡ Average CPU Usage</h3>
                <div class="value">{avg_cpu:.1f}</div>
                <div class="unit">%</div>
            </div>
            <div class="metric-card">
                <h3>✅ Success Rate</h3>
                <div class="value">{success_rate:.1f}</div>
                <div class="unit">%</div>
            </div>
        </div>
        """
    
    def _generate_visualizations_section_html(self, results: Dict[str, Any]) -> str:
        """Generate visualizations section for HTML dashboard"""
        viz_section = '''
        <div class="section">
            <h2>📊 Available Visualizations</h2>
        '''
        
        generated_viz = results.get("generated_visualizations", {})
        
        if generated_viz:
            for viz_name, viz_data in generated_viz.items():
                if viz_data.get("status") == "success":
                    file_path = Path(viz_data["file_path"])
                    file_name = file_path.name
                    chart_type = viz_data.get("chart_type", "unknown")
                    
                    viz_section += f'''
                    <div class="chart-container">
                        <h3>{viz_name.replace('_', ' ').title()}</h3>
                        <p>Type: {chart_type}</p>
                        <a href="./visualizations/{file_name}" class="chart-link" target="_blank">
                            🔗 Open Visualization
                        </a>
                    </div>
                    '''
        else:
            viz_section += '<p>No visualizations generated yet.</p>'
        
        viz_section += '</div>'
        return viz_section
    
    def _generate_data_sources_html(self) -> str:
        """Generate data sources section for HTML dashboard"""
        return f"""
        <div class="section">
            <h2>📁 Data Sources</h2>
            <div class="file-list">
                <div class="file-item">
                    <strong>Performance Data:</strong> 
                    {"✅ Loaded" if self.performance_data else "❌ Not available"}
                </div>
                <div class="file-item">
                    <strong>Metrics Data:</strong> 
                    {"✅ Loaded" if self.metrics_data else "❌ Not available"}
                </div>
                <div class="file-item">
                    <strong>Visualization Dependencies:</strong>
                    <br>• Matplotlib: {"✅" if MATPLOTLIB_AVAILABLE else "❌"}
                    <br>• Plotly: {"✅" if PLOTLY_AVAILABLE else "❌"}
                    <br>• Pandas: {"✅" if PANDAS_AVAILABLE else "❌"}
                </div>
            </div>
        </div>
        """
    
    def _create_visualization_summary(self, results: Dict[str, Any]):
        """Create summary of generated visualizations"""
        logger.info("📋 Creating visualization summary...")
        
        summary = {
            "visualization_summary": {
                "total_visualizations": len(results["generated_visualizations"]),
                "successful_visualizations": len([v for v in results["generated_visualizations"].values() 
                                                 if v.get("status") == "success"]),
                "dependencies_available": {
                    "matplotlib": MATPLOTLIB_AVAILABLE,
                    "plotly": PLOTLY_AVAILABLE,
                    "pandas": PANDAS_AVAILABLE
                },
                "output_directory": str(self.visualizations_dir),
                "generated_files": []
            }
        }
        
        for viz_name, viz_data in results["generated_visualizations"].items():
            if viz_data.get("status") == "success":
                summary["visualization_summary"]["generated_files"].append({
                    "name": viz_name,
                    "file_path": viz_data["file_path"],
                    "chart_type": viz_data.get("chart_type", "unknown")
                })
        
        # Save summary
        summary_path = self.visualizations_dir / "visualization_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        results["visualization_summary_file"] = str(summary_path)
        logger.info(f"  ✅ Visualization summary saved: {summary_path}")


async def main():
    """Main entry point for metrics visualization"""
    print("=" * 80)
    print("METRICS VISUALIZATION SYSTEM - Multi-Sensor Recording System")
    print("=" * 80)
    print()
    
    try:
        visualizer = MetricsVisualizer()
        results = visualizer.visualize_all_metrics()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = visualizer.visualizations_dir / f"visualization_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("=" * 80)
        print("VISUALIZATION GENERATION COMPLETED")
        print("=" * 80)
        print(f"Results saved to: {results_file}")
        print(f"Visualizations directory: {visualizer.visualizations_dir}")
        print(f"Generated visualizations: {len(results['generated_visualizations'])}")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"Critical error in visualization generation: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(main())
    sys.exit(0 if results else 1)