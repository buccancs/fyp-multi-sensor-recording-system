#!/usr/bin/env python3
"""
Quick fix script to correct imports in generated Android tests
"""

import os
from pathlib import Path

def fix_test_imports(file_path: Path):
    """Fix imports in a single test file."""
    try:
        content = file_path.read_text()
        
        # Replace kotlin.test imports with JUnit imports
        content = content.replace("import kotlin.test.assertEquals", "")
        content = content.replace("import kotlin.test.assertNotNull", "")  
        content = content.replace("import kotlin.test.assertTrue", "")
        content = content.replace("import kotlin.test.assertFalse", "")
        content = content.replace("import kotlin.test.*", "")
        
        # Add JUnit imports if not present
        if "import org.junit.Assert.*" not in content:
            # Find the imports section and add JUnit
            lines = content.split('\n')
            import_index = -1
            for i, line in enumerate(lines):
                if line.startswith("import javax.inject.Inject"):
                    import_index = i
                    break
            
            if import_index >= 0:
                lines.insert(import_index + 1, "import org.junit.Assert.*")
                content = '\n'.join(lines)
        
        file_path.write_text(content)
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all Android test files."""
    
    repo_root = Path(__file__).parent
    test_dir = repo_root / "AndroidApp" / "src" / "test" / "java" / "com" / "multisensor" / "recording"
    
    if not test_dir.exists():
        print("Test directory not found")
        return 1
    
    # Find all test files
    test_files = list(test_dir.rglob("*Test.kt"))
    print(f"Found {len(test_files)} test files to fix")
    
    fixed_count = 0
    for test_file in test_files:
        if fix_test_imports(test_file):
            fixed_count += 1
    
    print(f"Fixed {fixed_count}/{len(test_files)} test files")
    return 0

if __name__ == "__main__":
    exit(main())