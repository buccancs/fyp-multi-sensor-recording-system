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

### `/deprecated/`
- **Development-stage documents** that are no longer actively maintained:
  - Milestone completion reports
  - Development implementation summaries  
  - Architecture diagrams from development phases
  - Progress tracking and planning documents
  - Historical development artifacts

## 🔍 Finding What You Need

**New Users**: Start with `/user-guides/USER_GUIDE.md`

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
- `user-guides/USER_GUIDE.md` - Main user documentation
- `reference/DATA_STORAGE_QUICK_REFERENCE.md` - Quick data location guide
- `technical/SYSTEM_ARCHITECTURE.md` - System overview

### Integration Guides
- `user-guides/SHIMMER_PC_INTEGRATION_GUIDE.md` - Shimmer sensor setup
- `user-guides/SHIMMER_INTEGRATION_GUIDE.md` - Android Shimmer integration
- `user-guides/ROCK_SOLID_INTEGRATION_GUIDE.md` - Thermal camera integration

### Technical References
- `technical/DATA_STRUCTURE_DOCUMENTATION.md` - Data organization details
- `technical/SHIMMER3_GSR_PLUS_COMPREHENSIVE_DOCUMENTATION.md` - Shimmer technical specs
- `technical/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md` - Thermal camera specs
- `technical/ROCK_SOLID_NETWORKING.md` - Network synchronization details

### API and Schemas
- `api/session_metadata_schema.json` - Session data format
- `api/calibration_session_schema.json` - Calibration data format
- `api/session_log_schema.json` - Event logging format
- `api/processing_metadata_schema.json` - Processing results format

### Quick References
- `reference/FILE_NAMING_STANDARDS.md` - Naming conventions
- `reference/SHIMMER3_GSR_PLUS_QUICK_REFERENCE.md` - Shimmer quick start
- `reference/README_TESTING.md` - Testing procedures
- `reference/TEST_DOCUMENTATION.md` - Test documentation

---

**Note**: This reorganization consolidates 135+ documentation files from across the repository into a clear, navigable structure. Development-stage documents have been preserved in the `/deprecated/` folder for historical reference.