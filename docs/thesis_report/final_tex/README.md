# Bibliography Update README

This directory now contains a comprehensive bibliography system for the thesis.

## Files Updated

### New Files
- `references.bib` - Complete bibliography in BibTeX format containing all academic references
- `thesis_example.tex` - Example LaTeX document showing how to use the bibliography

### Updated Files
All LaTeX files have been updated with proper academic citation keys:
- `Chapter_1.tex` - Updated 16 citations
- `Chapter_2.tex` - Updated 41 citations  
- `Chapter_3.tex` - Updated 66 citations
- `Chapter_4.tex` - Updated 50 citations
- `Chapter_5.tex` - Updated 50 citations
- `Chapter_6.tex` - Updated 2 citations
- `Appendices.tex` - Updated 66 citations
- `shimmer-readme.tex` - Updated 54 citations
- `topdon-readme.tex` - Updated 55 citations

## Changes Made

### 1. Citation Key Conversion
- Converted generic references (`\cite{ref1}`, `\cite{ref2}`, etc.) to proper academic citation keys
- Example: `\cite{ref1}` → `\cite{Boucsein2012}`

### 2. Reference Cleanup
- Removed inline reference sections from the end of each chapter
- Consolidated all references into a single `references.bib` file

### 3. Academic Standards
The bibliography now follows proper academic format with:
- Author names in correct format
- Journal titles, volume, and page numbers
- DOI links where available
- URLs for online resources
- Proper BibTeX entry types (article, book, misc, techreport, etc.)

## Usage

To compile a thesis document using these references:

1. Include `\usepackage{cite}` in your preamble
2. Use `\bibliography{references}` to include the bibliography
3. Choose an appropriate bibliography style: `\bibliographystyle{plain}` or `\bibliographystyle{ieeetr}`
4. Compile with: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`

Example:
```latex
\documentclass{article}
\usepackage{cite}

\begin{document}
% Your content with \cite{CitationKey} references

\bibliographystyle{plain}
\bibliography{references}
\end{document}
```

## Reference Categories

The bibliography contains:
- Core physiological computing references (Boucsein, Picard, etc.)
- Stress measurement and GSR research papers
- System implementation references
- Technical standards and documentation
- Software and hardware documentation

## Citation Key Mapping

Major reference mappings:
- `Boucsein2012` - Primary GSR reference
- `AppleHealthWatch2019` / `SamsungHealth2020` - Consumer devices
- `DriverStressThermal2020` - Thermal stress detection
- `InstantStressSmartphone2019` - Smartphone-based stress detection
- `ContactlessStressThermal2022` - Contactless stress classification
- Implementation files mapped to appropriate system component references

All citations now follow academic standards and can be easily modified or extended.