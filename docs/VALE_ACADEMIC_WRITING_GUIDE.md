# Vale Academic Writing Guide

## Overview

Vale is now configured for the bucika_gsr repository to enforce academic writing standards. This guide explains how to use Vale for maintaining high-quality academic documentation.

## Configuration

Vale is configured via `.vale.ini` with academic writing rules focusing on:

- Clear, precise, and practical writing style
- Academic conventions and formatting
- Consistent terminology and style
- Component-first documentation approach

### Style Rules Applied

1. **Vale Core Rules**: Basic spelling and repetition checks
2. **Microsoft Writing Style Guide**: Professional writing standards
3. **write-good**: General writing improvement suggestions

### Documentation Types and Rules

#### Thesis Report (`docs/thesis_report/*.md`)
- **Strictest rules** for academic rigor
- First-person usage warnings
- Contractions are errors
- Passive voice warnings
- Sentence length monitoring

#### Technical Documentation (`docs/*.md`)
- **Moderate rules** for technical clarity
- Relaxed first-person usage
- Contractions allowed
- No passive voice restrictions

#### Root Documentation (`*.md`)
- **Suggestion level** for flexibility
- General writing improvement suggestions

## Usage

### Command Line

Run Vale on specific files:
```bash
vale docs/thesis_report/Chapter_1_Introduction.md
```

Run Vale on all markdown files:
```bash
vale docs/
```

Run Vale on thesis only:
```bash
vale docs/thesis_report/
```

### Pre-commit Integration

Vale runs automatically on commit for all `.md` files when pre-commit is installed:

```bash
pre-commit install
```

### Manual Check Before Commit

```bash
pre-commit run vale --files path/to/file.md
```

## Common Academic Writing Issues

Vale will help identify:

1. **Wordiness**: "in order to" → "to"
2. **Passive Voice**: "The experiment was conducted" → "We conducted the experiment"
3. **First Person Overuse**: Excessive use of "I" or "we" in formal sections
4. **Contractions**: "don't" → "do not" in formal writing
5. **Sentence Length**: Complex sentences over 30 words
6. **Repetition**: Repeated words or phrases
7. **Spelling**: Technical terms and proper nouns

## Academic Writing Best Practices

### For Thesis Chapters

- Use active voice when possible
- Keep sentences concise and clear
- Avoid contractions in formal sections
- Use first person sparingly and strategically
- Maintain consistent terminology

### For Technical Documentation

- Focus on clarity and precision
- Use active voice for instructions
- Allow reasonable use of first person for explanations
- Maintain component-first approach

## Customization

### Adding Technical Terms

To add project-specific terms to the Vale vocabulary:

1. Create `styles/config/vocabularies/Base/accept.txt`
2. Add one term per line
3. Terms will be accepted in all contexts

### Adjusting Rule Severity

Edit `.vale.ini` to change rule severity:
- `error`: Must be fixed
- `warning`: Should be fixed
- `suggestion`: Consider fixing
- `NO`: Disable rule

## Integration with Existing Tools

Vale works alongside existing linting tools:
- **markdownlint**: Handles markdown formatting
- **Vale**: Handles writing style and academic conventions
- **Pre-commit**: Orchestrates all linting tools

## Troubleshooting

### Common Issues

1. **Style not found**: Ensure `styles/` directory contains required style packages
2. **Config errors**: Check `.vale.ini` syntax
3. **False positives**: Add terms to vocabulary or adjust rule severity

### Getting Help

- Vale documentation: https://vale.sh/docs/
- Microsoft Style Guide: https://docs.microsoft.com/en-us/style-guide/
- Project-specific issues: Adjust `.vale.ini` configuration

## Academic Writing Workflow

1. **Draft**: Write content focusing on ideas
2. **Vale Check**: Run Vale to identify writing issues
3. **Revise**: Address Vale suggestions systematically
4. **Review**: Ensure changes maintain academic tone
5. **Commit**: Pre-commit hooks will catch remaining issues

This configuration supports the thesis project's focus on clear, precise, and practical academic writing while maintaining the established component-first documentation approach.