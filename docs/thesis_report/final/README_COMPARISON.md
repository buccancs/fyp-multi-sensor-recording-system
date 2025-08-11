# Content Comparison Tool for Markdown and LaTeX Files

## Overview

This directory contains both Markdown (`.md`) and LaTeX (`.tex`) versions of the thesis chapters and appendices. The `compare_md_tex.py` script provides automated comparison between corresponding files to ensure content synchronization and identify discrepancies.

## Files Structure

### Markdown Files (Source)
- `1.md` - `6.md`: Main thesis chapters (Introduction, Background, Requirements, Design, Evaluation, Conclusion)
- `appendix_*.md`: Appendices with detailed technical documentation
- `references.md`: Bibliography references

### LaTeX Files (Compiled Output)
- `latex/1.tex` - `6.tex`: LaTeX versions of main chapters
- `latex/appendix_*.tex`: LaTeX versions of appendices
- `latex/main.tex`: Main LaTeX document structure
- `latex/references.bib`: BibTeX bibliography

## Using the Comparison Tool

### Basic Usage

```bash
# Compare all corresponding .md and .tex files
python compare_md_tex.py

# Compare specific file(s) using pattern matching
python compare_md_tex.py --file-pattern "1.md"
python compare_md_tex.py --file-pattern "appendix_a"

# Show detailed differences
python compare_md_tex.py --verbose

# Use different base directory
python compare_md_tex.py --base-dir /path/to/files
```

### Command Line Options

- `--verbose, -v`: Show detailed line-by-line differences
- `--file-pattern PATTERN, -p PATTERN`: Filter files by pattern
- `--base-dir DIR, -d DIR`: Specify base directory (default: current directory)
- `--help, -h`: Show usage information

## Understanding the Results

### Similarity Levels

The tool calculates content similarity between normalized Markdown and LaTeX versions:

- **✅ High Similarity (>95%)**: Content is well-synchronized with only minor formatting differences
- **🟡 Medium Similarity (85-95%)**: Some content differences exist, may need review
- **🔴 Low Similarity (<85%)**: Significant content differences requiring attention

### Common Types of Differences

1. **Format-Specific Markup**
   - Markdown: `# Header`, `**bold**`, `[1]` (citations)
   - LaTeX: `\section{Header}`, `\textbf{bold}`, `\citep{ref1}`

2. **Content Structure**
   - Different organization of sections
   - Additional content in one format
   - Missing content in either version

3. **Technical Elements**
   - Code blocks formatting
   - Figure/table references
   - Mathematical expressions

### Status Icons

- **✅**: Content synchronized (>95% similarity)
- **🟡**: Minor differences (85-95% similarity)
- **🔴**: Major differences (<85% similarity)
- **📏**: Significant length difference (>30%)

## Current Status (Latest Run Results)

Based on the latest comparison run:

### Summary
- **Total file pairs**: 16
- **Files with differences**: 16 (all files have some differences)
- **Files in sync**: 0
- **High similarity (>95%)**: 4 files
- **Medium similarity (85-95%)**: 10 files
- **Low similarity (<85%)**: 2 files

### Critical Files Requiring Attention

1. **2.md ↔ 2.tex** (27.0% similarity)
   - Chapter 2: Background and Research Context
   - Significant length difference (52.3%)
   - **Action needed**: Major content synchronization required

2. **appendix_f_code_listings.md ↔ appendix_F.tex** (0.2% similarity)
   - Code listings appendix
   - LaTeX version is mostly a placeholder
   - **Action needed**: Full conversion from Markdown to LaTeX required

### Files with Good Synchronization (>95% similarity)

1. **appendix_a_system_manual.md ↔ appendix_A.tex** (98.92%)
2. **appendix_b_user_manual.md ↔ appendix_B.tex** (96.35%)
3. **appendix_c_supporting_documentation.md ↔ appendix_C.tex** (95.38%)
4. **appendix_h_reference_index.md ↔ appendix_H.tex** (97.96%)

## Maintenance Workflow

### For Content Authors

1. **Primary editing**: Make changes in Markdown files (`.md`)
2. **Synchronization check**: Run comparison tool before final publication
3. **LaTeX updates**: Update corresponding `.tex` files to match content changes
4. **Validation**: Re-run comparison to verify synchronization

### For Content Reviewers

1. **Quality check**: Use comparison tool to identify synchronization issues
2. **Content validation**: Focus on files with low similarity scores
3. **Format consistency**: Ensure citations, references, and formatting are consistent

## Technical Details

### Content Normalization

The tool normalizes both formats before comparison:

**Markdown Normalization:**
- Headers (`# Title` → `Title`)
- Bold/italic markup (`**text**` → `text`)
- Citations (`[1]` → `[1]`)
- List markers (`-` → `-`)

**LaTeX Normalization:**
- Commands (`\section{Title}` → `Title`)
- Formatting (`\textbf{text}` → `text`)
- Citations (`\citep{ref1}` → `[ref1]`)
- Comments (`% comment` → removed)
- Environments (`\begin{itemize}` → removed)

### Limitations

1. **Complex LaTeX structures**: Advanced LaTeX features may not normalize perfectly
2. **Mathematical expressions**: LaTeX math vs. Markdown math handling differs
3. **Code blocks**: Different syntax highlighting and formatting approaches
4. **Figures/tables**: Complex table structures and figure positioning

## Troubleshooting

### High False Positive Rate

If the tool reports differences for files that appear synchronized:

1. Check for invisible characters or encoding issues
2. Verify citation formats match between versions
3. Look for extra whitespace or line ending differences

### Missing File Pairs

If expected file pairs aren't found:

1. Verify file naming conventions
2. Check that both `.md` and corresponding `.tex` files exist
3. Ensure proper directory structure (`latex/` subdirectory for `.tex` files)

### Performance Issues

For large files or many comparisons:

1. Use `--file-pattern` to limit scope
2. Avoid `--verbose` for initial runs
3. Check available memory for very large appendices

## Future Enhancements

Potential improvements to the comparison tool:

1. **Automated synchronization**: Scripts to update LaTeX from Markdown changes
2. **Citation validation**: Cross-reference citation keys between formats
3. **Figure/table tracking**: Verify all references are maintained
4. **Integration with build process**: Automatic comparison during LaTeX compilation
5. **Configuration files**: Customizable normalization rules for specific content types

## Contributing

When adding new chapters or appendices:

1. Create both `.md` and `.tex` versions
2. Follow existing naming conventions
3. Update the `FileMapper` class in `compare_md_tex.py` if needed
4. Run comparison tool to verify initial synchronization
5. Document any format-specific considerations

## References

- [Markdown Specification](https://spec.commonmark.org/)
- [LaTeX Documentation](https://www.latex-project.org/help/documentation/)
- [UCL Thesis Guidelines](https://www.ucl.ac.uk/students/academic-support/)