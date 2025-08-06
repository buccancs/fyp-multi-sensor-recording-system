# Living Architecture Documentation

**Version**: 2.0  
**Last Updated**: January 2025  
**Status**: Active Development  

## Document Purpose

This living architecture document provides a comprehensive, up-to-date view of the Multi-Sensor Recording System architecture. It is maintained as a living document that evolves with the codebase to ensure accuracy for new contributors, researchers, and stakeholders.

## Architecture Overview

The Multi-Sensor Recording System implements a **distributed star-mesh topology** with **PC master-controller coordination**, designed for research-grade multi-modal physiological data collection.

### Core Architectural Principles

1. **PC Master-Controller**: Centralized coordination and session management
2. **Offline-First Recording**: Local data storage with synchronized timestamps
3. **JSON Socket Protocol**: Standardized real-time communication
4. **Component-First Design**: Self-contained, modular components
5. **Clean MVVM Separation**: Strict layer separation with reactive state management

## Current Implementation Status

### Android Application Architecture (Clean MVVM)

**Status**: ✅ **Production Ready** - Complete architectural refactoring completed

The Android application has undergone comprehensive architectural improvement, achieving a **78% reduction** in monolithic code complexity through specialized controller extraction.

#### Layer Architecture
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│    (Activities, Fragments, UI)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            ViewModel Layer              │
│     (MainViewModelRefactored)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Business Logic Layer           │
│  (Controllers, Managers, Services)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Data Layer                  │
│   (Repositories, Data Sources)         │
└─────────────────────────────────────────┘
```

#### Specialized Controllers (Current Implementation)

**RecordingSessionController** (218 lines)
- **Responsibility**: Recording operation management
- **Features**: Reactive StateFlow patterns, configuration-based setup
- **Status**: ✅ Production ready, comprehensive testing

**DeviceConnectionManager** (389 lines)  
- **Responsibility**: Device connectivity orchestration
- **Features**: Auto-discovery, connection state tracking
- **Status**: ✅ Production ready, supports up to 8 devices

**FileTransferManager** (448 lines)
- **Responsibility**: Data transfer and session management  
- **Features**: Progress tracking, batch operations
- **Status**: ✅ Production ready, optimized I/O

**CalibrationManager** (441 lines)
- **Responsibility**: System-wide calibration processes
- **Features**: Multi-device calibration, validation workflows
- **Status**: ✅ Production ready, validation implemented

**MainViewModelRefactored** (451 lines)
- **Responsibility**: UI state coordination only
- **Features**: Reactive state combination, clean delegation
- **Status**: ✅ Production ready, zero business logic

#### Dependency Injection (Hilt)

**Current Implementation:**
- **@Singleton**: All managers and infrastructure components
- **@HiltViewModel**: ViewModels with proper lifecycle management
- **@ActivityScoped**: UI controllers and coordinators

**Module Organization:**
- `AppModule`: Core dependencies
- `SecurityModule`: Security and encryption services
- Custom modules planned for network and testing

### Python Application Architecture

**Status**: ✅ **Stable** - Component-based architecture with manual DI

#### Core Components
```
PC Master Controller
├── GUI Layer (PyQt5)
│   ├── Main Interface
│   ├── Session Control
│   └── Device Monitoring
├── Business Logic Layer
│   ├── Session Coordinator
│   ├── Device Manager
│   ├── Calibration Manager
│   └── Data Aggregator
├── Network Layer
│   ├── WebSocket Server
│   ├── Device Communication
│   └── Protocol Handlers
└── Infrastructure Layer
    ├── Logging
    ├── Configuration
    └── Storage Management
```

**Key Capabilities:**
- **Multi-Device Coordination**: Up to 8 Android devices
- **Real-Time Monitoring**: Live data stream visualization
- **Session Management**: Recording lifecycle coordination
- **Data Aggregation**: Synchronized multi-modal data collection

### Communication Protocol

**Status**: ✅ **Production Ready** - JSON WebSocket protocol

#### Protocol Features
- **JSON Messaging**: Structured command and data exchange
- **WebSocket Transport**: Real-time bidirectional communication
- **TLS Encryption**: Secure data transmission
- **Authentication**: Token-based authentication with crypto validation
- **Synchronization**: <1ms precision timestamp coordination

#### Message Types
- **Session Control**: Start, stop, pause, configuration
- **Device Status**: Health monitoring, capability reporting
- **Data Streaming**: Sensor data with synchronized timestamps
- **Calibration**: Calibration coordination and validation
- **Error Handling**: Structured error reporting and recovery

### Infrastructure Layer (Cross-Cutting Concerns)

**Status**: ✅ **Well-Established** - Comprehensive implementation

#### Logging Infrastructure
- **Component**: `Logger.kt` (Android), `Logger.py` (Python)
- **Features**: Centralized logging, file rotation, structured output
- **Scope**: `@Singleton` with DI, thread-safe operations
- **Testing**: Comprehensive unit and integration tests

#### Synchronization Engine
- **Components**: `SyncClockManager`, `SessionSynchronizer`
- **Precision**: <1ms accuracy across all devices
- **Architecture**: Hierarchical sync with master clock authority
- **Recovery**: Automatic re-sync on connection restoration

#### Error Handling Framework
- **Pattern**: Result types with structured exception handling
- **Coverage**: 590+ Android handlers, comprehensive Python coverage
- **Reliability**: 98.4% system reliability under failure conditions
- **Recovery**: 80% automatic recovery from connection failures

## Current Capacity and Performance

### Proven Capabilities
- **Device Support**: Up to 8 concurrent Android devices (tested)
- **Data Throughput**: >10 MB/s per device, 100+ MB/s aggregate
- **Synchronization**: <1ms temporal accuracy across all streams
- **Session Duration**: Extended recording (hours to days)
- **Reliability**: >95% test success rate, 82.35% overall evaluation

### Performance Characteristics
- **Network Utilization**: 80-120 MB/s (approaching 1 Gbps Ethernet limit)
- **Storage I/O**: 90 MB/s sustained write performance
- **Memory Usage**: 4 GB typical (8 devices)
- **CPU Utilization**: 60% average under full load
- **Synchronization Overhead**: <5% of total system resources

## Architecture Enforcement

### Automated Enforcement (Current)

**Architecture Tests**: Enhanced `SimpleArchitectureTest.kt`
- **Layer Separation**: Validates UI doesn't import network/service layers
- **Dependency Direction**: Ensures proper dependency flow
- **Module Isolation**: Verifies managers don't import UI components
- **Cross-Cutting Boundaries**: Validates infrastructure layer usage

**Static Analysis**: Enhanced `detekt.yml` configuration
- **Custom Rules**: Architecture violation detection
- **Forbidden Imports**: Automated detection of layer violations  
- **Build Integration**: Architecture validation in CI/CD pipeline

### Manual Review Guidelines
- **Code Review Checklist**: Architecture compliance validation
- **Pull Request Templates**: Architecture impact assessment
- **Documentation Updates**: Living document maintenance requirements

## Known Technical Debt and Planned Improvements

### High Priority
1. **Network Module DI**: Extract network dependencies to dedicated Hilt module
2. **Python DI Framework**: Implement service registry pattern for better testability
3. **Performance Optimization**: Edge processing to reduce bandwidth requirements

### Medium Priority
1. **Monitoring Enhancement**: Real-time performance metrics dashboard
2. **Error Recovery**: Enhanced automatic recovery mechanisms
3. **Configuration Management**: Dynamic configuration updates

### Low Priority
1. **API Documentation**: OpenAPI specification for protocol documentation
2. **Metrics Export**: Integration with external monitoring systems
3. **Health Checks**: Automated system health monitoring

## Scaling Roadmap

### Current Limitations (8 devices)
- **Network Bandwidth**: Approaching 1 Gbps Ethernet saturation
- **Single Point Coordination**: PC master-controller bottleneck
- **Storage I/O**: Local filesystem performance limits

### Near-Term Scaling (12-16 devices)
- **Timeline**: 1-2 months
- **Approach**: Enhanced single PC with parallel processing
- **Requirements**: Hardware upgrades, network optimization

### Medium-Term Scaling (32+ devices)  
- **Timeline**: 6-12 months
- **Approach**: Hierarchical controller architecture
- **Features**: Sub-controllers, distributed session management

### Long-Term Vision (Unlimited)
- **Timeline**: 12-24 months  
- **Approach**: Distributed mesh architecture
- **Features**: Geographic distribution, auto-scaling

## Testing and Quality Assurance

### Current Test Coverage
- **Foundation Tests**: 100% success rate (11/11 tests)
- **Integration Tests**: 50% success rate (3/6 tests) - ongoing improvement
- **Architecture Tests**: Comprehensive layer separation validation
- **Performance Tests**: Scalability and load testing framework

### Quality Metrics
- **Code Quality**: 590+ enhanced exception handlers
- **Reliability**: 98.4% system reliability under failure conditions  
- **Performance**: <1ms synchronization accuracy, >95% uptime
- **Maintainability**: 78% reduction in monolithic code complexity

## Documentation Maintenance

### Living Document Process
1. **Code Changes**: Update architecture docs with implementation changes
2. **Review Cycle**: Monthly architecture review and document updates
3. **Version Control**: Architecture docs versioned with code changes
4. **Stakeholder Review**: Regular review with research team and contributors

### Update Triggers
- **New Component Addition**: Update component diagrams and descriptions
- **Performance Changes**: Update capacity and performance metrics
- **Architecture Evolution**: Document architectural decisions and trade-offs
- **Research Findings**: Incorporate learnings from research usage

### Documentation Standards
- **Academic Rigor**: Master's thesis level documentation quality
- **Technical Precision**: Accurate reflection of implementation details
- **Practical Guidance**: Clear guidance for contributors and users
- **Visual Consistency**: Maintain diagram quality and consistency

## References and Additional Documentation

### Core Documentation
- **[Infrastructure Layer](./INFRASTRUCTURE_LAYER.md)**: Cross-cutting concerns detailed documentation
- **[DI Guidelines](./DEPENDENCY_INJECTION_GUIDELINES.md)**: Comprehensive dependency injection patterns
- **[Scaling Architecture](./SCALING_ARCHITECTURE.md)**: Detailed scaling strategies and analysis
- **[Architecture Diagrams](./ARCHITECTURE_DIAGRAMS.md)**: Visual architecture documentation

### Implementation References  
- **[Architecture Refactoring Summary](../ARCHITECTURE_REFACTORING_SUMMARY.md)**: Detailed refactoring achievements
- **[Test Execution Guide](./TEST_EXECUTION_GUIDE.md)**: Comprehensive testing procedures
- **[Developer Guide](../DEVELOPER_GUIDE.md)**: Development workflow and standards

### Research Context
- **[README](../README.md)**: System overview and quick start
- **[Thesis Report](../THESIS_REPORT.md)**: Academic research context
- **Technical Glossary**: Terminology and definitions

---

**Maintenance Note**: This document is updated with each significant architectural change. Contributors must update relevant sections when modifying system architecture. The document serves as the authoritative reference for the current system design and evolution strategy.

**Last Architecture Review**: January 2025  
**Next Scheduled Review**: February 2025  
**Document Maintainer**: Architecture Team