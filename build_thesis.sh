#!/bin/bash
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
