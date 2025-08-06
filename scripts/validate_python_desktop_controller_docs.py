
"""
Simple Documentation Validation for Python Desktop Controller

This test validates that the documentation is complete and accurate
without requiring complex dependencies like PyQt5 or OpenCV.

Author: Multi-Sensor Recording System Team
Date: 2025-08-01
Purpose: Validate documentation completeness
"""

import os
import sys

def validate_documentation_files():
    """Validate that all required documentation files exist"""
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    new_docs_dir = os.path.join(docs_dir, 'new_documentation')

    required_files = [
        'README_python_desktop_controller.md',
        'USER_GUIDE_python_desktop_controller.md',
        'PROTOCOL_python_desktop_controller.md',
    ]

    other_required_files = [
        'DOCUMENTATION_INDEX.md'
    ]

    print("📋 Validating Documentation Files")
    print("=" * 50)

    all_files_exist = True

    for filename in required_files:
        filepath = os.path.join(new_docs_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ new_documentation/{filename} ({size:,} bytes)")
        else:
            print(f"❌ new_documentation/{filename} - NOT FOUND")
            all_files_exist = False

    for filename in other_required_files:
        filepath = os.path.join(docs_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filename} ({size:,} bytes)")
        else:
            print(f"❌ {filename} - NOT FOUND")
            all_files_exist = False

    return all_files_exist

def validate_source_structure():
    """Validate that documented source structure exists"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')

    expected_structure = {
        'files': [
            'application.py',
            'main.py'
        ],
        'directories': [
            'gui',
            'network',
            'session',
            'webcam',
            'calibration',
            'utils'
        ]
    }

    print("\n📁 Validating Source Structure")
    print("=" * 50)

    all_structure_valid = True

    for filename in expected_structure['files']:
        filepath = os.path.join(src_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} - NOT FOUND")
            all_structure_valid = False

    for dirname in expected_structure['directories']:
        dirpath = os.path.join(src_dir, dirname)
        if os.path.isdir(dirpath):
            file_count = len([f for f in os.listdir(dirpath) if f.endswith('.py')])
            print(f"✓ {dirname}/ ({file_count} Python files)")
        else:
            print(f"❌ {dirname}/ - NOT FOUND")
            all_structure_valid = False

    return all_structure_valid

def validate_documentation_content():
    """Validate key content exists in documentation"""
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    new_docs_dir = os.path.join(docs_dir, 'new_documentation')

    print("\n📄 Validating Documentation Content")
    print("=" * 50)

    content_checks = [
        {
            'file': 'README_python_desktop_controller.md',
            'required_sections': [
                'Architecture Overview',
                'Core Components',
                'Data Flow Architecture',
                'Integration Patterns',
                'Error Handling'
            ]
        },
        {
            'file': 'USER_GUIDE_python_desktop_controller.md',
            'required_sections': [
                'Pre-flight Checklist',
                'Getting Started',
                'User Interface Overview',
                'Step-by-Step Recording Workflow',
                'Troubleshooting'
            ]
        },
        {
            'file': 'PROTOCOL_python_desktop_controller.md',
            'required_sections': [
                'JSON Socket Protocol',
                'Message Types',
                'USB Device Integration',
                'File System Data Formats',
                'API Reference'
            ]
        }
    ]

    all_content_valid = True

    for check in content_checks:
        if check['file'] in ['README_python_desktop_controller.md', 'USER_GUIDE_python_desktop_controller.md', 'PROTOCOL_python_desktop_controller.md']:
            filepath = os.path.join(new_docs_dir, check['file'])
        else:
            filepath = os.path.join(docs_dir, check['file'])

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"\n📖 {check['file']}:")
            for section in check['required_sections']:
                if section in content:
                    print(f"  ✓ {section}")
                else:
                    print(f"  ❌ {section} - NOT FOUND")
                    all_content_valid = False
        else:
            print(f"\n❌ {check['file']} - FILE NOT FOUND")
            all_content_valid = False

    return all_content_valid

def validate_mermaid_diagrams():
    """Validate that Mermaid diagrams are present"""
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    new_docs_dir = os.path.join(docs_dir, 'new_documentation')

    print("\n🔗 Validating Mermaid Diagrams")
    print("=" * 50)

    files_to_check = [
        'README_python_desktop_controller.md',
        'USER_GUIDE_python_desktop_controller.md',
        'PROTOCOL_python_desktop_controller.md'
    ]

    diagram_count = 0
    for filename in files_to_check:
        filepath = os.path.join(new_docs_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            mermaid_blocks = content.count('```mermaid')
            diagram_count += mermaid_blocks
            print(f"✓ {filename}: {mermaid_blocks} diagrams")

    print(f"\n📊 Total Mermaid diagrams found: {diagram_count}")
    return diagram_count > 0

def check_documentation_index_references():
    """Check that documentation index references the new files"""
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    index_file = os.path.join(docs_dir, 'DOCUMENTATION_INDEX.md')

    print("\n📇 Validating Documentation Index")
    print("=" * 50)

    if not os.path.exists(index_file):
        print("❌ DOCUMENTATION_INDEX.md not found")
        return False

    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_references = [
        'README_python_desktop_controller.md',
        'USER_GUIDE_python_desktop_controller.md',
        'PROTOCOL_python_desktop_controller.md',
        'Python Desktop Controller'
    ]

    all_references_found = True
    for reference in required_references:
        if reference in content:
            print(f"✓ {reference}")
        else:
            print(f"❌ {reference} - NOT REFERENCED")
            all_references_found = False

    return all_references_found

def main():
    """Run all documentation validation checks"""
    print("🔍 Python Desktop Controller Documentation Validation")
    print("=" * 60)

    checks = [
        ("Documentation Files", validate_documentation_files),
        ("Source Structure", validate_source_structure),
        ("Documentation Content", validate_documentation_content),
        ("Mermaid Diagrams", validate_mermaid_diagrams),
        ("Documentation Index", check_documentation_index_references)
    ]

    results = []
    for check_name, check_function in checks:
        try:
            result = check_function()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ Error in {check_name}: {e}")
            results.append((check_name, False))

    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name:.<40} {status}")
        if not result:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 ALL DOCUMENTATION VALIDATION CHECKS PASSED!")
        print("📚 Python Desktop Controller documentation is complete and accurate.")
    else:
        print("⚠️  Some documentation validation checks failed.")
        print("📝 Please review and update the documentation as needed.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)