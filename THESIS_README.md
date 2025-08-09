# Thesis LaTeX Generation

This directory contains tools to generate a standalone LaTeX file from the thesis chapter markdown files.

## Generated Files

- `thesis.tex` - Complete standalone LaTeX document containing all chapters
- `generate_thesis_tex.py` - Python script to generate the LaTeX file
- `build_thesis.sh` - Shell script to regenerate and compile the thesis

## Usage

### Regenerating the LaTeX file

To regenerate the LaTeX file from the markdown sources:

```bash
python3 generate_thesis_tex.py
```

Or use the build script:

```bash
./build_thesis.sh
```

### Compiling to PDF

If you have LaTeX installed (pdflatex), you can compile the generated file to PDF:

```bash
pdflatex thesis.tex
```

You may need to run pdflatex multiple times to resolve cross-references and generate the table of contents properly:

```bash
pdflatex thesis.tex
pdflatex thesis.tex
```

## Source Files

The script automatically combines the following chapter files from `docs/thesis_report/final/`:

1. `1.md` - Chapter 1: Introduction
2. `2.md` - Chapter 2: Background and Literature Review
3. `3.md` - Chapter 3: Requirements
4. `4.md` - Chapter 4: Design and Implementation
5. `5.md` - Chapter 5: Evaluation and Testing
6. `6.md` - Chapter 6: Conclusions and Evaluation
7. `appendices.md` - Appendices

## LaTeX Document Features

The generated LaTeX document includes:

- Proper document structure with title page and table of contents
- Academic formatting suitable for thesis submission
- Hyperlinked cross-references and citations
- Code syntax highlighting using the listings package
- Support for figures and tables
- Proper page headers and numbering
- Standard academic packages for mathematics, tables, and graphics

## Dependencies

- Python 3.x
- pypandoc (automatically installed by the script if needed)
- LaTeX distribution (optional, for PDF compilation)

## Notes

- The script automatically fixes relative image paths to be relative to the repository root
- Chapter numbering is normalized to ensure consistency
- Page breaks are inserted between chapters
- The document uses standard academic LaTeX formatting suitable for submission