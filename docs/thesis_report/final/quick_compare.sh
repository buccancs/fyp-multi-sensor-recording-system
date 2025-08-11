#!/bin/bash
# Quick comparison script for thesis documentation
# Usage: ./quick_compare.sh [pattern]

set -e

cd "$(dirname "$0")"

echo "🔍 Running content comparison between .md and .tex files..."
echo "📂 Working directory: $(pwd)"
echo

if [ $# -eq 0 ]; then
    echo "📊 Comparing all files..."
    python compare_md_tex.py --html-report
else
    echo "📊 Comparing files matching pattern: $1"
    python compare_md_tex.py --file-pattern "$1" --verbose
fi

echo
echo "✅ Comparison completed!"

# If HTML report was generated, show its location
if [ -f "comparison_report.html" ]; then
    echo "📄 HTML report available at: $(pwd)/comparison_report.html"
fi