# Thesis LaTeX Build Instructions

This directory contains the LaTeX sources for the thesis chapters and a master build file.

## Files
- Master file: `docs/thesis_report/final/latex/main.tex`
- Converted chapters (selected):
  - `docs/thesis_report/final/4.tex` (Chapter 4)
  - `docs/thesis_report/final/6.tex` (Chapter 6)
  - `docs/thesis_report/final/latex/chapter2.tex` (Chapter 2 in latex subfolder)
  - Other chapters (e.g., 1.tex, 3.tex) will be included as available.

## Build
You can build the thesis PDF using a LaTeX distribution (TeX Live/MiKTeX):

1. Change directory to `docs/thesis_report/final/latex`.
2. Run:
   - `pdflatex main.tex`
   - `bibtex main` (optional; enables references via `references.bib`)
   - `pdflatex main.tex`
   - `pdflatex main.tex`

Notes:
- main.tex currently includes Chapters 4 and 6. Chapter 2 and others will be included as they are converted/standardized.
- The bibliography is referenced at `../../../../references.bib`. Ensure your toolchain can resolve this path or copy the file locally.
- Required packages are already declared in main.tex: `graphicx`, `amsmath`, `amssymb`, `siunitx` (or `textcomp`), and `hyperref`.
- Some figure assets referenced in Chapter 4 may not exist yet. Provide assets or comment out includes to avoid build failures.

## TODOs
- Map numeric citations `[n]` in chapter sources to proper `\cite{...}` keys in a centralized BibTeX file.
- Validate symbol rendering for `\texttimes`/`\textmu` (provided via siunitx or textcomp).
- Standardize chapter file locations (prefer `docs/thesis_report/final/*.tex`).

## Exclusions
- Do not include `external/` or `docs/generated_docs` in any build artifacts.


## Appendices

The appendices have been converted to LaTeX and are included from the thesis master at `docs/thesis_report/final/latex/main.tex` after a `\appendix` directive.

- Location: `docs/thesis_report/final/latex/`
- Files:
  - `appendix_A.tex` (System Manual)
  - `appendix_B.tex` (User Manual)
  - `appendix_C.tex` (Supporting Documentation)
  - `appendix_D.tex` (Test Reports)
  - `appendix_E.tex` (Evaluation Data)
  - `appendix_F.tex` (Code Listings — TODO placeholder)
  - `appendix_G.tex` (Diagnostic Figures — analysis only)
  - `appendix_H.tex` (Consolidated Technical Reference)
  - `appendix_I.tex` (Deprecated — content migrated to Appendix Z)
  - `appendix_Z.tex` (Consolidated Figures)

Notes:
- Several appendices currently wrap Markdown content in LaTeX `verbatim` blocks for quick inclusion. These will be refined to proper LaTeX lists/tables and `\cite{}` references in a follow-up pass.
- Mermaid diagram of the LaTeX structure (including appendices) is available at `docs/diagrams/mermaid_thesis_appendices.mmd`.
- Build remains the same: run `pdflatex` on `main.tex` as described above.


## Mermaid Diagrams Rendering in LaTeX

We now render Mermaid diagrams directly in LaTeX using the `mermaid` package.

Build requirements:
- LaTeX: Enable shell-escape when compiling (required for external tools).
- Node.js 16+ installed and available on PATH.
- Mermaid CLI (mmdc): `npm install -g @mermaid-js/mermaid-cli`

Compile steps (example with MiKTeX/TeX Live):
- From `docs\thesis_report\final\latex`:
  - `pdflatex -shell-escape main.tex`
  - `bibtex main` (if bibliography used)
  - `pdflatex -shell-escape main.tex`
  - `pdflatex -shell-escape main.tex`

Notes:
- Mermaid examples are included in Appendix Z under "Rendered Mermaid Diagrams (LaTeX)".
- If compilation fails for Mermaid, verify Node + mmdc installation and that `-shell-escape` is used.
- Exclusions remain: do not include `external/` or `docs/generated_docs` in any build artifacts.
