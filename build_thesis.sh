#!/bin/bash
# Build script for thesis LaTeX document

echo "Building thesis.tex..."

# Generate the LaTeX file
python3 generate_thesis_tex.py

# Compile with pdflatex (if available)
if command -v pdflatex &> /dev/null; then
    echo "Compiling LaTeX to PDF with bibliography..."
    
    # First pass
    pdflatex thesis.tex
    
    # Process bibliography if bibtex is available
    if command -v bibtex &> /dev/null; then
        echo "Processing bibliography..."
        bibtex thesis
        
        # Second pass (resolve citations)
        pdflatex thesis.tex
        
        # Third pass (resolve references)
        pdflatex thesis.tex
    else
        echo "bibtex not available. Bibliography may not be processed correctly."
        # Just do a second pass for cross-references
        pdflatex thesis.tex
    fi
    
    echo "✓ PDF generated: thesis.pdf"
else
    echo "pdflatex not available. LaTeX file ready for compilation."
fi
