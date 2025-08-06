# Vale Academic Quality Configuration

## Overview

This project uses Vale for academic quality assurance of markdown files. Vale is a syntax-aware linter for prose that helps maintain consistent, high-quality academic writing across all documentation.

## Configuration

### Main Configuration File

The Vale configuration is located at `.vale.ini` in the project root:

```ini
# Vale configuration for academic quality markdown files
StylesPath = .vale-styles

# Set minimum alert level (suggestion, warning, error)
MinAlertLevel = suggestion

# Global settings
[*]
# Core academic writing styles
BasedOnStyles = Vale

# Markdown-specific configuration
[*.md]
BasedOnStyles = Vale

# Enable specific rules for academic writing
Vale.Spelling = YES
Vale.Repetition = YES
Vale.Terms = YES

# Documentation files (less strict)
[docs/*.md]
BasedOnStyles = Vale

# README files (more lenient)
[README.md]
BasedOnStyles = Vale
```

### Directory Structure

```
.vale-styles/           # Vale styles directory
config/
  vocabularies/
    academic/
      accept.txt        # Project-specific vocabulary
```

### Academic Vocabulary

The `config/vocabularies/academic/accept.txt` file contains 131 project-specific terms including:

- Technical terms: GSR, multisensor, Bluetooth, Android
- Development tools: Kotlin, Python, Gradle, pytest
- Academic concepts: calibration, synchronization, thermal, biometric
- Framework terms: androidx, coroutines, OpenCV, MediaPipe

## Usage

### Basic Commands

Check a specific markdown file:
```bash
vale README.md
```

Check all markdown files:
```bash
vale *.md
```

Check thesis chapters:
```bash
vale "docs\thesis_report\*.md"
```

Check documentation files:
```bash
vale "docs\*.md"
```

### Rule Differentiation

Vale applies different rule sets based on file types:

1. **Thesis Chapters** (`docs/thesis_report/*.md`): Full academic quality checking
2. **Documentation Files** (`docs/*.md`): Less strict rules for technical content
3. **README Files** (`README.md`): Most lenient rules for project overview

### Example Output

```
docs\thesis_report\Chapter_1_Introduction.md
 8:3      error  Did you really mean 'Contactless'?    Vale.Spelling
 54:86    error  Did you really mean 'contactless'?    Vale.Spelling
 947:68   error  'W' is repeated!                      Vale.Repetition
✖ 55 errors, 0 warnings and 0 suggestions in 1 file.
```

## Quality Standards

### Academic Writing Rules

- **Spelling**: Checks for misspelled words with project vocabulary support
- **Repetition**: Identifies repeated words that may indicate editing errors
- **Terms**: Ensures consistent terminology usage

### Alert Levels

- **Suggestion**: Non-blocking quality improvements
- **Warning**: Recommended changes for better readability
- **Error**: Issues that should be addressed for academic quality

## Integration with Development Workflow

### Pre-commit Checks

Add Vale to your pre-commit workflow:
```bash
# Check all modified markdown files
git diff --name-only --cached | grep '\.md$' | xargs vale
```

### CI/CD Integration

Vale can be integrated into continuous integration pipelines to ensure consistent quality across all documentation updates.

### Editor Integration

Vale supports integration with various editors:
- VS Code: Vale extension available
- Vim/Neovim: ALE plugin support
- Emacs: Flycheck integration

## Troubleshooting

### Common Issues

1. **Vocabulary not recognized**: Ensure terms are added to `config/vocabularies/academic/accept.txt`
2. **Style package errors**: Currently using built-in Vale styles only
3. **Path issues**: Use forward slashes in file paths for cross-platform compatibility

### Adding New Terms

To add project-specific terms to the vocabulary:

1. Edit `config/vocabularies/academic/accept.txt`
2. Add one term per line
3. Terms are case-sensitive
4. Restart Vale to reload vocabulary

## Future Enhancements

### Planned Improvements

- Integration with additional style packages (Microsoft, write-good, alex, proselint)
- Custom academic writing rules for thesis formatting
- Automated vocabulary updates from code comments
- Integration with academic citation checking

### Style Package Installation

When additional style packages become available:
```bash
vale sync  # Install configured style packages
```

## Maintenance

### Regular Tasks

1. **Vocabulary Updates**: Add new technical terms as the project evolves
2. **Rule Tuning**: Adjust rule strictness based on document types
3. **Quality Reviews**: Regular checks of thesis chapters and documentation

### Performance Considerations

- Vale processes files quickly but large documents may take longer
- Consider running Vale on changed files only in CI/CD pipelines
- Use appropriate alert levels to balance quality and productivity

## References

- [Vale Documentation](https://vale.sh/)
- [Academic Writing Guidelines](docs/ACADEMIC_QA_WORKFLOW.md)
- [Project Changelog](../changelog.md)

---

*This documentation is maintained as part of the bucika_gsr project's commitment to academic quality and comprehensive documentation standards.*