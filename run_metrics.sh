#!/bin/bash
# Quick Metrics Generation Script - Multi-Sensor Recording System
# Usage: ./run_metrics.sh

echo "🚀 Starting Comprehensive Metrics Generation..."
echo "=================================================="

# Ensure we're in the project root
if [ ! -f "generate_all_metrics.py" ]; then
    echo "❌ Error: Must be run from project root directory"
    exit 1
fi

# Check Python availability
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    exit 1
fi

# Install required dependencies
echo "📦 Installing required dependencies..."
pip install --user psutil 2>/dev/null || echo "⚠️  psutil already installed or installation failed"

# Run comprehensive metrics generation
echo ""
echo "📊 Running comprehensive metrics generation..."
python generate_all_metrics.py

# Check if metrics were generated successfully
if [ $? -eq 0 ] || [ $? -eq 1 ]; then
    echo ""
    echo "✅ Metrics generation completed!"
    echo ""
    echo "📈 Generated Reports:"
    echo "  • metrics_output/comprehensive_metrics_dashboard_*.json"
    echo "  • metrics_output/comprehensive_metrics_report_*.md"
    echo "  • PythonApp/performance_reports/performance_benchmark_*.json"
    echo "  • PythonApp/test_results/ (various test reports)"
    echo ""
    echo "📋 Quick Access:"
    echo "  • Main Summary: cat METRICS_GENERATION_SUMMARY.md"
    echo "  • Latest Report: ls -la metrics_output/*.md | tail -1"
    echo "  • Performance: cat PythonApp/performance_reports/performance_summary_*.txt"
    echo ""
    echo "🔄 To regenerate metrics: ./run_metrics.sh"
else
    echo "❌ Metrics generation failed with exit code $?"
    exit 1
fi