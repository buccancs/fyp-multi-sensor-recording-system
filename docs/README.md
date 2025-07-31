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
- `reference/data-storage-quick-reference.md` - Quick data location guide
- `technical/system-architecture-overview.md` - System overview

### Comprehensive Guides
- `comprehensive/pc-android-ui-guide.md` - Complete UI documentation with screenshots
- `comprehensive/pc-android-logging-guide.md` - Logging systems documentation  
- `comprehensive/pc-android-testing-guide.md` - Testing infrastructure guide

### Integration Guides
- `user-guides/shimmer-pc-integration-guide.md` - Shimmer sensor setup
- `user-guides/shimmer-integration-guide.md` - Android Shimmer integration
- `user-guides/rock-solid-integration-guide.md` - Thermal camera integration

### Technical References
- `technical/data-structure-documentation.md` - Data organization details
- `technical/shimmer3-gsr-plus-comprehensive-documentation.md` - Shimmer technical specs
- `technical/topdon-tc001-comprehensive-documentation.md` - Thermal camera specs
- `technical/rock-solid-networking.md` - Network synchronization details

### API and Schemas
- `api/session_metadata_schema.json` - Session data format
- `api/calibration_session_schema.json` - Calibration data format
- `api/session_log_schema.json` - Event logging format
- `api/processing_metadata_schema.json` - Processing results format

### Quick References
- `reference/file-naming-standards.md` - Naming conventions
- `reference/shimmer3-gsr-plus-quick-reference.md` - Shimmer quick start
- `reference/readme-testing.md` - Testing procedures
- `reference/test-documentation.md` - Test documentation

---

**Note**: This reorganization consolidates 135+ documentation files from across the repository into a clear, navigable structure. Development-stage documents have been preserved in the `/deprecated/` folder for historical reference.