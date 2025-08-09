# Thesis LaTeX Generation System

This system automatically generates a standalone LaTeX thesis document from markdown chapter files, with consolidated BibTeX bibliography support.

## Overview

The thesis generation system processes all chapter files from `docs/thesis_report/final/` and combines them into a single, properly formatted LaTeX document suitable for academic submission. The system now includes comprehensive bibliography management using BibTeX.

## Generated Files

- `thesis.tex` - Complete standalone LaTeX document containing all chapters
- `references.bib` - Consolidated BibTeX bibliography file
- `generate_thesis_tex.py` - Python script to generate the LaTeX file  
- `build_thesis.sh` - Enhanced shell script with bibliography compilation
- `THESIS_README.md` - This documentation file

## Usage

### Regenerating the LaTeX file

To regenerate the LaTeX file from the markdown sources:

```bash
python3 generate_thesis_tex.py
```

Or use the enhanced build script that handles the complete compilation process:

```bash
./build_thesis.sh
```

### Compiling to PDF with Bibliography

The build script automatically handles the complete LaTeX compilation sequence including bibliography processing:

```bash
./build_thesis.sh
```

This runs:
1. Generate LaTeX from markdown
2. First LaTeX pass (`pdflatex thesis.tex`)
3. Process bibliography (`bibtex thesis`)
4. Second LaTeX pass (resolve citations)
5. Third LaTeX pass (resolve cross-references)

For manual compilation:
```bash
pdflatex thesis.tex
bibtex thesis
pdflatex thesis.tex
pdflatex thesis.tex
```

## Bibliography System

### Consolidated References
All citations are now consolidated into a single `references.bib` file using standard BibTeX format. This replaces the previous scattered reference system.

### Adding New References
Add new citations to `references.bib`:

```bibtex
@article{AuthorYear,
  title={Title of the Article},
  author={Author Name},
  journal={Journal Name},
  year={2024},
  doi={10.1000/example}
}
```

### Using Citations in Markdown
Use proper citation commands:

```markdown
This is a citation \citep{AuthorYear}.
Multiple citations \citep{Author2020, Author2021}.
In-text citation \cite{AuthorYear} shows that...
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

## Key Features

### Academic LaTeX Formatting
- Complete document structure with title page and table of contents
- Professional formatting suitable for Master's thesis submission
- Comprehensive package imports for mathematics, tables, figures, and code
- **Consolidated bibliography system using natbib and BibTeX**

### Intelligent Content Processing
- Normalizes chapter numbering for consistency
- Fixes relative image paths to work from repository root
- Adds page breaks between chapters
- **Cleans up broken reference links** and converts to proper citations
- Converts markdown to LaTeX using pandoc with citation support

## Migration from Old System

The system automatically handles migration from the previous reference system:
- Broken links to `docs/thesis_report/draft/bibliography.md` are cleaned up
- Inline reference numbers are converted to proper citations where possible
- All references are consolidated into the `references.bib` file

This provides a clean, maintainable bibliography system following academic standards.
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