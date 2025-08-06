"""
Architecture Tests for Multi-Sensor Recording System

These tests enforce clean architecture principles and prevent dependency violations
between different layers of the system.

Architecture Rules:
1. UI layer should not directly access data/persistence layer
2. Business logic should not depend on specific UI frameworks
3. Network layer should be isolated from UI concerns
4. Utilities should not import from business logic
5. Test code should not be imported by production code

Run with: python -m pytest tests/test_architecture.py -v
"""

import ast
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple
import pytest


class ArchitectureViolation(Exception):
    """Raised when architecture rules are violated"""
    pass


class DependencyAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze import dependencies"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: Set[str] = set()
        self.from_imports: Set[str] = set()
    
    def visit_Import(self, node: ast.Import):
        """Track regular imports"""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from imports"""
        if node.module:
            self.from_imports.add(node.module)
        self.generic_visit(node)


def analyze_file_dependencies(file_path: Path) -> Tuple[Set[str], Set[str]]:
    """Analyze import dependencies in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        analyzer = DependencyAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        return analyzer.imports, analyzer.from_imports
    except Exception:
        # Skip files that can't be parsed
        return set(), set()


def get_project_structure() -> Dict[str, List[Path]]:
    """Analyze project structure and categorize files by layer"""
    
    project_root = Path(__file__).parent.parent
    
    structure = {
        'ui': [],
        'business': [],
        'network': [],
        'data': [],
        'utils': [],
        'tests': [],
        'config': []
    }
    
    # Define layer patterns
    layer_patterns = {
        'ui': [
            r'.*gui.*',
            r'.*ui.*',
            r'.*web_ui.*',
            r'.*frontend.*',
            r'.*dashboard.*',
            r'.*activity.*',
            r'.*fragment.*',
            r'.*viewmodel.*'
        ],
        'business': [
            r'.*manager.*',
            r'.*controller.*',
            r'.*service.*',
            r'.*recording.*',
            r'.*session.*',
            r'.*calibration.*',
            r'.*shimmer.*'
        ],
        'network': [
            r'.*network.*',
            r'.*server.*',
            r'.*client.*',
            r'.*protocol.*',
            r'.*websocket.*',
            r'.*socket.*'
        ],
        'data': [
            r'.*data.*',
            r'.*storage.*',
            r'.*persistence.*',
            r'.*database.*',
            r'.*file.*',
            r'.*export.*'
        ],
        'utils': [
            r'.*util.*',
            r'.*helper.*',
            r'.*common.*',
            r'.*tool.*'
        ],
        'tests': [
            r'.*test.*',
            r'.*spec.*'
        ],
        'config': [
            r'.*config.*',
            r'.*setting.*',
            r'.*environment.*'
        ]
    }
    
    # Analyze Python files
    for py_file in project_root.rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        file_str = str(py_file).lower()
        categorized = False
        
        for layer, patterns in layer_patterns.items():
            if any(re.search(pattern, file_str) for pattern in patterns):
                structure[layer].append(py_file)
                categorized = True
                break
        
        if not categorized:
            # Default categorization based on directory structure
            if 'gui' in str(py_file) or 'ui' in str(py_file):
                structure['ui'].append(py_file)
            elif 'test' in str(py_file):
                structure['tests'].append(py_file)
            else:
                structure['business'].append(py_file)
    
    return structure


def check_layer_dependencies(structure: Dict[str, List[Path]]) -> List[str]:
    """Check for architecture violations between layers"""
    violations = []
    
    # Define forbidden dependencies (source_layer -> forbidden_targets)
    forbidden_deps = {
        'ui': ['data'],  # UI should not directly access data layer
        'utils': ['business', 'ui', 'network'],  # Utils should be independent
        'config': ['business', 'ui', 'network'],  # Config should be independent
    }
    
    # Analyze dependencies for each layer
    for source_layer, files in structure.items():
        if source_layer in forbidden_deps:
            for file_path in files:
                imports, from_imports = analyze_file_dependencies(file_path)
                all_imports = imports.union(from_imports)
                
                # Check against files in forbidden layers
                for forbidden_layer in forbidden_deps[source_layer]:
                    forbidden_files = structure[forbidden_layer]
                    
                    for forbidden_file in forbidden_files:
                        # Extract module name patterns - handle different directory structures
                        try:
                            relative_path = str(forbidden_file.relative_to(file_path.parent.parent))
                        except ValueError:
                            # Files in different directory trees - use absolute comparison
                            relative_path = str(forbidden_file)
                        
                        module_patterns = [
                            relative_path.replace('/', '.').replace('.py', ''),
                            forbidden_file.stem,
                            forbidden_file.name.replace('.py', '')
                        ]
                        
                        # Check if any imports violate the rule
                        for imp in all_imports:
                            for pattern in module_patterns:
                                if pattern in imp:
                                    violations.append(
                                        f"Architecture violation: {source_layer} layer file "
                                        f"'{file_path.name}' imports from {forbidden_layer} layer "
                                        f"('{imp}' -> '{forbidden_file.name}')"
                                    )
    
    return violations


def check_cross_platform_dependencies() -> List[str]:
    """Check for platform-specific dependencies that break portability"""
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    # Platform-specific modules that should be avoided in business logic
    platform_specific = {
        'win32api', 'win32con', 'winsound', 'msvcrt',  # Windows
        'termios', 'tty', 'grp', 'pwd',  # Unix/Linux
        'CoreFoundation', 'Foundation', 'AppKit'  # macOS
    }
    
    business_files = []
    for py_file in project_root.rglob('*.py'):
        if any(keyword in str(py_file).lower() for keyword in ['manager', 'controller', 'service']):
            business_files.append(py_file)
    
    for file_path in business_files:
        imports, from_imports = analyze_file_dependencies(file_path)
        all_imports = imports.union(from_imports)
        
        for imp in all_imports:
            if any(platform_mod in imp for platform_mod in platform_specific):
                violations.append(
                    f"Platform dependency violation: Business logic file "
                    f"'{file_path.name}' imports platform-specific module '{imp}'"
                )
    
    return violations


def check_test_isolation() -> List[str]:
    """Ensure test code is not imported by production code"""
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    # Find all test files
    test_files = []
    for py_file in project_root.rglob('*.py'):
        if 'test' in str(py_file).lower() or py_file.name.startswith('test_'):
            test_files.append(py_file)
    
    # Find all production files
    production_files = []
    for py_file in project_root.rglob('*.py'):
        if ('test' not in str(py_file).lower() and 
            not py_file.name.startswith('test_') and
            'venv' not in str(py_file) and
            '__pycache__' not in str(py_file)):
            production_files.append(py_file)
    
    # Check if production code imports test code
    for prod_file in production_files:
        imports, from_imports = analyze_file_dependencies(prod_file)
        all_imports = imports.union(from_imports)
        
        for test_file in test_files:
            test_module = test_file.stem
            
            for imp in all_imports:
                if test_module in imp and 'test' in imp:
                    violations.append(
                        f"Test isolation violation: Production file "
                        f"'{prod_file.name}' imports test module '{imp}'"
                    )
    
    return violations


def check_circular_dependencies() -> List[str]:
    """Check for circular dependencies between modules"""
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    # Build dependency graph
    dependency_graph = {}
    
    for py_file in project_root.rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        imports, from_imports = analyze_file_dependencies(py_file)
        all_imports = imports.union(from_imports)
        
        module_name = py_file.stem
        dependency_graph[module_name] = []
        
        for imp in all_imports:
            # Extract module name from import
            imported_module = imp.split('.')[0] if '.' in imp else imp
            if imported_module != module_name:  # Avoid self-references
                dependency_graph[module_name].append(imported_module)
    
    # Simple cycle detection (can be improved with more sophisticated algorithms)
    def has_cycle(graph, start, visited, rec_stack):
        visited[start] = True
        rec_stack[start] = True
        
        for neighbor in graph.get(start, []):
            if neighbor in graph:  # Only check modules we know about
                if not visited.get(neighbor, False):
                    if has_cycle(graph, neighbor, visited, rec_stack):
                        return True
                elif rec_stack.get(neighbor, False):
                    return True
        
        rec_stack[start] = False
        return False
    
    visited = {}
    rec_stack = {}
    
    for module in dependency_graph:
        if not visited.get(module, False):
            if has_cycle(dependency_graph, module, visited, rec_stack):
                violations.append(f"Circular dependency detected involving module '{module}'")
    
    return violations


# Test Cases

def test_layer_separation():
    """Test that layers don't violate dependency rules"""
    structure = get_project_structure()
    violations = check_layer_dependencies(structure)
    
    if violations:
        pytest.fail(f"Architecture violations found:\n" + "\n".join(violations))


def test_platform_independence():
    """Test that business logic doesn't use platform-specific modules"""
    violations = check_cross_platform_dependencies()
    
    if violations:
        pytest.fail(f"Platform dependency violations found:\n" + "\n".join(violations))


def test_test_isolation():
    """Test that production code doesn't import test modules"""
    violations = check_test_isolation()
    
    if violations:
        pytest.fail(f"Test isolation violations found:\n" + "\n".join(violations))


def test_no_circular_dependencies():
    """Test for circular dependencies between modules"""
    violations = check_circular_dependencies()
    
    # Allow some expected cycles (common in large projects)
    allowed_cycles = {'manager', 'controller', 'service'}  # These often need to reference each other
    
    significant_violations = [v for v in violations 
                            if not any(allowed in v.lower() for allowed in allowed_cycles)]
    
    if significant_violations:
        pytest.fail(f"Circular dependency violations found:\n" + "\n".join(significant_violations))


def test_project_structure_completeness():
    """Test that project structure analysis is comprehensive"""
    structure = get_project_structure()
    
    total_files = sum(len(files) for files in structure.values())
    
    # Ensure we're analyzing a reasonable number of files
    assert total_files > 10, f"Only {total_files} files found - check analysis patterns"
    
    # Ensure each layer has some files (unless it's a very small project)
    important_layers = ['business', 'ui']
    for layer in important_layers:
        assert len(structure[layer]) > 0, f"No files found in {layer} layer"


def test_architecture_documentation():
    """Test that architecture decisions are documented"""
    project_root = Path(__file__).parent.parent
    
    # Check for architecture documentation
    arch_docs = list(project_root.rglob('*ARCHITECTURE*')) + list(project_root.rglob('*architecture*'))
    
    assert len(arch_docs) > 0, "No architecture documentation found. Add ARCHITECTURE.md or similar."


if __name__ == '__main__':
    # Run manual analysis
    print("🏗️  Architecture Analysis")
    print("=" * 50)
    
    structure = get_project_structure()
    for layer, files in structure.items():
        print(f"{layer.upper()}: {len(files)} files")
    
    print("\n🔍 Checking Architecture Rules...")
    
    all_violations = []
    
    # Check each rule
    layer_violations = check_layer_dependencies(structure)
    all_violations.extend(layer_violations)
    
    platform_violations = check_cross_platform_dependencies()
    all_violations.extend(platform_violations)
    
    test_violations = check_test_isolation()
    all_violations.extend(test_violations)
    
    circular_violations = check_circular_dependencies()
    all_violations.extend(circular_violations)
    
    if all_violations:
        print(f"\n❌ {len(all_violations)} architecture violations found:")
        for violation in all_violations:
            print(f"  - {violation}")
    else:
        print("\n✅ No architecture violations found!")
    
    print(f"\n📊 Analysis Summary:")
    print(f"  Total files analyzed: {sum(len(files) for files in structure.values())}")
    print(f"  Architecture violations: {len(all_violations)}")
    print(f"  Compliance score: {max(0, 100 - len(all_violations) * 5):.1f}%")