# GitHub Copilot Academic Writing Configuration

This document provides comprehensive guidelines for using GitHub Copilot with academic writing standards in this project.

## Academic Writing Prompts and Comments

Use these comment patterns in your markdown files to guide Copilot for academic quality:

```markdown
<!-- ACADEMIC_STYLE: Use formal academic tone, avoid contractions, prefer active voice -->
<!-- CITATION_FORMAT: Use APA style citations -->
<!-- TECHNICAL_TERMS: Maintain consistency with GSR, multisensor, Bluetooth, Android terminology -->
<!-- STRUCTURE: Follow academic paper structure with clear sections -->
```

## Custom Copilot Instructions

Add these instructions at the top of academic markdown files:

```markdown
<!--
COPILOT ACADEMIC WRITING INSTRUCTIONS:
1. Use formal academic language and avoid contractions
2. Prefer active voice over passive voice
3. Use precise technical terminology consistently
4. Structure arguments logically with clear transitions
5. Support claims with evidence and citations
6. Maintain objective, scholarly tone
7. Use clear, concise sentences (max 25 words)
8. Follow academic formatting conventions
9. Include proper section headings and numbering
10. Ensure coherent flow between paragraphs
-->
```

## Language-Specific Configurations

### Research Papers
```markdown
<!-- COPILOT_MODE: research_paper -->
<!-- STYLE: APA, formal, evidence-based -->
<!-- SECTIONS: abstract, introduction, methodology, results, discussion, conclusion -->
```

### Technical Documentation
```markdown
<!-- COPILOT_MODE: technical_docs -->
<!-- STYLE: clear, precise, step-by-step -->
<!-- AUDIENCE: technical professionals, researchers -->
```

### Literature Reviews
```markdown
<!-- COPILOT_MODE: literature_review -->
<!-- STYLE: analytical, comparative, synthesizing -->
<!-- FOCUS: critical evaluation, gap identification -->
```

## Project-Specific Academic Templates

### Thesis Template
```markdown
<!-- THESIS_TEMPLATE -->
<!--
Chapter Structure:
1. Introduction (research problem, questions, significance)
2. Literature Review (current state, gaps, theoretical framework)
3. Methodology (approach, data collection, analysis methods)
4. Results (findings, data presentation, statistical analysis)
5. Discussion (interpretation, implications, limitations)
6. Conclusion (summary, contributions, future work)
-->
```

### Academic Paper Template
```markdown
<!-- PAPER_TEMPLATE -->
<!--
Academic Paper Structure:
- Title: Clear, specific, informative
- Abstract: Background, methods, results, conclusions
- Keywords: 3-6 relevant terms
- Introduction: Context, problem, objectives
- Methods: Reproducible procedures
- Results: Objective findings
- Discussion: Interpretation, significance
- References: Complete, formatted consistently
-->
```

## Academic Content Structure Templates

### Abstract Template
```markdown
## Abstract
<!-- 
Academic requirements:
- 150-250 words
- Background, methods, results, conclusions
- No citations in abstract
- Formal tone
-->
```

### Introduction Template
```markdown
## Introduction
<!-- 
Copilot guidelines:
- Start with broad context, narrow to specific problem
- Clear research questions/hypotheses
- Justify significance of research
- Preview paper structure
-->
```

## Copilot Chat Prompts for Academic Writing

Use these prompts in Copilot Chat for academic assistance:

- `/fix "Improve this paragraph for academic writing standards, ensuring formal tone and clear argumentation"`
- `/explain "Analyze this methodology section for completeness and academic rigor"`
- `/generate "Create an academic abstract for this research following standard structure"`
- `/optimize "Enhance this conclusion to better synthesize findings and suggest future research"`

## Integration with Vale

This configuration works alongside the existing Vale setup:

```markdown
<!-- 
QUALITY_CHECKS:
1. Use GitHub Copilot for content generation
2. Run Vale for style and grammar checking
3. Manual review for academic standards
4. Peer review for technical accuracy
-->

<!-- Vale configuration reference: .vale.ini -->
<!-- Academic vocabulary: GSR, multisensor, Bluetooth, Android, calibration, synchronization, thermal, biometric -->
```

## Quality Assurance Workflow

```markdown
<!-- 
ACADEMIC_QA_WORKFLOW:
1. Draft with Copilot assistance
2. Vale style checking
3. Manual academic review
4. Peer feedback incorporation
5. Final proofreading
6. Citation verification
7. Format compliance check
-->
```

## Project-Specific Technical Terms

Maintain consistency with these technical terms:
- GSR (Galvanic Skin Response)
- multisensor
- Bluetooth
- Android
- calibration
- synchronization
- thermal
- biometric
- real-time
- data acquisition
- sensor fusion

## Best Practices

1. **Formal Tone**: Always use formal academic language
2. **Active Voice**: Prefer active over passive voice
3. **Precision**: Use precise technical terminology
4. **Evidence**: Support all claims with evidence
5. **Structure**: Follow logical argument structure
6. **Citations**: Include proper citations in APA format
7. **Clarity**: Write clear, concise sentences
8. **Consistency**: Maintain consistent terminology throughout
9. **Objectivity**: Maintain objective, scholarly tone
10. **Flow**: Ensure coherent transitions between ideas