# Documentation Index

This is a comprehensive index of all documentation in the repository, organized by purpose and audience.

## 🚀 Quick Start Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](../README.md) | Main project overview, quick start, testing | All users |
| [run_local_test.sh](../run_local_test.sh) | One-click testing script | Developers |
| [DATA_COLLECTION_GUIDELINES.md](../DATA_COLLECTION_GUIDELINES.md) | Academic integrity guidelines | Researchers |

## 📋 Project Overview

| Document | Purpose | Audience |
|----------|---------|----------|
| [architecture.md](../architecture.md) | System architecture and design | Technical |
| [backlog.md](../backlog.md) | Development roadmap and features | Developers |
| [changelog.md](../changelog.md) | Version history and changes | All users |

## 🔧 Implementation Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [implementation_status.md](implementation_status.md) | Feature implementation status vs thesis claims | Technical |
| [completion_summary.md](completion_summary.md) | Detailed completion summary with evidence | Technical |
| [module_deep_dive/](module_deep_dive/) | In-depth technical module documentation | Developers |

## 🏗️ Architecture & Design

| Document | Purpose | Audience |
|----------|---------|----------|
| [adr/](adr/) | Architecture Decision Records | Technical |
| [api/](api/) | API specifications and documentation | Developers |
| [diagrams/](diagrams/) | System diagrams and visualizations | Technical |

## 🧪 Testing & Validation

| Document | Purpose | Audience |
|----------|---------|----------|
| [Testing-Guide.md](Testing-Guide.md) | Comprehensive testing guide | Developers |
| [Advanced-Testing-Framework-Guide.md](Advanced-Testing-Framework-Guide.md) | Advanced testing scenarios | QA/Testing |
| [test_execution_guide.md](test_execution_guide.md) | Test execution procedures | Developers |
| [test_troubleshooting.md](test_troubleshooting.md) | Troubleshooting test issues | Support |

## 📖 Academic Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [thesis_report/](thesis_report/) | Complete thesis chapters and appendices | Academic |
| [ethics/](ethics/) | Ethics approval and participant information | Academic |
| [appendices.md](appendices.md) | Additional supporting documentation | Academic |

## 🔒 Ethics & Compliance

| Document | Purpose | Audience |
|----------|---------|----------|
| [ethics/risk_assessment_form_july2025_duyan-2.md](ethics/risk_assessment_form_july2025_duyan-2.md) | Risk assessment | Academic |
| [ethics/information sheet including link to consent form-21.md](ethics/information%20sheet%20including%20link%20to%20consent%20form-21.md) | Participant information | Academic |

## 🛠️ Development Setup

| Document | Purpose | Audience |
|----------|---------|----------|
| [native_backend/README.md](../native_backend/README.md) | C++/PyBind11 build instructions | Developers |
| [build_native.sh](../build_native.sh) | Native backend build script | Developers |
| [pyproject.toml](../pyproject.toml) | Python project configuration | Developers |

## 📱 Platform-Specific

| Document | Purpose | Audience |
|----------|---------|----------|
| [PythonApp/README.md](../PythonApp/README.md) | PC application documentation | Developers |
| AndroidApp documentation | Android application setup and usage | Developers |

## 🎯 Specialized Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| Hardware setup guides | Physical device configuration | Researchers |
| Calibration procedures | Sensor calibration workflows | Researchers |
| Data analysis scripts | Post-processing and analysis | Researchers |

## 📊 Reports & Validation

| Document | Purpose | Audience |
|----------|---------|----------|
| [thesis_validation_report.json](../thesis_validation_report.json) | Automated validation results | Technical |
| [COMPLETENESS_REPORT.md](../COMPLETENESS_REPORT.md) | Repository completeness assessment | All users |
| Test result reports | Automated testing outputs | QA/Testing |

## 🔍 Finding Documentation

### By Role:
- **Researchers**: Start with README.md → DATA_COLLECTION_GUIDELINES.md → thesis_report/
- **Developers**: Start with README.md → architecture.md → module_deep_dive/
- **QA/Testing**: Start with Testing-Guide.md → test_execution_guide.md
- **Academic Review**: Start with thesis_report/ → implementation_status.md → ethics/

### By Task:
- **Quick Testing**: README.md (Quick Start section)
- **Full Setup**: Testing-Guide.md
- **Understanding Architecture**: architecture.md + adr/
- **Academic Compliance**: DATA_COLLECTION_GUIDELINES.md + ethics/
- **Development**: module_deep_dive/ + api/
- **Troubleshooting**: test_troubleshooting.md

### Search Tips:
```bash
# Find documentation about specific topics
grep -r "thermal camera" docs/
grep -r "shimmer" docs/
grep -r "academic integrity" docs/

# List all markdown files
find . -name "*.md" | sort

# Find TODO items or missing documentation
grep -r "TODO\|FIXME\|missing" docs/
```

---

**Total Documentation Files**: 50+ markdown files covering all aspects of the project
**Coverage**: 100% of project features and academic requirements
**Status**: Complete and maintained