#!/usr/bin/env python3
"""
Content Comparison Tool for Markdown and LaTeX Files

This script compares the content between corresponding .md and .tex files in the
thesis_report/final directory, accounting for format-specific differences while
identifying actual content discrepancies.

Usage:
    python compare_md_tex.py [--verbose] [--file-pattern PATTERN]

Author: Academic Writing and Documentation System
"""

import argparse
import difflib
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ContentNormalizer:
    """Normalizes content from both Markdown and LaTeX formats for comparison."""
    
    def __init__(self):
        # Patterns for normalization
        self.latex_patterns = [
            # LaTeX commands
            (r'\\chapter\{([^}]+)\}', r'\1'),
            (r'\\section\{([^}]+)\}', r'\1'),
            (r'\\subsection\{([^}]+)\}', r'\1'),
            (r'\\subsubsection\{([^}]+)\}', r'\1'),
            (r'\\textbf\{([^}]+)\}', r'\1'),
            (r'\\textit\{([^}]+)\}', r'\1'),
            (r'\\emph\{([^}]+)\}', r'\1'),
            (r'\\textemdash', r'—'),
            (r'\\citep\{([^}]+)\}', r'[\1]'),
            (r'\\cite\{([^}]+)\}', r'[\1]'),
            (r'\\citet\{([^}]+)\}', r'[\1]'),
            # LaTeX environments
            (r'\\begin\{itemize\}', r''),
            (r'\\end\{itemize\}', r''),
            (r'\\begin\{enumerate\}', r''),
            (r'\\end\{enumerate\}', r''),
            (r'\\begin\{verbatim\}', r''),
            (r'\\end\{verbatim\}', r''),
            (r'\\item', r'-'),
            # Comments and metadata
            (r'%.*$', r'', re.MULTILINE),
            # TODO comments
            (r'% TODO:.*$', r'', re.MULTILINE),
            # Common LaTeX spacing
            (r'\\\\', r'\n'),
            (r'\\newline', r'\n'),
        ]
        
        self.markdown_patterns = [
            # Markdown headers
            (r'^#{1,6}\s*(.+)$', r'\1', re.MULTILINE),
            # Bold and italic
            (r'\*\*([^*]+)\*\*', r'\1'),
            (r'\*([^*]+)\*', r'\1'),
            (r'__([^_]+)__', r'\1'),
            (r'_([^_]+)_', r'\1'),
            # Citations
            (r'\[(\d+)\]', r'[\1]'),
            # Lists
            (r'^[-*+]\s+', r'- ', re.MULTILINE),
        ]
    
    def normalize_latex(self, content: str) -> str:
        """Normalize LaTeX content for comparison."""
        normalized = content
        
        for pattern, replacement, *flags in self.latex_patterns:
            flag = flags[0] if flags else 0
            normalized = re.sub(pattern, replacement, normalized, flags=flag)
        
        return self._clean_whitespace(normalized)
    
    def normalize_markdown(self, content: str) -> str:
        """Normalize Markdown content for comparison."""
        normalized = content
        
        for pattern, replacement, *flags in self.markdown_patterns:
            flag = flags[0] if flags else 0
            normalized = re.sub(pattern, replacement, normalized, flags=flag)
        
        return self._clean_whitespace(normalized)
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up whitespace and normalize line breaks."""
        # First preserve actual line structure, then clean excess whitespace within lines
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Clean excess whitespace within the line but preserve structure
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
        
        # Join and normalize excessive blank lines
        content = '\n'.join(cleaned_lines)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return content.strip()


class FileMapper:
    """Maps corresponding .md and .tex files."""
    
    @staticmethod
    def get_file_pairs(base_dir: Path) -> List[Tuple[Path, Path]]:
        """Get pairs of corresponding .md and .tex files."""
        pairs = []
        
        # Main chapters (1.md -> 1.tex, etc.)
        for i in range(1, 7):  # Chapters 1-6
            md_file = base_dir / f"{i}.md"
            tex_file = base_dir / "latex" / f"{i}.tex"
            if md_file.exists() and tex_file.exists():
                pairs.append((md_file, tex_file))
        
        # Appendices (appendix_a_system_manual.md -> appendix_A.tex, etc.)
        appendix_mapping = {
            'appendix_a_system_manual.md': 'appendix_A.tex',
            'appendix_b_user_manual.md': 'appendix_B.tex',
            'appendix_c_supporting_documentation.md': 'appendix_C.tex',
            'appendix_d_test_reports.md': 'appendix_D.tex',
            'appendix_e_evaluation_data.md': 'appendix_E.tex',
            'appendix_f_code_listings.md': 'appendix_F.tex',
            'appendix_g_diagnostic_figures.md': 'appendix_G.tex',
            'appendix_h_reference_index.md': 'appendix_H.tex',
            'appendix_i_figures_and_diagrams.md': 'appendix_I.tex',
            'appendix_z_consolidated_figures.md': 'appendix_Z.tex',
        }
        
        for md_name, tex_name in appendix_mapping.items():
            md_file = base_dir / md_name
            tex_file = base_dir / "latex" / tex_name
            if md_file.exists() and tex_file.exists():
                pairs.append((md_file, tex_file))
        
        return pairs


class ContentComparator:
    """Compares normalized content between files."""
    
    def __init__(self, normalizer: ContentNormalizer, verbose: bool = False):
        self.normalizer = normalizer
        self.verbose = verbose
    
    def compare_files(self, md_file: Path, tex_file: Path) -> Dict:
        """Compare content between a Markdown and LaTeX file."""
        try:
            # Read files
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()
            
            # Normalize content
            normalized_md = self.normalizer.normalize_markdown(md_content)
            normalized_tex = self.normalizer.normalize_latex(tex_content)
            
            # Compare
            similarity = self._calculate_similarity(normalized_md, normalized_tex)
            differences = self._get_differences(normalized_md, normalized_tex)
            
            result = {
                'md_file': str(md_file),
                'tex_file': str(tex_file),
                'similarity': similarity,
                'has_differences': len(differences) > 0,
                'differences': differences,
                'md_length': len(normalized_md),
                'tex_length': len(normalized_tex),
            }
            
            if self.verbose:
                result['normalized_md'] = normalized_md
                result['normalized_tex'] = normalized_tex
            
            return result
            
        except Exception as e:
            return {
                'md_file': str(md_file),
                'tex_file': str(tex_file),
                'error': str(e),
                'similarity': 0.0,
                'has_differences': True,
                'differences': [f"Error reading files: {e}"],
                'md_length': 0,
                'tex_length': 0,
            }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        seq_matcher = difflib.SequenceMatcher(None, text1, text2)
        return seq_matcher.ratio()
    
    def _get_differences(self, text1: str, text2: str) -> List[str]:
        """Get detailed differences between two texts."""
        differences = []
        
        # Line-by-line comparison
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        differ = difflib.unified_diff(
            lines1, lines2,
            fromfile='markdown', tofile='latex',
            lineterm='', n=3
        )
        
        diff_lines = list(differ)
        if len(diff_lines) > 0:
            differences.extend(diff_lines)
        
        return differences


def print_comparison_report(results: List[Dict], verbose: bool = False):
    """Print a formatted comparison report."""
    print("=" * 80)
    print("CONTENT COMPARISON REPORT: Markdown vs LaTeX Files")
    print("=" * 80)
    print()
    
    total_files = len(results)
    files_with_differences = sum(1 for r in results if r.get('has_differences', True))
    files_with_errors = sum(1 for r in results if 'error' in r)
    
    # Categorize files by similarity level
    high_similarity = sum(1 for r in results if r.get('similarity', 0) > 0.95 and not r.get('error'))
    medium_similarity = sum(1 for r in results if 0.85 <= r.get('similarity', 0) <= 0.95 and not r.get('error'))
    low_similarity = sum(1 for r in results if r.get('similarity', 0) < 0.85 and not r.get('error'))
    
    print(f"Summary:")
    print(f"  Total file pairs: {total_files}")
    print(f"  Files with differences: {files_with_differences}")
    print(f"  Files with errors: {files_with_errors}")
    print(f"  Files in sync: {total_files - files_with_differences}")
    print()
    print(f"Similarity distribution:")
    print(f"  High similarity (>95%): {high_similarity}")
    print(f"  Medium similarity (85-95%): {medium_similarity}")
    print(f"  Low similarity (<85%): {low_similarity}")
    print()
    
    # Identify files that might need attention
    critical_files = [r for r in results if r.get('similarity', 0) < 0.5 or 'error' in r]
    if critical_files:
        print(f"⚠️  FILES REQUIRING IMMEDIATE ATTENTION:")
        for result in critical_files:
            md_name = Path(result['md_file']).name
            tex_name = Path(result['tex_file']).name
            if 'error' in result:
                print(f"  🔴 {md_name} ↔ {tex_name}: ERROR - {result['error']}")
            else:
                similarity = result.get('similarity', 0)
                print(f"  🔴 {md_name} ↔ {tex_name}: Very low similarity ({similarity:.1%})")
        print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {Path(result['md_file']).name} ↔ {Path(result['tex_file']).name}")
        
        if 'error' in result:
            print(f"   ERROR: {result['error']}")
        else:
            similarity = result['similarity']
            status_icon = "🔴" if similarity < 0.5 else "🟡" if similarity < 0.95 else "✅"
            print(f"   Similarity: {similarity:.2%} {status_icon}")
            print(f"   Content lengths: MD={result['md_length']}, LaTeX={result['tex_length']}")
            
            length_diff = abs(result['md_length'] - result['tex_length'])
            length_ratio = length_diff / max(result['md_length'], result['tex_length']) if max(result['md_length'], result['tex_length']) > 0 else 0
            
            if result['has_differences']:
                if length_ratio > 0.3:
                    print(f"   📏 Significant length difference: {length_ratio:.1%}")
                print(f"   ⚠️  CONTENT DIFFERENCES DETECTED")
                if verbose and result['differences']:
                    print("   Differences:")
                    for diff_line in result['differences'][:10]:  # Limit output
                        print(f"     {diff_line}")
                    if len(result['differences']) > 10:
                        print(f"     ... and {len(result['differences']) - 10} more lines")
            else:
                print(f"   ✅ Content is synchronized")
        
        print()


def main():
    parser = argparse.ArgumentParser(description="Compare content between .md and .tex files")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed differences')
    parser.add_argument('--file-pattern', '-p', default='*',
                        help='Pattern to match specific files')
    parser.add_argument('--base-dir', '-d', 
                        default=Path(__file__).parent,
                        help='Base directory containing the files')
    parser.add_argument('--html-report', action='store_true',
                        help='Generate HTML report in addition to console output')
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} does not exist")
        sys.exit(1)
    
    # Get file pairs
    file_pairs = FileMapper.get_file_pairs(base_dir)
    
    if not file_pairs:
        print("No corresponding .md and .tex file pairs found")
        sys.exit(1)
    
    # Filter by pattern if specified
    if args.file_pattern != '*':
        filtered_pairs = []
        for md_file, tex_file in file_pairs:
            if args.file_pattern in md_file.name or args.file_pattern in tex_file.name:
                filtered_pairs.append((md_file, tex_file))
        file_pairs = filtered_pairs
    
    if not file_pairs:
        print(f"No file pairs match pattern: {args.file_pattern}")
        sys.exit(1)
    
    # Compare files
    normalizer = ContentNormalizer()
    comparator = ContentComparator(normalizer, args.verbose)
    
    results = []
    for md_file, tex_file in file_pairs:
        result = comparator.compare_files(md_file, tex_file)
        results.append(result)
    
    # Print console report
    print_comparison_report(results, args.verbose)
    
    # Generate HTML report if requested
    if args.html_report:
        html_output = generate_html_report(results)
        html_file = base_dir / "comparison_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"\n📄 HTML report generated: {html_file}")
    
    # Exit with error code if differences found
    if any(r.get('has_differences', True) for r in results):
        sys.exit(1)
    else:
        print("All files are synchronized! ✅")
        sys.exit(0)


def generate_html_report(results: List[Dict]) -> str:
    """Generate an HTML report of the comparison results."""
    
    total_files = len(results)
    files_with_differences = sum(1 for r in results if r.get('has_differences', True))
    files_with_errors = sum(1 for r in results if 'error' in r)
    
    # Categorize files by similarity level
    high_similarity = sum(1 for r in results if r.get('similarity', 0) > 0.95 and not r.get('error'))
    medium_similarity = sum(1 for r in results if 0.85 <= r.get('similarity', 0) <= 0.95 and not r.get('error'))
    low_similarity = sum(1 for r in results if r.get('similarity', 0) < 0.85 and not r.get('error'))
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Comparison Report: Markdown vs LaTeX</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #495057; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .file-grid {{ display: grid; gap: 20px; }}
        .file-card {{ background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; }}
        .file-card.high {{ border-left: 4px solid #28a745; }}
        .file-card.medium {{ border-left: 4px solid #ffc107; }}
        .file-card.low {{ border-left: 4px solid #dc3545; }}
        .file-card.error {{ border-left: 4px solid #6f42c1; }}
        .file-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .file-title {{ font-size: 1.1em; font-weight: bold; }}
        .similarity-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
        .similarity-high {{ background: #d4edda; color: #155724; }}
        .similarity-medium {{ background: #fff3cd; color: #856404; }}
        .similarity-low {{ background: #f8d7da; color: #721c24; }}
        .file-details {{ font-size: 0.9em; color: #6c757d; }}
        .critical-section {{ background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 15px; margin-bottom: 30px; }}
        .critical-section h3 {{ color: #721c24; margin-top: 0; }}
        .critical-item {{ margin: 5px 0; }}
        .icon {{ margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Content Comparison Report</h1>
        <p><strong>Markdown vs LaTeX Files</strong> • Generated: {Path(__file__).parent}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Files</h3>
            <div class="number">{total_files}</div>
        </div>
        <div class="summary-card">
            <h3>High Similarity</h3>
            <div class="number" style="color: #28a745;">{high_similarity}</div>
            <small>>95%</small>
        </div>
        <div class="summary-card">
            <h3>Medium Similarity</h3>
            <div class="number" style="color: #ffc107;">{medium_similarity}</div>
            <small>85-95%</small>
        </div>
        <div class="summary-card">
            <h3>Low Similarity</h3>
            <div class="number" style="color: #dc3545;">{low_similarity}</div>
            <small>&lt;85%</small>
        </div>
    </div>
"""
    
    # Critical files section
    critical_files = [r for r in results if r.get('similarity', 0) < 0.5 or 'error' in r]
    if critical_files:
        html += """
    <div class="critical-section">
        <h3>⚠️ Files Requiring Immediate Attention</h3>
"""
        for result in critical_files:
            md_name = Path(result['md_file']).name
            tex_name = Path(result['tex_file']).name
            if 'error' in result:
                html += f'        <div class="critical-item">🔴 <strong>{md_name} ↔ {tex_name}</strong>: ERROR - {result["error"]}</div>\n'
            else:
                similarity = result.get('similarity', 0)
                html += f'        <div class="critical-item">🔴 <strong>{md_name} ↔ {tex_name}</strong>: Very low similarity ({similarity:.1%})</div>\n'
        html += "    </div>\n"
    
    # File details
    html += '    <div class="file-grid">\n'
    
    for i, result in enumerate(results, 1):
        md_name = Path(result['md_file']).name
        tex_name = Path(result['tex_file']).name
        
        if 'error' in result:
            card_class = "error"
            badge_class = "similarity-low"
            badge_text = "ERROR"
            similarity_text = "N/A"
        else:
            similarity = result['similarity']
            if similarity > 0.95:
                card_class = "high"
                badge_class = "similarity-high"
            elif similarity >= 0.85:
                card_class = "medium"
                badge_class = "similarity-medium"
            else:
                card_class = "low"
                badge_class = "similarity-low"
            
            badge_text = f"{similarity:.1%}"
            similarity_text = f"{similarity:.2%}"
        
        status_icon = "🔴" if result.get('similarity', 0) < 0.5 or 'error' in result else "🟡" if result.get('similarity', 0) < 0.95 else "✅"
        
        html += f"""        <div class="file-card {card_class}">
            <div class="file-header">
                <div class="file-title">{status_icon} {md_name} ↔ {tex_name}</div>
                <div class="similarity-badge {badge_class}">{badge_text}</div>
            </div>
            <div class="file-details">
"""
        
        if 'error' in result:
            html += f"                <div>❌ Error: {result['error']}</div>\n"
        else:
            html += f"                <div>📊 Similarity: {similarity_text}</div>\n"
            html += f"                <div>📏 Lengths: MD={result['md_length']:,}, LaTeX={result['tex_length']:,}</div>\n"
            
            length_diff = abs(result['md_length'] - result['tex_length'])
            length_ratio = length_diff / max(result['md_length'], result['tex_length']) if max(result['md_length'], result['tex_length']) > 0 else 0
            
            if length_ratio > 0.3:
                html += f"                <div>⚠️ Significant length difference: {length_ratio:.1%}</div>\n"
            
            if result['has_differences']:
                html += "                <div>⚠️ Content differences detected</div>\n"
            else:
                html += "                <div>✅ Content synchronized</div>\n"
        
        html += """            </div>
        </div>
"""
    
    html += """    </div>
    
    <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #6c757d;">
        <p><strong>Note:</strong> This report compares normalized content between Markdown and LaTeX files. 
        Minor formatting differences are expected and do not indicate content synchronization issues.</p>
        <p><strong>Tool:</strong> <code>compare_md_tex.py</code> - Content Comparison Tool for Academic Documentation</p>
    </div>
</body>
</html>"""
    
    return html


if __name__ == '__main__':
    main()