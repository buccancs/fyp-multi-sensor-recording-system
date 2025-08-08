import ast
import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
@dataclass
class ComplexityAnalysis:
    file_path: str
    function_name: str
    line_number: int
    complexity_score: int
    type: str
    needs_docs: bool
    current_docs: str
    suggested_docs: str
    reasoning: List[str]
class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.results: List[ComplexityAnalysis] = []
        self.current_class = None
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        complexity = self._calculate_complexity(node)
        needs_docs = self._needs_documentation(node, complexity)
        current_docs = ast.get_docstring(node) or ""
        suggested_docs = self._generate_docstring(node, complexity) if needs_docs else ""
        reasoning = self._get_complexity_reasons(node, complexity)
        analysis = ComplexityAnalysis(
            file_path=self.file_path,
            function_name=node.name,
            line_number=node.lineno,
            complexity_score=complexity,
            type='method' if self.current_class else 'function',
            needs_docs=needs_docs,
            current_docs=current_docs,
            suggested_docs=suggested_docs,
            reasoning=reasoning
        )
        self.results.append(analysis)
        self.generic_visit(node)
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name
        complexity = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.With))])
        needs_docs = not ast.get_docstring(node) and complexity > 5
        if needs_docs:
            analysis = ComplexityAnalysis(
                file_path=self.file_path,
                function_name=node.name,
                line_number=node.lineno,
                complexity_score=complexity,
                type='class',
                needs_docs=needs_docs,
                current_docs=ast.get_docstring(node) or "",
                suggested_docs=self._generate_class_docstring(node),
                reasoning=[f"Complex class with {complexity} control structures"]
            )
            self.results.append(analysis)
        self.generic_visit(node)
        self.current_class = old_class
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        return complexity
    def _needs_documentation(self, node: ast.FunctionDef, complexity: int) -> bool:
        if complexity > 10:
            return True
        has_complex_logic = self._has_complex_logic(node)
        has_no_docstring = not ast.get_docstring(node)
        is_public = not node.name.startswith('_')
        has_multiple_returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)]) > 1
        return (has_no_docstring and is_public and 
                (complexity > 7 or has_complex_logic or has_multiple_returns))
    def _has_complex_logic(self, node: ast.FunctionDef) -> bool:
        nested_loops = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                for grandchild in ast.walk(child):
                    if isinstance(grandchild, (ast.For, ast.While)) and grandchild != child:
                        nested_loops += 1
        has_exception_handling = any(isinstance(n, ast.Try) for n in ast.walk(node))
        has_async_patterns = any(isinstance(n, (ast.Await, ast.AsyncWith, ast.AsyncFor)) 
                                for n in ast.walk(node))
        complex_conditionals = len([n for n in ast.walk(node) 
                                  if isinstance(n, ast.BoolOp) and len(n.values) > 2])
        return (nested_loops > 0 or has_exception_handling or 
                has_async_patterns or complex_conditionals > 0)
    def _get_complexity_reasons(self, node: ast.FunctionDef, complexity: int) -> List[str]:
        reasons = []
        if complexity > 15:
            reasons.append(f"Very high cyclomatic complexity ({complexity})")
        elif complexity > 10:
            reasons.append(f"High cyclomatic complexity ({complexity})")
        if self._has_complex_logic(node):
            reasons.append("Contains complex logic patterns (nested loops, exception handling, or async operations)")
        returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
        if returns > 2:
            reasons.append(f"Multiple return paths ({returns})")
        args_count = len(node.args.args)
        if args_count > 6:
            reasons.append(f"Many parameters ({args_count})")
        if not ast.get_docstring(node):
            reasons.append("Missing documentation")
        return reasons
    def _generate_docstring(self, node: ast.FunctionDef, complexity: int) -> str:
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        return_stmts = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
        has_returns = any(stmt.value is not None for stmt in return_stmts)
        docstring_parts = []
        docstring_parts.append(f'"""{self._generate_function_summary(node, complexity)}')
        docstring_parts.append("")
        
        if complexity > 10:
            docstring_parts.append("This function has high complexity and handles multiple responsibilities.")
            docstring_parts.append("Consider refactoring into smaller functions.")
            docstring_parts.append("")
        
        if args:
            docstring_parts.append("Args:")
            for arg in args:
                docstring_parts.append(f"    {arg}: [Type and description needed]")
            docstring_parts.append("")
        
        if has_returns:
            docstring_parts.append("Returns:")
            docstring_parts.append("    [Return type and description needed]")
            docstring_parts.append("")
        
        if complexity > 12:
            docstring_parts.append("Note:")
            docstring_parts.append(f"    High complexity function (complexity: {complexity})")
            docstring_parts.append("    Consider breaking down into smaller, focused functions")
            docstring_parts.append("")
        
        if any(isinstance(n, ast.Try) for n in ast.walk(node)):
            docstring_parts.append("Raises:")
            docstring_parts.append("    [Exception types and conditions needed]")
            docstring_parts.append("")
        
        docstring_parts.append('"""')
        return "\n".join(docstring_parts)
    def _generate_class_docstring(self, node: ast.ClassDef) -> str:
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        docstring_parts = []
        docstring_parts.append(f'"""{node.name} class with specialized functionality.')
        docstring_parts.append("")
        docstring_parts.append("This class handles [describe main responsibility].")
        
        if len(methods) > 10:
            docstring_parts.append("Large class - consider splitting responsibilities.")
        
        docstring_parts.append("")
        docstring_parts.append("Attributes:")
        docstring_parts.append("    [Add main attributes and their descriptions]")
        docstring_parts.append('"""')
        return "\n".join(docstring_parts)
    def _generate_function_summary(self, node: ast.FunctionDef, complexity: int) -> str:
        name_words = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}', node.name)
        if name_words:
            action = name_words[0].lower()
            if action in ['get', 'fetch', 'retrieve', 'find']:
                return f"Retrieve and return {' '.join(name_words[1:]).lower()}"
            elif action in ['set', 'update', 'modify', 'change']:
                return f"Update {' '.join(name_words[1:]).lower()}"
            elif action in ['create', 'make', 'build', 'generate']:
                return f"Create {' '.join(name_words[1:]).lower()}"
            elif action in ['validate', 'check', 'verify']:
                return f"Validate {' '.join(name_words[1:]).lower()}"
            elif action in ['handle', 'process', 'manage']:
                return f"Handle {' '.join(name_words[1:]).lower()}"
        return f"Handle {node.name.replace('_', ' ').lower()} functionality"
def analyze_file(file_path: Path) -> List[ComplexityAnalysis]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        analyzer = ComplexityAnalyzer(str(file_path))
        analyzer.visit(tree)
        return analyzer.results
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []
def analyze_project(root_path: Path, exclude_patterns: List[str] = None) -> List[ComplexityAnalysis]:
    if exclude_patterns is None:
        exclude_patterns = ['test_', '__pycache__', '.git', 'venv', 'env', 'build']
    all_results = []
    for py_file in root_path.rglob('*.py'):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        results = analyze_file(py_file)
        all_results.extend(results)
    return all_results
def generate_documentation_report(results: List[ComplexityAnalysis], output_file: Path) -> None:
    results_by_complexity = sorted(results, key=lambda x: x.complexity_score, reverse=True)
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_analyzed': len(results),
        'needs_documentation': len([r for r in results if r.needs_docs]),
        'high_complexity': len([r for r in results if r.complexity_score > 15]),
        'medium_complexity': len([r for r in results if 10 < r.complexity_score <= 15]),
        'summary': {
            'undocumented_complex_functions': len([r for r in results if r.needs_docs and r.complexity_score > 10]),
            'average_complexity': sum(r.complexity_score for r in results) / len(results) if results else 0,
            'max_complexity': max((r.complexity_score for r in results), default=0)
        },
        'recommendations': [],
        'detailed_analysis': []
    }
    high_complexity_funcs = [r for r in results if r.complexity_score > 15]
    if high_complexity_funcs:
        report['recommendations'].append({
            'priority': 'HIGH',
            'category': 'Complexity Reduction',
            'description': f'{len(high_complexity_funcs)} functions have very high complexity (>15)',
            'action': 'Refactor these functions into smaller, focused functions'
        })
    undocumented_complex = [r for r in results if r.needs_docs and r.complexity_score > 10]
    if undocumented_complex:
        report['recommendations'].append({
            'priority': 'MEDIUM',
            'category': 'Documentation',
            'description': f'{len(undocumented_complex)} complex functions lack documentation',
            'action': 'Add complete docstrings explaining logic and parameters'
        })
    for result in results_by_complexity[:20]:
        if result.needs_docs or result.complexity_score > 12:
            report['detailed_analysis'].append({
                'file': result.file_path,
                'function': result.function_name,
                'line': result.line_number,
                'type': result.type,
                'complexity': result.complexity_score,
                'needs_docs': result.needs_docs,
                'current_docs_length': len(result.current_docs),
                'reasons': result.reasoning,
                'suggested_docstring': result.suggested_docs[:200] + '...' if result.suggested_docs else None
            })
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w') as f:
        f.write(f"# Code Complexity and Documentation Analysis\n\n")
        f.write(f"**Generated:** {report['generated_at']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Functions Analyzed:** {report['total_analyzed']}\n")
        f.write(f"- **Need Documentation:** {report['needs_documentation']}\n")
        f.write(f"- **High Complexity (>15):** {report['high_complexity']}\n")
        f.write(f"- **Medium Complexity (10-15):** {report['medium_complexity']}\n")
        f.write(f"- **Average Complexity:** {report['summary']['average_complexity']:.1f}\n\n")
        f.write(f"## Recommendations\n\n")
        for rec in report['recommendations']:
            f.write(f"### {rec['priority']}: {rec['category']}\n")
            f.write(f"**Issue:** {rec['description']}\n\n")
            f.write(f"**Action:** {rec['action']}\n\n")
        f.write(f"## Top Complex Functions Needing Attention\n\n")
        for item in report['detailed_analysis'][:10]:
            f.write(f"### `{item['function']}` in `{item['file']}`\n")
            f.write(f"- **Complexity:** {item['complexity']}\n")
            f.write(f"- **Line:** {item['line']}\n")
            f.write(f"- **Type:** {item['type']}\n")
            f.write(f"- **Needs Docs:** {'Yes' if item['needs_docs'] else 'No'}\n")
            f.write(f"- **Reasons:** {', '.join(item['reasons'])}\n\n")
def main():
    parser = argparse.ArgumentParser(description='Analyze code complexity and documentation needs')
    parser.add_argument('--root', type=Path, default=Path('.'), 
                       help='Root directory to analyze (default: current directory)')
    parser.add_argument('--output', type=Path, default=Path('complexity-analysis.json'),
                       help='Output file for analysis results')
    parser.add_argument('--threshold', type=int, default=10,
                       help='Complexity threshold for documentation requirements')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze, do not modify files')
    parser.add_argument('--add-docs', action='store_true',
                       help='Automatically add suggested documentation')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    args = parser.parse_args()
    print(f"🔍 Analyzing code complexity in {args.root}")
    results = analyze_project(args.root)
    if args.verbose:
        print(f"Found {len(results)} functions/classes to analyze")
    generate_documentation_report(results, args.output)
    needs_docs = [r for r in results if r.needs_docs]
    high_complexity = [r for r in results if r.complexity_score > 15]
    print(f"\n📊 Analysis Results:")
    print(f"  Total analyzed: {len(results)}")
    print(f"  Need documentation: {len(needs_docs)}")
    print(f"  High complexity (>15): {len(high_complexity)}")
    print(f"  Average complexity: {sum(r.complexity_score for r in results) / len(results):.1f}")
    if high_complexity:
        print(f"\n⚠️  High complexity functions:")
        for result in high_complexity[:5]:
            print(f"    {result.file_path}:{result.line_number} - {result.function_name} (complexity: {result.complexity_score})")
    if needs_docs:
        print(f"\n📝 Functions needing documentation:")
        for result in sorted(needs_docs, key=lambda x: x.complexity_score, reverse=True)[:5]:
            print(f"    {result.file_path}:{result.line_number} - {result.function_name} (complexity: {result.complexity_score})")
    print(f"\n📄 Detailed report saved to: {args.output}")
    print(f"📋 Markdown summary saved to: {args.output.with_suffix('.md')}")
    if len(high_complexity) > 5:
        print(f"\n❌ Too many high complexity functions ({len(high_complexity)}). Consider refactoring.")
        return 1
    return 0
if __name__ == '__main__':
    exit(main())