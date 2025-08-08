
import ast
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple
import pytest

class ArchitectureViolation(Exception):
    pass

class DependencyAnalyzer(ast.NodeVisitor):
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: Set[str] = set()
        self.from_imports: Set[str] = set()
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.from_imports.add(node.module)
        self.generic_visit(node)

def analyze_file_dependencies(file_path: Path) -> Tuple[Set[str], Set[str]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        analyzer = DependencyAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        return analyzer.imports, analyzer.from_imports
    except Exception:
        return set(), set()

def get_project_structure() -> Dict[str, List[Path]]:
    
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
            if 'gui' in str(py_file) or 'ui' in str(py_file):
                structure['ui'].append(py_file)
            elif 'test' in str(py_file):
                structure['tests'].append(py_file)
            else:
                structure['business'].append(py_file)
    
    return structure

def check_layer_dependencies(structure: Dict[str, List[Path]]) -> List[str]:
    violations = []
    
    forbidden_deps = {
        'ui': ['data'],
        'utils': ['business', 'ui', 'network'],
        'config': ['business', 'ui', 'network'],
    }
    
    for source_layer, files in structure.items():
        if source_layer in forbidden_deps:
            for file_path in files:
                imports, from_imports = analyze_file_dependencies(file_path)
                all_imports = imports.union(from_imports)
                
                for forbidden_layer in forbidden_deps[source_layer]:
                    forbidden_files = structure[forbidden_layer]
                    
                    for forbidden_file in forbidden_files:
                        try:
                            relative_path = str(forbidden_file.relative_to(file_path.parent.parent))
                        except ValueError:
                            relative_path = str(forbidden_file)
                        
                        module_patterns = [
                            relative_path.replace('/', '.').replace('.py', ''),
                            forbidden_file.stem,
                            forbidden_file.name.replace('.py', '')
                        ]
                        
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
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    platform_specific = {
        'win32api', 'win32con', 'winsound', 'msvcrt',
        'termios', 'tty', 'grp', 'pwd',
        'CoreFoundation', 'Foundation', 'AppKit'
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
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    test_files = []
    for py_file in project_root.rglob('*.py'):
        if 'test' in str(py_file).lower() or py_file.name.startswith('test_'):
            test_files.append(py_file)
    
    production_files = []
    for py_file in project_root.rglob('*.py'):
        if ('test' not in str(py_file).lower() and 
            not py_file.name.startswith('test_') and
            'venv' not in str(py_file) and
            '__pycache__' not in str(py_file)):
            production_files.append(py_file)
    
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
    violations = []
    
    project_root = Path(__file__).parent.parent
    
    dependency_graph = {}
    
    for py_file in project_root.rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        imports, from_imports = analyze_file_dependencies(py_file)
        all_imports = imports.union(from_imports)
        
        module_name = py_file.stem
        dependency_graph[module_name] = []
        
        for imp in all_imports:
            imported_module = imp.split('.')[0] if '.' in imp else imp
            if imported_module != module_name:
                dependency_graph[module_name].append(imported_module)
    
    def has_cycle(graph, start, visited, rec_stack):
        visited[start] = True
        rec_stack[start] = True
        
        for neighbor in graph.get(start, []):
            if neighbor in graph:
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

def test_layer_separation():
    structure = get_project_structure()
    violations = check_layer_dependencies(structure)
    
    if violations:
        pytest.fail(f"Architecture violations found:\n" + "\n".join(violations))

def test_platform_independence():
    violations = check_cross_platform_dependencies()
    
    if violations:
        pytest.fail(f"Platform dependency violations found:\n" + "\n".join(violations))

def test_test_isolation():
    violations = check_test_isolation()
    
    if violations:
        pytest.fail(f"Test isolation violations found:\n" + "\n".join(violations))

def test_no_circular_dependencies():
    violations = check_circular_dependencies()
    
    allowed_cycles = {'manager', 'controller', 'service'}
    
    significant_violations = [v for v in violations 
                            if not any(allowed in v.lower() for allowed in allowed_cycles)]
    
    if significant_violations:
        pytest.fail(f"Circular dependency violations found:\n" + "\n".join(significant_violations))

def test_project_structure_completeness():
    structure = get_project_structure()
    
    total_files = sum(len(files) for files in structure.values())
    
    assert total_files > 10, f"Only {total_files} files found - check analysis patterns"
    
    important_layers = ['business', 'ui']
    for layer in important_layers:
        assert len(structure[layer]) > 0, f"No files found in {layer} layer"

def test_architecture_documentation():
    project_root = Path(__file__).parent.parent
    
    arch_docs = list(project_root.rglob('*ARCHITECTURE*')) + list(project_root.rglob('*architecture*'))
    
    assert len(arch_docs) > 0, "No architecture documentation found. Add ARCHITECTURE.md or similar."

if __name__ == '__main__':
    print("🏗️  Architecture Analysis")
    print("=" * 50)
    
    structure = get_project_structure()
    for layer, files in structure.items():
        print(f"{layer.upper()}: {len(files)} files")
    
    print("\n🔍 Checking Architecture Rules...")
    
    all_violations = []
    
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