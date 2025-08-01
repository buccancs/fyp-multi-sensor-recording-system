# Documentation Directory

This directory contains all consolidated documentation for the Multi-Sensor Synchronized Recording System. The documentation has been reorganized into clear categories for better navigation and maintenance.

## 📁 Directory Structure

### `/api/`
- **JSON schema files** defining data structures and APIs
- Schema validation files for session data, calibration data, and metadata
- Use these when integrating with the system or validating data formats

### `/reference/`
- **Quick reference guides** and lookup documentation
- File naming standards and conventions
- Testing documentation and procedures
- Essential reference materials for daily use

### `/technical/`
- **Comprehensive technical documentation** including:
  - System architecture and design documents
  - Component-specific technical guides (Shimmer, Thermal cameras, etc.)
  - Networking and synchronization technical details
  - Data structure specifications
  - Requirements analysis and technology selection

### `/user-guides/`
- **Step-by-step user guides** for:
  - System setup and configuration
  - Integration guides for various components
  - End-user operational procedures
  - Getting started tutorials

### `/comprehensive/`
- **Complete system documentation** covering:
  - PC/Android UI comprehensive guide with screenshots
  - PC/Android logging systems documentation
  - PC/Android testing infrastructure guide
  - Cross-platform integration documentation

### `/deprecated/`
- **Development-stage documents** that are no longer actively maintained:
  - Milestone completion reports
  - Development implementation summaries  
  - Architecture diagrams from development phases
  - Progress tracking and planning documents
  - Historical development artifacts

## 🔍 Finding What You Need

**New Users**: Start with `/user-guides/user-guide.md`

**Comprehensive Guides**: See `/comprehensive/` for complete PC/Android documentation

**Developers**: Check `/technical/` for architecture and `/api/` for schemas

**Quick Answers**: Look in `/reference/` for fast lookup information

**Historical Context**: See `/deprecated/` for development history

## 📋 Document Categories

All documents have been categorized based on their current relevance and target audience:

- **Active Documentation**: User guides, technical references, and API documentation that is actively maintained
- **Reference Materials**: Quick lookups, standards, and testing procedures
- **Deprecated Content**: Development milestones, progress reports, and outdated implementation details

This organization ensures that current, relevant documentation is easily accessible while preserving historical development artifacts for reference.

## 📚 Key Documents by Category

### Essential Starting Points
- `user-guides/user-guide.md` - Main user documentation
- `comprehensive/README.md` - Complete PC/Android documentation suite
- `new_documentation/session-management-quick-reference.md` - Session operations and data location guide
- `technical/system-architecture-overview.md` - System overview

### Comprehensive Guides
- `new_documentation/` - Complete Android Mobile Application documentation with technical guides, user manuals, and protocol specifications

### Integration Guides
- `new_documentation/USER_GUIDE_shimmer3_gsr_plus.md` - Shimmer3 GSR+ practical user guide
- `user-guides/rock-solid-integration-guide.md` - Thermal camera integration

### Technical References
- `technical/data-structure-documentation.md` - Data organization details
- `new_documentation/README_shimmer3_gsr_plus.md` - Shimmer3 GSR+ technical deep-dive
- `technical/topdon-tc001-comprehensive-documentation.md` - Thermal camera specs

### API and Schemas
- `new_documentation/session_metadata_schema.json` - Session data format
- `new_documentation/calibration_session_schema.json` - Calibration data format
- `new_documentation/session_log_schema.json` - Event logging format
- `api/processing_metadata_schema.json` - Processing results format

### Quick References
- `reference/file-naming-standards.md` - Naming conventions
- `new_documentation/INDEX.md` - Shimmer3 GSR+ comprehensive documentation index
- `reference/readme-testing.md` - Testing procedures
- `reference/test-documentation.md` - Test documentation

---

**Note**: This reorganization consolidates 135+ documentation files from across the repository into a clear, navigable structure. Development-stage documents have been preserved in the `/deprecated/` folder for historical reference.