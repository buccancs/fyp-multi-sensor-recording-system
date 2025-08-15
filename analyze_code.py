#!/usr/bin/env python3
"""
Simple Code Analysis Script
===========================

Analyzes the GUI code to identify any placeholder functions, stubs, or non-functioning code.
"""

import ast
import os
from pathlib import Path

def analyze_gui_code():
    """Analyze the GUI code for placeholders and stubs."""
    print("=== Code Analysis ===")
    
    gui_file = Path("PythonApp/gui/main_window.py")
    
    if not gui_file.exists():
        print(f"✗ GUI file not found: {gui_file}")
        return
    
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for common placeholder patterns
    issues = []
    
    # Look for placeholder functions
    placeholder_patterns = [
        "pass",
        "TODO",
        "FIXME", 
        "NotImplemented",
        "raise NotImplementedError",
        "placeholder",
        "stub",
        "# TODO",
        "# FIXME",
    ]
    
    lines = content.split('\n')
    
    print("\n--- Checking for Placeholder Code ---")
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        for pattern in placeholder_patterns:
            if pattern in line_stripped and not line_stripped.startswith('#'):
                if pattern == "pass" and ("except" in lines[i-2:i] or "if" in lines[i-2:i] or "def" in lines[i-2:i]):
                    # Skip pass statements that are likely intentional
                    continue
                issues.append(f"Line {i}: Possible placeholder - '{line_stripped}'")
    
    # Check for function definitions without implementations
    print("\n--- Checking Function Implementations ---")
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function body only contains pass, docstring, or comments
                body_statements = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Constant)]
                
                if len(body_statements) == 1 and isinstance(body_statements[0], ast.Pass):
                    issues.append(f"Function '{node.name}' only contains 'pass' statement")
                elif len(body_statements) == 0:
                    issues.append(f"Function '{node.name}' has empty body")
                    
    except SyntaxError as e:
        print(f"✗ Syntax error in file: {e}")
    
    # Check for button connection issues
    print("\n--- Checking Button Connections ---")
    button_connections = []
    connect_lines = [line for line in lines if '.connect(' in line and 'btn' in line]
    
    for line in connect_lines:
        if 'self._' in line:
            func_name = line.split('self._')[1].split(')')[0]
            button_connections.append(func_name)
    
    print(f"Found {len(button_connections)} button connections:")
    for conn in sorted(set(button_connections)):
        print(f"  - {conn}")
    
    # Check if all connected functions exist
    function_names = []
    for line in lines:
        if line.strip().startswith('def _'):
            func_name = line.strip().split('def ')[1].split('(')[0]
            function_names.append(func_name)
    
    missing_functions = set(button_connections) - set(function_names)
    if missing_functions:
        for func in missing_functions:
            issues.append(f"Button connected to missing function: {func}")
    
    # Report results
    print(f"\n=== Analysis Results ===")
    if issues:
        print(f"Found {len(issues)} potential issues:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("✓ No obvious placeholder code or missing functions found!")
    
    return issues

def check_backend_modules():
    """Check backend modules for stub implementations."""
    print("\n=== Backend Module Analysis ===")
    
    modules_to_check = [
        "PythonApp/session/__init__.py",
        "PythonApp/sensors/__init__.py", 
        "PythonApp/sync/__init__.py",
        "PythonApp/calibration/__init__.py",
        "PythonApp/transfer/__init__.py",
        "PythonApp/security/__init__.py",
        "PythonApp/camera/__init__.py",
    ]
    
    issues = []
    
    for module_path in modules_to_check:
        if not os.path.exists(module_path):
            issues.append(f"Missing module: {module_path}")
            continue
            
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for empty or stub modules
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        non_import_lines = [line for line in lines if not line.startswith('import') and not line.startswith('from')]
        
        if len(non_import_lines) < 5:  # Very minimal implementation
            issues.append(f"Module {module_path} appears to have minimal implementation")
        
        # Check for NotImplementedError
        if "NotImplementedError" in content:
            issues.append(f"Module {module_path} contains NotImplementedError")
    
    if issues:
        print(f"Found {len(issues)} backend module issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Backend modules appear to be properly implemented")
    
    return issues

if __name__ == "__main__":
    gui_issues = analyze_gui_code()
    backend_issues = check_backend_modules()
    
    total_issues = len(gui_issues) + len(backend_issues)
    print(f"\n=== Summary ===")
    print(f"Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("✓ Code analysis complete - no major issues found!")
    else:
        print("Issues found that may need fixing.")