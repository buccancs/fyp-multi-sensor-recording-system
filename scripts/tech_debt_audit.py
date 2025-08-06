#!/usr/bin/env python3
"""
Technical Debt Audit Script for Multi-Sensor Recording System

Executes comprehensive quality analysis across Python and Kotlin codebases,
generating actionable reports for technical debt management.

Usage:
    python scripts/tech_debt_audit.py [--fix] [--report] [--category CATEGORY]

Examples:
    python scripts/tech_debt_audit.py --report
    python scripts/tech_debt_audit.py --fix --category python
    python scripts/tech_debt_audit.py --category documentation
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse


class TechnicalDebtAuditor:
    """Comprehensive technical debt audit framework."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.audit_results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.issues_found = []
        
    def run_full_audit(self, auto_fix: bool = False, category: Optional[str] = None) -> Dict[str, Any]:
        """Execute comprehensive technical debt audit."""
        print(f"🔍 Starting Technical Debt Audit - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Repository: {self.repo_path}")
        
        audit_report = {
            'timestamp': self.timestamp,
            'repo_path': str(self.repo_path),
            'categories': {}
        }
        
        # Define audit categories
        categories = {
            'python': self._audit_python_quality,
            'android': self._audit_android_quality,
            'dependencies': self._audit_dependencies,
            'documentation': self._audit_documentation,
            'performance': self._audit_performance,
            'security': self._audit_security
        }
        
        # Execute audits
        if category and category in categories:
            # Single category audit
            print(f"🎯 Auditing category: {category}")
            audit_report['categories'][category] = categories[category](auto_fix)
        else:
            # Full audit
            for cat_name, audit_func in categories.items():
                print(f"\n📊 Auditing {cat_name}...")
                try:
                    audit_report['categories'][cat_name] = audit_func(auto_fix)
                except Exception as e:
                    print(f"❌ Error auditing {cat_name}: {e}")
                    audit_report['categories'][cat_name] = {
                        'error': str(e),
                        'status': 'failed'
                    }
        
        # Calculate overall score
        audit_report['overall_score'] = self._calculate_overall_score(audit_report['categories'])
        audit_report['total_issues'] = len(self.issues_found)
        audit_report['critical_issues'] = len([i for i in self.issues_found if i.get('priority') == 'P0'])
        
        return audit_report
    
    def _audit_python_quality(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit Python code quality metrics."""
        print("  🐍 Analyzing Python code quality...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 0
        }
        
        python_app_path = self.repo_path / "PythonApp"
        if not python_app_path.exists():
            results['status'] = 'skipped'
            results['reason'] = 'PythonApp directory not found'
            return results
        
        # Check file count and structure
        py_files = list(python_app_path.rglob("*.py"))
        results['checks']['file_count'] = len(py_files)
        print(f"    📁 Found {len(py_files)} Python files")
        
        # Basic syntax check
        syntax_issues = self._check_python_syntax(py_files)
        results['checks']['syntax_errors'] = len(syntax_issues)
        results['issues'].extend(syntax_issues)
        
        # Import analysis
        import_issues = self._check_python_imports(py_files)
        results['checks']['import_issues'] = len(import_issues)
        results['issues'].extend(import_issues)
        
        # Code complexity (basic heuristic)
        complexity_issues = self._check_python_complexity(py_files)
        results['checks']['complexity_issues'] = len(complexity_issues)
        results['issues'].extend(complexity_issues)
        
        # Calculate score
        max_issues = len(py_files) * 3  # Rough heuristic
        total_issues = len(syntax_issues) + len(import_issues) + len(complexity_issues)
        results['score'] = max(0, 100 - (total_issues / max(max_issues, 1)) * 100)
        
        if auto_fix:
            self._fix_python_issues(results['issues'])
        
        return results
    
    def _audit_android_quality(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit Android/Kotlin code quality metrics."""
        print("  🤖 Analyzing Android code quality...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 0
        }
        
        android_app_path = self.repo_path / "AndroidApp"
        if not android_app_path.exists():
            results['status'] = 'skipped'
            results['reason'] = 'AndroidApp directory not found'
            return results
        
        # Check Kotlin files
        kt_files = list(android_app_path.rglob("*.kt"))
        results['checks']['kotlin_files'] = len(kt_files)
        print(f"    📁 Found {len(kt_files)} Kotlin files")
        
        # Check for common patterns
        architecture_issues = self._check_android_architecture(kt_files)
        results['checks']['architecture_issues'] = len(architecture_issues)
        results['issues'].extend(architecture_issues)
        
        # Check for long files
        long_file_issues = self._check_file_lengths(kt_files, max_lines=500)
        results['checks']['long_files'] = len(long_file_issues)
        results['issues'].extend(long_file_issues)
        
        # Build system check
        build_issues = self._check_android_build_config()
        results['checks']['build_issues'] = len(build_issues)
        results['issues'].extend(build_issues)
        
        # Calculate score
        total_issues = len(architecture_issues) + len(long_file_issues) + len(build_issues)
        results['score'] = max(0, 100 - (total_issues / max(len(kt_files), 1)) * 50)
        
        return results
    
    def _audit_dependencies(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit dependency health and security."""
        print("  📦 Analyzing dependencies...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 100
        }
        
        # Check Python dependencies
        requirements_files = list(self.repo_path.glob("*requirements*.txt"))
        pyproject_file = self.repo_path / "pyproject.toml"
        environment_file = self.repo_path / "environment.yml"
        
        python_deps = []
        if pyproject_file.exists():
            python_deps.extend(self._parse_pyproject_dependencies(pyproject_file))
        if environment_file.exists():
            python_deps.extend(self._parse_conda_dependencies(environment_file))
        
        results['checks']['python_dependencies'] = len(python_deps)
        
        # Check for outdated patterns or potential issues
        dep_issues = self._check_dependency_issues(python_deps)
        results['issues'].extend(dep_issues)
        results['checks']['dependency_issues'] = len(dep_issues)
        
        # Android dependencies
        gradle_files = list(self.repo_path.rglob("build.gradle*"))
        android_deps = []
        for gradle_file in gradle_files:
            android_deps.extend(self._parse_gradle_dependencies(gradle_file))
        
        results['checks']['android_dependencies'] = len(android_deps)
        
        # Calculate score based on issues found
        if len(dep_issues) > 0:
            results['score'] = max(0, 100 - len(dep_issues) * 10)
        
        return results
    
    def _audit_documentation(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit documentation completeness and quality."""
        print("  📚 Analyzing documentation...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 0
        }
        
        # Find documentation files
        doc_files = list(self.repo_path.rglob("*.md")) + list(self.repo_path.rglob("*.rst"))
        results['checks']['doc_files'] = len(doc_files)
        print(f"    📄 Found {len(doc_files)} documentation files")
        
        # Check for essential documentation
        essential_docs = ['README.md', 'CONTRIBUTOR_GUIDE.md', 'changelog.md']
        missing_docs = []
        for doc in essential_docs:
            if not (self.repo_path / doc).exists():
                missing_docs.append({
                    'type': 'missing_documentation',
                    'priority': 'P1',
                    'description': f"Missing essential document: {doc}",
                    'file': doc
                })
        
        results['issues'].extend(missing_docs)
        results['checks']['missing_essential_docs'] = len(missing_docs)
        
        # Check documentation quality
        doc_quality_issues = self._check_documentation_quality(doc_files)
        results['issues'].extend(doc_quality_issues)
        results['checks']['quality_issues'] = len(doc_quality_issues)
        
        # Check for ADR directory
        adr_path = self.repo_path / "docs" / "adr"
        if adr_path.exists():
            adr_files = list(adr_path.glob("ADR-*.md"))
            results['checks']['adr_count'] = len(adr_files)
        else:
            results['issues'].append({
                'type': 'missing_architecture_docs',
                'priority': 'P2',
                'description': 'No Architecture Decision Records directory found',
                'file': 'docs/adr/'
            })
            results['checks']['adr_count'] = 0
        
        # Calculate score
        total_issues = len(missing_docs) + len(doc_quality_issues)
        base_score = 100 - (total_issues * 5)
        # Bonus for having good documentation structure
        if len(doc_files) > 10 and len(missing_docs) == 0:
            base_score += 10
        
        results['score'] = max(0, min(100, base_score))
        
        return results
    
    def _audit_performance(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit system performance metrics."""
        print("  ⚡ Analyzing performance...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 85  # Default good score unless issues found
        }
        
        # Check for performance anti-patterns in Python
        python_perf_issues = self._check_python_performance_patterns()
        results['issues'].extend(python_perf_issues)
        results['checks']['python_performance_issues'] = len(python_perf_issues)
        
        # Check file sizes
        large_file_issues = self._check_large_files()
        results['issues'].extend(large_file_issues)
        results['checks']['large_files'] = len(large_file_issues)
        
        # Adjust score based on issues
        total_issues = len(python_perf_issues) + len(large_file_issues)
        if total_issues > 0:
            results['score'] = max(0, 85 - total_issues * 5)
        
        return results
    
    def _audit_security(self, auto_fix: bool) -> Dict[str, Any]:
        """Audit security considerations."""
        print("  🔒 Analyzing security...")
        results = {
            'status': 'completed',
            'checks': {},
            'issues': [],
            'score': 90  # Default good score
        }
        
        # Check for hardcoded secrets
        secret_issues = self._check_for_secrets()
        results['issues'].extend(secret_issues)
        results['checks']['potential_secrets'] = len(secret_issues)
        
        # Check for insecure patterns
        security_pattern_issues = self._check_security_patterns()
        results['issues'].extend(security_pattern_issues)
        results['checks']['security_patterns'] = len(security_pattern_issues)
        
        # Adjust score
        total_issues = len(secret_issues) + len(security_pattern_issues)
        if total_issues > 0:
            results['score'] = max(0, 90 - total_issues * 15)  # Security issues are weighted heavily
        
        return results
    
    def _check_python_syntax(self, py_files: List[Path]) -> List[Dict[str, Any]]:
        """Check Python files for basic syntax errors."""
        issues = []
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, str(file_path), 'exec')
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'priority': 'P0',
                    'description': f"Syntax error: {e.msg}",
                    'file': str(file_path.relative_to(self.repo_path)),
                    'line': e.lineno
                })
            except UnicodeDecodeError:
                issues.append({
                    'type': 'encoding_error',
                    'priority': 'P1',
                    'description': "File encoding issue",
                    'file': str(file_path.relative_to(self.repo_path))
                })
            except Exception:
                # Skip files that can't be read
                pass
        return issues
    
    def _check_python_imports(self, py_files: List[Path]) -> List[Dict[str, Any]]:
        """Check for problematic import patterns."""
        issues = []
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        line = line.strip()
                        # Check for star imports (except in __init__.py)
                        if 'from' in line and 'import *' in line and not file_path.name == '__init__.py':
                            issues.append({
                                'type': 'star_import',
                                'priority': 'P2',
                                'description': f"Star import found: {line}",
                                'file': str(file_path.relative_to(self.repo_path)),
                                'line': i
                            })
            except Exception:
                pass
        return issues
    
    def _check_python_complexity(self, py_files: List[Path]) -> List[Dict[str, Any]]:
        """Check for overly complex functions (basic heuristic)."""
        issues = []
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    current_function = None
                    function_start = 0
                    indent_level = 0
                    
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith('def '):
                            # New function found
                            if current_function and (i - function_start) > 60:
                                issues.append({
                                    'type': 'long_function',
                                    'priority': 'P2',
                                    'description': f"Function '{current_function}' is {i - function_start} lines long",
                                    'file': str(file_path.relative_to(self.repo_path)),
                                    'line': function_start
                                })
                            
                            current_function = stripped.split('(')[0].replace('def ', '')
                            function_start = i
                            indent_level = len(line) - len(line.lstrip())
                        elif stripped.startswith('class '):
                            current_function = None
            except Exception:
                pass
        return issues
    
    def _check_android_architecture(self, kt_files: List[Path]) -> List[Dict[str, Any]]:
        """Check Android architecture patterns."""
        issues = []
        
        # Look for potential architecture violations
        activity_files = [f for f in kt_files if 'Activity.kt' in str(f)]
        viewmodel_files = [f for f in kt_files if 'ViewModel' in str(f)]
        
        # Check if Activities are too large
        for activity_file in activity_files:
            try:
                with open(activity_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 300:
                        issues.append({
                            'type': 'large_activity',
                            'priority': 'P2',
                            'description': f"Activity file has {len(lines)} lines (consider refactoring)",
                            'file': str(activity_file.relative_to(self.repo_path))
                        })
            except Exception:
                pass
        
        return issues
    
    def _check_file_lengths(self, files: List[Path], max_lines: int = 500) -> List[Dict[str, Any]]:
        """Check for overly long files."""
        issues = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                    if line_count > max_lines:
                        issues.append({
                            'type': 'long_file',
                            'priority': 'P2',
                            'description': f"File has {line_count} lines (exceeds {max_lines} line threshold)",
                            'file': str(file_path.relative_to(self.repo_path))
                        })
            except Exception:
                pass
        return issues
    
    def _check_android_build_config(self) -> List[Dict[str, Any]]:
        """Check Android build configuration."""
        issues = []
        
        gradle_files = list(self.repo_path.rglob("build.gradle*"))
        for gradle_file in gradle_files:
            try:
                with open(gradle_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for hardcoded version numbers
                    if 'compileSdkVersion' in content or 'targetSdkVersion' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if 'compileSdkVersion' in line and any(str(v) in line for v in range(20, 35)):
                                if not any(var in line for var in ['$', 'rootProject', 'project']):
                                    issues.append({
                                        'type': 'hardcoded_version',
                                        'priority': 'P3',
                                        'description': "Hardcoded SDK version (consider using variables)",
                                        'file': str(gradle_file.relative_to(self.repo_path)),
                                        'line': i
                                    })
            except Exception:
                pass
        
        return issues
    
    def _parse_pyproject_dependencies(self, pyproject_file: Path) -> List[str]:
        """Parse dependencies from pyproject.toml."""
        dependencies = []
        try:
            import tomllib
            with open(pyproject_file, 'rb') as f:
                data = tomllib.load(f)
                if 'project' in data and 'dependencies' in data['project']:
                    dependencies.extend(data['project']['dependencies'])
        except ImportError:
            # Fallback for older Python versions
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    # Basic parsing - look for dependencies array
                    in_deps = False
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('dependencies'):
                            in_deps = True
                        elif in_deps and line.startswith(']'):
                            break
                        elif in_deps and line.startswith('"'):
                            dep = line.strip('",')
                            if dep:
                                dependencies.append(dep)
            except Exception:
                pass
        except Exception:
            pass
        
        return dependencies
    
    def _parse_conda_dependencies(self, environment_file: Path) -> List[str]:
        """Parse dependencies from environment.yml."""
        dependencies = []
        try:
            with open(environment_file, 'r') as f:
                content = f.read()
                in_deps = False
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('dependencies:'):
                        in_deps = True
                    elif in_deps and line.startswith('- pip:'):
                        continue
                    elif in_deps and line.startswith('-'):
                        dep = line.strip('- ')
                        if dep and not dep.startswith('pip'):
                            dependencies.append(dep)
                    elif in_deps and not line.startswith(' ') and not line.startswith('-') and line:
                        break
        except Exception:
            pass
        
        return dependencies
    
    def _parse_gradle_dependencies(self, gradle_file: Path) -> List[str]:
        """Parse dependencies from Gradle files."""
        dependencies = []
        try:
            with open(gradle_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                in_dependencies = False
                for line in lines:
                    line = line.strip()
                    if 'dependencies {' in line:
                        in_dependencies = True
                    elif in_dependencies and '}' in line and not any(keyword in line for keyword in ['implementation', 'testImplementation', 'kapt']):
                        in_dependencies = False
                    elif in_dependencies and any(keyword in line for keyword in ['implementation', 'testImplementation', 'kapt', 'api']):
                        dependencies.append(line)
        except Exception:
            pass
        
        return dependencies
    
    def _check_dependency_issues(self, dependencies: List[str]) -> List[Dict[str, Any]]:
        """Check for dependency-related issues."""
        issues = []
        
        # Check for potentially outdated or problematic dependencies
        for dep in dependencies:
            # Check for very old Python versions
            if 'python' in dep.lower() and any(old_ver in dep for old_ver in ['3.6', '3.7']):
                issues.append({
                    'type': 'outdated_python',
                    'priority': 'P1',
                    'description': f"Potentially outdated Python version requirement: {dep}",
                    'file': 'dependencies'
                })
            
            # Check for unpinned dependencies (very basic check)
            if dep and '==' not in dep and '>=' not in dep and '~=' not in dep and not any(char in dep for char in ['<', '>']):
                # Only flag if it's not a simple package name
                if '/' not in dep and '.' not in dep and len(dep.split()) == 1:
                    issues.append({
                        'type': 'unpinned_dependency',
                        'priority': 'P3',
                        'description': f"Unpinned dependency (consider version constraints): {dep}",
                        'file': 'dependencies'
                    })
        
        return issues
    
    def _check_documentation_quality(self, doc_files: List[Path]) -> List[Dict[str, Any]]:
        """Check documentation quality."""
        issues = []
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for very short documentation files
                    if len(content.strip()) < 100:
                        issues.append({
                            'type': 'short_documentation',
                            'priority': 'P3',
                            'description': "Documentation file is very short (consider expanding)",
                            'file': str(doc_file.relative_to(self.repo_path))
                        })
                    
                    # Check for broken internal links
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if '](.' in line or '](/' in line:
                            # Basic check for relative links
                            import re
                            links = re.findall(r'\]\(([^)]+)\)', line)
                            for link in links:
                                if link.startswith('./') or link.startswith('/'):
                                    # Check if file exists
                                    link_path = self.repo_path / link.lstrip('./')
                                    if not link_path.exists() and not link.startswith('http'):
                                        issues.append({
                                            'type': 'broken_link',
                                            'priority': 'P2',
                                            'description': f"Potentially broken link: {link}",
                                            'file': str(doc_file.relative_to(self.repo_path)),
                                            'line': i
                                        })
            except Exception:
                pass
        
        return issues
    
    def _check_python_performance_patterns(self) -> List[Dict[str, Any]]:
        """Check for Python performance anti-patterns."""
        issues = []
        
        python_files = list((self.repo_path / "PythonApp").rglob("*.py")) if (self.repo_path / "PythonApp").exists() else []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        line_stripped = line.strip()
                        
                        # Check for string concatenation in loops (basic pattern)
                        if 'for ' in line and '+=' in line and '"' in line:
                            issues.append({
                                'type': 'string_concatenation_in_loop',
                                'priority': 'P2',
                                'description': "Potential inefficient string concatenation in loop",
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': i
                            })
                        
                        # Check for synchronous operations that might benefit from async
                        if any(pattern in line_stripped for pattern in ['time.sleep(', 'requests.get(', 'urllib.request']):
                            issues.append({
                                'type': 'potential_async_opportunity',
                                'priority': 'P3',
                                'description': "Consider async alternatives for I/O operations",
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': i
                            })
            except Exception:
                pass
        
        return issues
    
    def _check_large_files(self) -> List[Dict[str, Any]]:
        """Check for large files that might impact performance."""
        issues = []
        
        # Check for large code files
        code_files = (
            list(self.repo_path.rglob("*.py")) + 
            list(self.repo_path.rglob("*.kt")) + 
            list(self.repo_path.rglob("*.java"))
        )
        
        for file_path in code_files:
            try:
                file_size = file_path.stat().st_size
                if file_size > 100 * 1024:  # 100 KB
                    issues.append({
                        'type': 'large_code_file',
                        'priority': 'P2',
                        'description': f"Large code file ({file_size // 1024} KB) - consider splitting",
                        'file': str(file_path.relative_to(self.repo_path))
                    })
            except Exception:
                pass
        
        return issues
    
    def _check_for_secrets(self) -> List[Dict[str, Any]]:
        """Check for potential hardcoded secrets."""
        issues = []
        
        # Define patterns that might indicate secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][^"\']{16,}["\']',
        ]
        
        import re
        
        code_files = (
            list(self.repo_path.rglob("*.py")) + 
            list(self.repo_path.rglob("*.kt")) + 
            list(self.repo_path.rglob("*.java")) +
            list(self.repo_path.rglob("*.js")) +
            list(self.repo_path.rglob("*.ts"))
        )
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                # Skip obvious test/example values
                                if not any(test_indicator in line.lower() for test_indicator in ['test', 'example', 'dummy', 'fake', 'xxxx']):
                                    issues.append({
                                        'type': 'potential_secret',
                                        'priority': 'P0',
                                        'description': "Potential hardcoded secret detected",
                                        'file': str(file_path.relative_to(self.repo_path)),
                                        'line': i
                                    })
            except Exception:
                pass
        
        return issues
    
    def _check_security_patterns(self) -> List[Dict[str, Any]]:
        """Check for insecure coding patterns."""
        issues = []
        
        code_files = list(self.repo_path.rglob("*.py")) + list(self.repo_path.rglob("*.kt"))
        
        insecure_patterns = {
            'python': [
                ('eval(', 'Use of eval() is dangerous'),
                ('exec(', 'Use of exec() is dangerous'),
                ('subprocess.call(shell=True', 'Shell injection risk'),
                ('os.system(', 'Command injection risk'),
            ],
            'kotlin': [
                ('Runtime.getRuntime().exec(', 'Command injection risk'),
                ('.setJavaScriptEnabled(true)', 'JavaScript enabled in WebView'),
            ]
        }
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    file_type = 'python' if file_path.suffix == '.py' else 'kotlin'
                    patterns = insecure_patterns.get(file_type, [])
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, description in patterns:
                            if pattern in line:
                                issues.append({
                                    'type': 'security_pattern',
                                    'priority': 'P1',
                                    'description': description,
                                    'file': str(file_path.relative_to(self.repo_path)),
                                    'line': i
                                })
            except Exception:
                pass
        
        return issues
    
    def _fix_python_issues(self, issues: List[Dict[str, Any]]) -> None:
        """Auto-fix Python issues where possible."""
        print("    🔧 Auto-fixing Python issues...")
        
        # For now, just report what could be fixed
        fixable_issues = [i for i in issues if i['type'] in ['star_import']]
        
        if fixable_issues:
            print(f"    ✅ Could auto-fix {len(fixable_issues)} issues (implementation needed)")
        else:
            print("    ℹ️  No auto-fixable issues found")
    
    def _calculate_overall_score(self, categories: Dict[str, Any]) -> int:
        """Calculate overall technical debt score (0-100)."""
        scores = []
        weights = {
            'python': 0.25,
            'android': 0.25,
            'dependencies': 0.15,
            'documentation': 0.15,
            'performance': 0.1,
            'security': 0.1
        }
        
        total_weight = 0
        weighted_score = 0
        
        for category, weight in weights.items():
            if category in categories and categories[category].get('status') == 'completed':
                score = categories[category].get('score', 0)
                weighted_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            return int(weighted_score / total_weight)
        else:
            return 0
    
    def generate_report(self, audit_results: Dict[str, Any], output_file: Optional[Path] = None) -> str:
        """Generate comprehensive audit report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_lines = [
            f"# Technical Debt Audit Report",
            f"",
            f"**Generated**: {timestamp}",
            f"**Repository**: {audit_results['repo_path']}",
            f"**Overall Score**: {audit_results['overall_score']}/100",
            f"**Total Issues**: {audit_results['total_issues']}",
            f"**Critical Issues**: {audit_results['critical_issues']}",
            f"",
            f"## Executive Summary",
            f"",
            self._generate_executive_summary(audit_results),
            f"",
            f"## Category Breakdown",
            f"",
        ]
        
        # Add category details
        for category, results in audit_results['categories'].items():
            if results.get('status') == 'completed':
                report_lines.extend([
                    f"### {category.title()}",
                    f"",
                    f"**Score**: {results.get('score', 0)}/100",
                    f"**Issues Found**: {len(results.get('issues', []))}",
                    f"",
                ])
                
                # Add checks summary
                if 'checks' in results:
                    report_lines.append("**Checks Performed**:")
                    for check, value in results['checks'].items():
                        report_lines.append(f"- {check.replace('_', ' ').title()}: {value}")
                    report_lines.append("")
                
                # Add issues
                issues = results.get('issues', [])
                if issues:
                    report_lines.append("**Issues Found**:")
                    for issue in issues[:10]:  # Limit to first 10 issues per category
                        priority = issue.get('priority', 'P3')
                        file_info = f" ({issue['file']})" if 'file' in issue else ""
                        line_info = f":{issue['line']}" if 'line' in issue else ""
                        report_lines.append(f"- [{priority}] {issue['description']}{file_info}{line_info}")
                    
                    if len(issues) > 10:
                        report_lines.append(f"- ... and {len(issues) - 10} more issues")
                    report_lines.append("")
            elif results.get('status') == 'skipped':
                report_lines.extend([
                    f"### {category.title()}",
                    f"",
                    f"**Status**: Skipped - {results.get('reason', 'Unknown reason')}",
                    f"",
                ])
        
        # Add recommendations
        report_lines.extend([
            f"## Recommendations",
            f"",
            self._generate_recommendations(audit_results),
            f"",
            f"## Next Steps",
            f"",
            self._generate_next_steps(audit_results),
        ])
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report_content)
            print(f"📊 Report saved to: {output_file}")
        
        return report_content
    
    def _generate_executive_summary(self, audit_results: Dict[str, Any]) -> str:
        """Generate executive summary of audit results."""
        overall_score = audit_results['overall_score']
        total_issues = audit_results['total_issues']
        critical_issues = audit_results['critical_issues']
        
        if overall_score >= 90:
            health_status = "Excellent"
            health_emoji = "🟢"
        elif overall_score >= 75:
            health_status = "Good"
            health_emoji = "🟡"
        elif overall_score >= 60:
            health_status = "Fair"
            health_emoji = "🟠"
        else:
            health_status = "Needs Attention"
            health_emoji = "🔴"
        
        summary_lines = [
            f"{health_emoji} **Overall Health**: {health_status} ({overall_score}/100)",
            f"",
            f"The codebase analysis reveals {total_issues} total issues across all categories. ",
        ]
        
        if critical_issues > 0:
            summary_lines.append(f"**{critical_issues} critical issues require immediate attention.**")
        else:
            summary_lines.append("No critical issues identified.")
        
        summary_lines.extend([
            f"",
            f"**Key Findings**:",
        ])
        
        # Analyze category performance
        categories = audit_results.get('categories', {})
        best_category = None
        worst_category = None
        best_score = -1
        worst_score = 101
        
        for category, results in categories.items():
            if results.get('status') == 'completed':
                score = results.get('score', 0)
                if score > best_score:
                    best_score = score
                    best_category = category
                if score < worst_score:
                    worst_score = score
                    worst_category = category
        
        if best_category:
            summary_lines.append(f"- Strongest area: {best_category.title()} ({best_score}/100)")
        if worst_category and worst_category != best_category:
            summary_lines.append(f"- Area needing attention: {worst_category.title()} ({worst_score}/100)")
        
        return "\n".join(summary_lines)
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> str:
        """Generate actionable recommendations."""
        recommendations = []
        
        critical_issues = audit_results['critical_issues']
        overall_score = audit_results['overall_score']
        
        if critical_issues > 0:
            recommendations.extend([
                f"### Immediate Actions Required",
                f"",
                f"1. **Address {critical_issues} critical security/syntax issues**",
                f"   - Review P0 priority items in the detailed findings",
                f"   - These issues could compromise system security or functionality",
                f"",
            ])
        
        if overall_score < 75:
            recommendations.extend([
                f"### Code Quality Improvements",
                f"",
                f"1. **Establish quality gates**",
                f"   - Integrate static analysis tools into CI/CD pipeline",
                f"   - Set minimum quality thresholds for new code",
                f"",
                f"2. **Plan technical debt reduction**",
                f"   - Allocate 20% of development time to technical debt",
                f"   - Prioritize P1 and P2 issues identified in this audit",
                f"",
            ])
        
        # Category-specific recommendations
        categories = audit_results.get('categories', {})
        
        for category, results in categories.items():
            if results.get('status') == 'completed':
                score = results.get('score', 0)
                issues = results.get('issues', [])
                
                if score < 70 and issues:
                    recommendations.extend([
                        f"### {category.title()} Specific Actions",
                        f"",
                    ])
                    
                    if category == 'documentation':
                        recommendations.extend([
                            f"- Complete missing essential documentation",
                            f"- Review and update existing documentation for accuracy",
                            f"- Establish documentation standards and review process",
                        ])
                    elif category == 'security':
                        recommendations.extend([
                            f"- Immediate security review required",
                            f"- Implement secure coding training for team",
                            f"- Add security scanning to CI/CD pipeline",
                        ])
                    elif category == 'dependencies':
                        recommendations.extend([
                            f"- Update outdated dependencies",
                            f"- Implement dependency vulnerability scanning",
                            f"- Establish dependency update schedule",
                        ])
                    
                    recommendations.append("")
        
        return "\n".join(recommendations)
    
    def _generate_next_steps(self, audit_results: Dict[str, Any]) -> str:
        """Generate concrete next steps."""
        next_steps = [
            "1. **Prioritize Critical Issues**",
            "   - Address all P0 issues within 1 week",
            "   - Create GitHub issues for tracking",
            "",
            "2. **Implement Continuous Monitoring**",
            "   - Schedule weekly automated audits",
            "   - Set up alerts for quality threshold violations",
            "",
            "3. **Team Training**",
            "   - Code review training focused on identified patterns",
            "   - Tool-specific training for static analysis tools",
            "",
            "4. **Process Improvements**",
            "   - Update development workflow to include quality checks",
            "   - Establish definition of done including quality criteria",
            "",
            "5. **Schedule Next Audit**",
            f"   - Recommended: {(datetime.now() + __import__('datetime').timedelta(weeks=4)).strftime('%Y-%m-%d')}",
            "   - Focus on improvement tracking and new issue identification",
        ]
        
        return "\n".join(next_steps)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Technical Debt Audit for Multi-Sensor Recording System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tech_debt_audit.py --report
  python scripts/tech_debt_audit.py --fix --category python
  python scripts/tech_debt_audit.py --category documentation
        """
    )
    
    parser.add_argument(
        "--fix", 
        action="store_true", 
        help="Auto-fix issues where possible"
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate detailed markdown report"
    )
    parser.add_argument(
        "--category", 
        choices=['python', 'android', 'dependencies', 'documentation', 'performance', 'security'],
        help="Audit specific category only"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report (default: audit_reports/tech_debt_audit_TIMESTAMP.md)"
    )
    
    args = parser.parse_args()
    
    # Initialize auditor
    repo_path = Path.cwd()
    auditor = TechnicalDebtAuditor(repo_path)
    
    try:
        # Run audit
        print("🚀 Starting Technical Debt Audit...")
        results = auditor.run_full_audit(auto_fix=args.fix, category=args.category)
        
        # Display summary
        print(f"\n📊 Audit Summary:")
        print(f"   Overall Score: {results['overall_score']}/100")
        print(f"   Total Issues: {results['total_issues']}")
        print(f"   Critical Issues: {results['critical_issues']}")
        
        # Generate report if requested
        if args.report:
            if args.output:
                output_file = args.output
            else:
                output_file = repo_path / "audit_reports" / f"tech_debt_audit_{auditor.timestamp}.md"
            
            auditor.generate_report(results, output_file)
        
        # Exit with appropriate code
        if results['critical_issues'] > 0:
            print(f"\n⚠️  Critical issues found. Please address P0 issues immediately.")
            sys.exit(1)
        elif results['overall_score'] < 70:
            print(f"\n⚠️  Code quality below threshold. Consider addressing identified issues.")
            sys.exit(1)
        else:
            print(f"\n✅ Code quality acceptable. Continue monitoring with regular audits.")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Audit interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()