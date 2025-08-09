#!/usr/bin/env python3
"""
Script to generate a standalone LaTeX file from thesis chapter markdown files.
Combines all chapter files in the correct order and converts to LaTeX.
"""

import os
import re
from pathlib import Path
import pypandoc


def read_markdown_file(file_path):
    """Read a markdown file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def clean_markdown_content(content, chapter_num=None):
    """Clean markdown content and ensure proper chapter formatting."""
    # Remove any existing chapter numbering conflicts
    if chapter_num:
        # Replace first # Chapter X or just # X with proper numbering
        content = re.sub(r'^#\s*Chapter\s*\d*[.:]*\s*', f'# Chapter {chapter_num}: ', content, flags=re.MULTILINE)
        content = re.sub(r'^#\s*\d+\s*', f'# Chapter {chapter_num}: ', content, flags=re.MULTILINE)
    
    # Fix relative image paths to be relative to final output
    content = re.sub(r'\]\(\.\./diagrams/', '](docs/diagrams/', content)
    content = re.sub(r'\]\(diagrams/', '](docs/diagrams/', content)
    
    # Fix other relative paths
    content = re.sub(r'\]\(\.\./\.\./diagrams/', '](docs/diagrams/', content)
    
    return content


def combine_chapters():
    """Combine all chapter markdown files in the correct order."""
    thesis_dir = Path('/home/runner/work/bucika_gsr/bucika_gsr/docs/thesis_report/final')
    
    # Define the order of chapters
    chapter_files = [
        ('1.md', 1),
        ('2.md', 2), 
        ('3.md', 3),
        ('4.md', 4),
        ('5.md', 5),
        ('6.md', 6),
        ('appendices.md', None)  # Don't renumber appendices
    ]
    
    combined_content = []
    
    for filename, chapter_num in chapter_files:
        file_path = thesis_dir / filename
        if file_path.exists():
            print(f"Processing {filename}...")
            content = read_markdown_file(file_path)
            content = clean_markdown_content(content, chapter_num)
            combined_content.append(content)
            combined_content.append('\n\\newpage\n\n')  # Add page break between chapters
        else:
            print(f"Warning: {filename} not found, skipping...")
    
    return '\n'.join(combined_content)


def create_latex_document(markdown_content):
    """Convert markdown to LaTeX and wrap in document structure."""
    
    # Convert markdown to LaTeX using pypandoc
    try:
        latex_body = pypandoc.convert_text(
            markdown_content, 
            'latex', 
            format='markdown',
            extra_args=[
                '--wrap=none',
                '--listings',  # Use listings package for code
                '--number-sections',  # Number sections automatically
            ]
        )
    except Exception as e:
        print(f"Error converting with pypandoc: {e}")
        print("Falling back to basic conversion...")
        latex_body = markdown_content  # Fallback to raw markdown
    
    # Create complete LaTeX document structure
    latex_document = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{microtype}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}
\\usepackage{{listings}}
\\usepackage{{fancyhdr}}
\\usepackage{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{booktabs}}
\\usepackage{{longtable}}
\\usepackage{{array}}
\\usepackage{{multirow}}
\\usepackage{{wrapfig}}
\\usepackage{{float}}
\\usepackage{{colortbl}}
\\usepackage{{pdflscape}}
\\usepackage{{tabu}}
\\usepackage{{threeparttable}}
\\usepackage{{threeparttablex}}
\\usepackage{{ulem}}
\\usepackage{{makecell}}

% Page geometry
\\geometry{{
    a4paper,
    total={{170mm,257mm}},
    left=20mm,
    top=20mm,
}}

% Headers and footers
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{Multi-Sensor Recording System for Contactless GSR Prediction Research}}
\\lhead{{\\leftmark}}
\\rfoot{{\\thepage}}

% Hyperref setup
\\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    citecolor=blue,
}}

% Listings setup for code
\\lstset{{
    basicstyle=\\ttfamily\\footnotesize,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\\tiny,
    showstringspaces=false,
}}

\\title{{Multi-Sensor Recording System for Contactless GSR Prediction Research}}
\\author{{Master's Thesis}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle
\\newpage

\\tableofcontents
\\newpage

{latex_body}

\\end{{document}}
"""
    
    return latex_document


def main():
    """Main function to generate the LaTeX thesis file."""
    print("Generating standalone LaTeX thesis file...")
    
    # Combine all chapters
    combined_markdown = combine_chapters()
    
    # Convert to LaTeX
    latex_content = create_latex_document(combined_markdown)
    
    # Write to output file
    output_path = Path('/home/runner/work/bucika_gsr/bucika_gsr/thesis.tex')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✓ LaTeX thesis file generated: {output_path}")
    print(f"✓ File size: {output_path.stat().st_size} bytes")
    
    # Also create a build script
    build_script_path = Path('/home/runner/work/bucika_gsr/bucika_gsr/build_thesis.sh')
    build_script = """#!/bin/bash
# Build script for thesis LaTeX document

echo "Building thesis.tex..."

# Generate the LaTeX file
python3 generate_thesis_tex.py

# Compile with pdflatex (if available)
if command -v pdflatex &> /dev/null; then
    echo "Compiling LaTeX to PDF..."
    pdflatex thesis.tex
    echo "✓ PDF generated: thesis.pdf"
else
    echo "pdflatex not available. LaTeX file ready for compilation."
fi
"""
    
    with open(build_script_path, 'w') as f:
        f.write(build_script)
    
    os.chmod(build_script_path, 0o755)  # Make executable
    print(f"✓ Build script created: {build_script_path}")


if __name__ == "__main__":
    main()