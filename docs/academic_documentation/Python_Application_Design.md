# Python Desktop Application Design and Implementation

## 1. Introduction to Python Desktop Application Design

The Python desktop application functions as the sophisticated central command and control center for the entire contactless GSR prediction system, serving as the primary orchestration platform responsible for coordinating all distributed system components while simultaneously providing comprehensive real-time monitoring capabilities, advanced data analysis functionality, and robust research management tools specifically designed for physiological monitoring research applications. The application design philosophy emphasizes unwavering scientific rigor, exceptional real-time performance characteristics, and extensive extensibility capabilities to support the diverse range of research protocols, experimental configurations, and analytical requirements commonly encountered in physiological research environments.

The complexity and scope of the desktop application stems from its role as the central nervous system of the distributed measurement infrastructure, where it must seamlessly integrate and coordinate multiple heterogeneous hardware platforms, diverse sensor modalities, real-time signal processing algorithms, machine learning inference systems, and comprehensive data management capabilities. This central coordination role requires the application to maintain precise temporal awareness across all system components while providing researchers with intuitive interfaces for experimental control, real-time monitoring, and post-hoc analysis.

This comprehensive document presents an exhaustive technical analysis of the desktop application architecture, examining in detail the sophisticated design patterns employed, the complex implementation strategies developed specifically for multi-device coordination requirements, the advanced real-time data processing capabilities, the comprehensive visualization systems designed for physiological research applications, and the robust data management frameworks that ensure research data integrity and scientific reproducibility throughout the entire research workflow.

The architectural analysis encompasses both the theoretical foundations underlying the design decisions and the practical implementation considerations that drive the selection of specific technologies, frameworks, algorithms, and design patterns. The discussion reveals how the application successfully balances the competing requirements of real-time performance versus computational accuracy, distributed system coordination versus local processing optimization, research flexibility versus operational reliability, and advanced functionality versus user interface simplicity.

### 1.1 Design Philosophy and Fundamental Approach

The foundational design philosophy governing the Python desktop application development reflects a deep understanding of the unique challenges and specialized requirements inherent in physiological research applications, where traditional desktop application design approaches often prove inadequate for meeting the specialized needs of scientific data collection, analysis, and management systems.

**Research-Centric Design Methodology:**
The application design fundamentally prioritizes research workflow optimization and scientific validity over conventional desktop application design patterns and user experience conventions, recognizing that research applications have fundamentally different success criteria than commercial software products. This research-centric approach emphasizes experimental control capabilities, comprehensive data integrity mechanisms, and scientific reproducibility features as the primary success metrics, with traditional usability considerations being carefully balanced against the fundamental requirement of providing researchers with the precise control and monitoring capabilities necessary for conducting valid scientific studies.

This design philosophy manifests throughout the application architecture in numerous specific ways. User interface design prioritizes information density and functional completeness over visual simplicity, providing researchers with comprehensive access to all system parameters and status information necessary for experimental control and monitoring. Data processing pipelines are optimized for accuracy and validation rather than processing speed, implementing extensive quality checks and validation mechanisms that ensure scientific validity even when such mechanisms impose computational overhead.

The research-centric approach also drives the selection of technologies and implementation strategies that may differ significantly from typical desktop application development practices. Real-time processing requirements take precedence over standard GUI framework limitations, requiring custom threading architectures and asynchronous processing patterns that can maintain consistent operation despite the event-driven nature of GUI frameworks.

**Distributed System Orchestration and Coordination:**
The application design approaches the desktop system as the central conductor of a complex distributed orchestra, where it must coordinate multiple mobile devices, diverse sensor systems, distributed processing components, and network communication channels while maintaining the precise temporal synchronization essential for physiological monitoring applications.

This orchestration responsibility requires sophisticated distributed system design patterns that can manage the complex interactions between autonomous system components while providing centralized coordination and control capabilities. The application implements comprehensive device discovery and management systems that can automatically detect and configure new system components, maintain real-time awareness of system status and performance, and provide automatic recovery mechanisms when distributed components experience failures or temporary disruptions.

The coordination architecture extends beyond simple command and control to encompass sophisticated workflow management capabilities that can adapt to varying experimental requirements and research protocols. The system can dynamically reconfigure its processing pipelines, modify data collection parameters, and adjust coordination strategies based on real-time assessment of system performance and experimental requirements.

**Real-Time Performance and Temporal Precision:**
All architectural decisions throughout the application are systematically evaluated for their impact on real-time processing capabilities, with particular emphasis on ensuring sub-second response times for critical research operations, providing immediate feedback for experimental monitoring activities, and maintaining precise temporal relationships between distributed system components.

The real-time performance requirements imposed by physiological monitoring applications are significantly more demanding than typical desktop application requirements. Physiological signals often contain critical information at frequencies approaching the Nyquist limit of the measurement system, requiring consistent, low-latency processing that cannot tolerate the variable timing characteristics typical of many desktop application architectures.

Performance optimization extends throughout the application stack, from low-level device communication protocols to high-level user interface responsiveness. Communication systems are optimized for predictable latency rather than maximum throughput, ensuring that coordination commands reach distributed components within specified timing windows. Processing pipelines are designed for consistent timing rather than peak performance, ensuring that temporal artifacts do not compromise physiological signal extraction and analysis.

**Extensible Research Platform Architecture:**
The application architecture is designed to function as a comprehensive research platform that can accommodate the addition of new experimental protocols, analysis methodologies, sensor types, and device configurations without requiring fundamental system redesign or extensive modification of existing functionality.

The extensibility architecture employs plugin-based design patterns that enable researchers to add custom analysis algorithms, visualization components, and data export capabilities through well-defined extension interfaces. This extensibility approach enables the system to evolve with advancing research methodologies while maintaining backward compatibility with existing datasets and analysis workflows.

The platform architecture also supports configurable experimental protocols that can be adapted to different research requirements and methodological approaches. Researchers can define custom measurement procedures, specify data collection parameters, and implement specialized analysis workflows through configuration interfaces rather than requiring software development expertise.

**Data Integrity and Scientific Validation Framework:**
Every aspect of the application architecture incorporates comprehensive data validation mechanisms, integrity checking systems, and quality assurance frameworks specifically designed to ensure the reliability and validity of research results throughout the entire research workflow, from initial data collection through final analysis and publication.

The validation framework operates at multiple levels throughout the system, providing real-time quality assessment during data collection, comprehensive validation during data processing, and ongoing integrity monitoring during data storage and analysis. These validation mechanisms enable researchers to identify and address potential data quality issues before they compromise research validity.

The scientific validation architecture also includes extensive logging and audit capabilities that provide comprehensive documentation of all system activities, configuration changes, and data processing operations. This audit trail supports research reproducibility requirements while enabling post-hoc analysis of system behavior during specific experimental sessions.

### 1.2 Technical Foundation and Technology Selection Rationale

The selection of specific technologies and frameworks for the Python desktop application reflects careful analysis of the unique requirements imposed by real-time physiological monitoring applications, including the need for sophisticated scientific computing capabilities, robust multi-threaded processing support, comprehensive visualization tools, and seamless integration with the broader Python scientific computing ecosystem.

**PyQt5 Framework Selection and Justification:**
The selection of PyQt5 as the primary application framework represents the optimal balance of performance characteristics, feature completeness, cross-platform compatibility, and scientific computing integration capabilities required for sophisticated research applications that must operate reliably across diverse research environments and hardware configurations.

PyQt5 provides exceptional performance characteristics that are essential for real-time applications, including efficient event handling systems that can manage multiple concurrent data streams without introducing significant latency, sophisticated threading support that enables complex asynchronous operations while maintaining user interface responsiveness, and high-performance graphics capabilities that support real-time visualization of multiple physiological signals simultaneously.

The framework's mature ecosystem provides access to comprehensive UI components specifically designed for data-intensive applications, including advanced plotting widgets, scientific data display components, and specialized input controls that facilitate the complex parameter configuration requirements typical of research applications. This component ecosystem significantly reduces development complexity while ensuring consistent, professional user interface design that meets the expectations of research users.

Cross-platform compatibility ensures that the application can operate effectively across different operating systems commonly encountered in research environments, including Windows, macOS, and Linux systems. This compatibility reduces deployment complexity and enables collaborative research across institutions with different computing infrastructure standards.

The tight integration between PyQt5 and the Python scientific computing ecosystem enables seamless data exchange between the user interface components and the underlying analysis systems, eliminating the performance penalties and complexity associated with cross-language data marshaling that would be required with other framework choices.

**Scientific Computing Integration and Ecosystem Utilization:**
The application architecture leverages deep integration with the comprehensive Python scientific computing ecosystem, including NumPy for efficient numerical array processing, SciPy for advanced signal processing algorithms, matplotlib for sophisticated data visualization, scikit-learn for machine learning capabilities, and pandas for complex data manipulation and analysis operations.

NumPy integration provides the foundation for all numerical processing within the application, enabling efficient manipulation of large multi-dimensional arrays representing time-series physiological data. The NumPy array interface ensures optimal memory utilization and computational efficiency for the intensive numerical operations required by real-time signal processing algorithms.

SciPy integration provides access to sophisticated signal processing algorithms specifically designed for scientific applications, including advanced filtering techniques, spectral analysis methods, statistical analysis tools, and optimization algorithms. These capabilities enable the implementation of research-grade signal processing pipelines without requiring custom algorithm development or external library dependencies.

Matplotlib integration enables the creation of publication-quality visualizations that can display complex multi-modal data streams in real-time while supporting the detailed annotation and customization requirements necessary for research applications. The matplotlib integration supports both real-time data streaming and comprehensive post-hoc analysis visualization capabilities.

Scikit-learn integration provides access to state-of-the-art machine learning algorithms and evaluation frameworks that enable the implementation of sophisticated GSR prediction models while supporting the validation and performance assessment requirements necessary for scientific applications.

**Asynchronous Architecture and Concurrency Management:**
The application employs sophisticated asynchronous programming patterns and advanced concurrency management techniques to handle the complex requirements of concurrent device communication, real-time signal processing, comprehensive data logging, and responsive user interface management without introducing blocking operations that could compromise system performance or user experience.

The asynchronous architecture enables the application to maintain simultaneous connections with multiple mobile devices while processing their data streams in real-time, coordinating timing synchronization across all system components, and providing immediate user interface feedback about system status and data quality. This concurrent operation is essential for the multi-device coordination requirements of the contactless GSR prediction system.

Advanced threading strategies ensure that computationally intensive operations such as signal processing and machine learning inference do not interfere with time-critical operations such as device communication and user interface responsiveness. The threading architecture implements sophisticated load balancing and priority management mechanisms that can adapt to varying computational demands while maintaining consistent system performance.

The concurrency management system also implements comprehensive error isolation mechanisms that prevent failures in individual processing threads from affecting other system components. This isolation ensures that temporary problems with individual devices or processing components do not compromise the overall system functionality or data collection continuity.

**Modular Component Design and Software Engineering Principles:**
The application architecture adheres rigorously to modular design principles that create clear, well-defined boundaries between distinct functional domains, enabling independent development, comprehensive testing, collaborative maintenance, and systematic evolution of different system aspects while facilitating future enhancements and modifications without requiring extensive system redesign.

The modular architecture extends beyond simple code organization to encompass data models, communication protocols, configuration management, and deployment strategies. Each module encapsulates specific domain knowledge and functionality while exposing minimal, carefully designed interfaces to other system components. This approach enables specialized development teams to focus on their areas of expertise while ensuring consistent integration patterns.

The separation of concerns principle is implemented throughout the application, with distinct modules handling device communication, signal processing, machine learning inference, data storage, user interface management, and configuration management. This separation enables comprehensive testing strategies where each module can be thoroughly validated in isolation before integration testing validates inter-module interactions and system-level behavior.

The modular design also facilitates technology evolution and future enhancement, where individual modules can be updated, replaced, or extended without requiring changes to other system components. This modularity proves particularly valuable in research environments where different aspects of the system may evolve at different rates based on research priorities, technological advances, and changing experimental requirements.

## 2. Application Architecture Overview

### 2.1 High-Level Architecture Pattern

The Python desktop application implements a sophisticated layered architecture enhanced with reactive programming patterns and distributed system coordination capabilities.

**Architecture Layers:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Main Window   │  │  Visualization  │  │   Configuration │ │
│  │   & Controls    │  │    Modules      │  │    Dialogs      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Application   │  │   Experiment    │  │     Device      │ │
│  │   Controller    │  │   Controller    │  │   Controller    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Data Proc.    │  │   Communication │  │    Analysis     │ │
│  │    Service      │  │     Service     │  │    Service      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Data Access   │  │   File System   │  │    Network      │ │
│  │     Objects     │  │    Manager      │  │   Interface     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Application Framework

**2.2.1 Main Application Class**

```python
class GSRPredictionApplication(QApplication):
    """
    Main application class coordinating all system components and managing
    application lifecycle for physiological research workflows.
    """
    
    def __init__(self, argv: List[str]):
        super().__init__(argv)
        
        # Application metadata
        self.setApplicationName("GSR Prediction Research System")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("Physiological Computing Research Lab")
        
        # Initialize core application services
        self.dependency_container = DependencyContainer()
        self.configuration_manager = ConfigurationManager()
        self.logging_system = LoggingSystem()
        self.error_handler = GlobalErrorHandler()
        
        # Initialize subsystem managers
        self.device_manager = DeviceManager(self.dependency_container)
        self.experiment_manager = ExperimentManager(self.dependency_container)
        self.data_manager = DataManager(self.dependency_container)
        self.analysis_engine = AnalysisEngine(self.dependency_container)
        
        # Initialize user interface
        self.main_window = None
        self.splash_screen = None
        
        # Setup application-level signal handling
        self.setup_signal_connections()
        self.setup_exception_handling()
        
    def initialize_application(self) -> bool:
        """
        Initialize application components with comprehensive error handling
        and validation of system requirements.
        """
        try:
            # Display splash screen during initialization
            self.splash_screen = SplashScreen()
            self.splash_screen.show()
            
            # Initialize configuration
            self.splash_screen.update_status("Loading configuration...")
            if not self.configuration_manager.initialize():
                raise ApplicationInitializationError("Configuration initialization failed")
                
            # Initialize logging system
            self.splash_screen.update_status("Initializing logging system...")
            self.logging_system.configure(self.configuration_manager.get_logging_config())
            
            # Validate system requirements
            self.splash_screen.update_status("Validating system requirements...")
            if not self.validate_system_requirements():
                raise SystemRequirementsError("System requirements not met")
            
            # Initialize core services
            self.splash_screen.update_status("Initializing core services...")
            self.initialize_core_services()
            
            # Initialize device discovery and communication
            self.splash_screen.update_status("Starting device discovery...")
            self.device_manager.start_discovery()
            
            # Create and show main window
            self.splash_screen.update_status("Loading user interface...")
            self.main_window = MainWindow(
                device_manager=self.device_manager,
                experiment_manager=self.experiment_manager,
                data_manager=self.data_manager,
                analysis_engine=self.analysis_engine
            )
            
            self.splash_screen.finish(self.main_window)
            self.main_window.show()
            
            logging.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Application initialization failed: {e}")
            QMessageBox.critical(
                None, 
                "Initialization Error", 
                f"Failed to initialize application: {str(e)}"
            )
            return False
    
    def validate_system_requirements(self) -> bool:
        """Validate that system meets minimum requirements for operation."""
        requirements = SystemRequirements()
        
        # Check Python version
        if not requirements.check_python_version():
            return False
            
        # Check required libraries
        if not requirements.check_required_libraries():
            return False
            
        # Check hardware capabilities
        if not requirements.check_hardware_capabilities():
            return False
            
        # Check network connectivity
        if not requirements.check_network_connectivity():
            return False
            
        return True
    
    def run(self) -> int:
        """Main application execution entry point."""
        if self.initialize_application():
            return self.exec_()
        else:
            return 1
```

**2.2.2 Dependency Injection Container**

```python
class DependencyContainer:
    """
    Dependency injection container managing application-wide services
    and component lifecycles with proper cleanup and resource management.
    """
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
        self._factories = {}
        
        self.register_core_services()
        
    def register_core_services(self):
        """Register core application services with appropriate lifecycle management."""
        
        # Configuration services
        self.register_singleton(
            ConfigurationManager,
            lambda: ConfigurationManager()
        )
        
        # Communication services
        self.register_singleton(
            NetworkCommunicationService,
            lambda: NetworkCommunicationService(
                config=self.get(ConfigurationManager).get_network_config()
            )
        )
        
        # Data processing services
        self.register_singleton(
            RealTimeDataProcessor,
            lambda: RealTimeDataProcessor(
                config=self.get(ConfigurationManager).get_processing_config()
            )
        )
        
        # Analysis services
        self.register_singleton(
            StatisticalAnalysisEngine,
            lambda: StatisticalAnalysisEngine()
        )
        
        # Visualization services
        self.register_singleton(
            VisualizationManager,
            lambda: VisualizationManager()
        )
        
        # Data persistence services
        self.register_singleton(
            DataPersistenceManager,
            lambda: DataPersistenceManager(
                config=self.get(ConfigurationManager).get_storage_config()
            )
        )
    
    def register_singleton(self, service_type: Type, factory: Callable):
        """Register singleton service with lazy initialization."""
        self._factories[service_type] = factory
        
    def register_transient(self, service_type: Type, factory: Callable):
        """Register transient service created for each request."""
        self._services[service_type] = factory
        
    def get(self, service_type: Type) -> Any:
        """Retrieve service instance with proper lifecycle management."""
        if service_type in self._singletons:
            return self._singletons[service_type]
            
        if service_type in self._factories:
            instance = self._factories[service_type]()
            self._singletons[service_type] = instance
            return instance
            
        if service_type in self._services:
            return self._services[service_type]()
            
        raise ServiceNotRegisteredException(f"Service {service_type} not registered")
    
    def cleanup(self):
        """Cleanup all registered services and release resources."""
        for service in self._singletons.values():
            if hasattr(service, 'cleanup'):
                try:
                    service.cleanup()
                except Exception as e:
                    logging.error(f"Error cleaning up service {type(service)}: {e}")
        
        self._singletons.clear()
```

## 3. Device Management and Communication

### 3.1 Device Discovery and Management System

The device management system handles the complex task of discovering, connecting to, and coordinating multiple Android devices and sensors in the distributed research environment.

**3.1.1 Device Manager Architecture**

```python
class DeviceManager(QObject):
    """
    Central coordinator for all connected devices, managing discovery,
    connection lifecycle, and communication coordination.
    """
    
    # Qt signals for UI updates
    device_discovered = pyqtSignal(dict)
    device_connected = pyqtSignal(str, dict)
    device_disconnected = pyqtSignal(str)
    device_status_changed = pyqtSignal(str, str)
    data_received = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str, str)
    
    def __init__(self, dependency_container: DependencyContainer):
        super().__init__()
        
        self.dependency_container = dependency_container
        self.communication_service = dependency_container.get(NetworkCommunicationService)
        self.config_manager = dependency_container.get(ConfigurationManager)
        
        # Device registry and state management
        self.connected_devices = {}
        self.device_capabilities = {}
        self.device_status = {}
        
        # Discovery and communication components
        self.discovery_server = None
        self.websocket_manager = None
        self.udp_broadcaster = None
        
        # Background processing
        self.discovery_thread = None
        self.communication_thread_pool = QThreadPool()
        
        self.setup_discovery_system()
        
    def setup_discovery_system(self):
        """Initialize device discovery and communication infrastructure."""
        
        # UDP discovery server for device announcement
        self.discovery_server = UDPDiscoveryServer(
            port=self.config_manager.get('network.discovery_port', 8888),
            callback=self.handle_device_discovery
        )
        
        # WebSocket manager for real-time communication
        self.websocket_manager = WebSocketManager(
            port_range=(9000, 9100),
            message_handler=self.handle_device_message,
            connection_handler=self.handle_connection_events
        )
        
        # UDP broadcaster for coordinated commands
        self.udp_broadcaster = UDPBroadcaster(
            broadcast_port=self.config_manager.get('network.broadcast_port', 8889)
        )
    
    def start_discovery(self):
        """Start device discovery process."""
        try:
            # Start discovery server
            self.discovery_server.start()
            
            # Start WebSocket manager
            self.websocket_manager.start()
            
            # Begin periodic device discovery broadcasts
            self.start_discovery_broadcasts()
            
            logging.info("Device discovery started successfully")
            
        except Exception as e:
            logging.error(f"Failed to start device discovery: {e}")
            self.error_occurred.emit("Discovery", str(e))
    
    def handle_device_discovery(self, device_info: dict, source_address: tuple):
        """Process discovered device and initiate connection."""
        
        device_id = device_info.get('device_id')
        device_type = device_info.get('device_type')
        
        if not device_id or not device_type:
            logging.warning(f"Invalid device discovery from {source_address}")
            return
        
        # Validate device capabilities
        if not self.validate_device_capabilities(device_info):
            logging.warning(f"Device {device_id} does not meet capability requirements")
            return
        
        # Check if device is already connected
        if device_id in self.connected_devices:
            logging.debug(f"Device {device_id} already connected, updating status")
            self.update_device_status(device_id, "active")
            return
        
        # Emit discovery signal for UI updates
        self.device_discovered.emit(device_info)
        
        # Initiate connection process
        self.initiate_device_connection(device_id, device_info, source_address)
    
    def initiate_device_connection(self, device_id: str, device_info: dict, address: tuple):
        """Establish connection with discovered device."""
        
        connection_task = DeviceConnectionTask(
            device_id=device_id,
            device_info=device_info,
            address=address,
            websocket_manager=self.websocket_manager,
            success_callback=self.on_device_connected,
            error_callback=self.on_connection_error
        )
        
        self.communication_thread_pool.start(connection_task)
    
    def on_device_connected(self, device_id: str, connection_info: dict):
        """Handle successful device connection."""
        
        self.connected_devices[device_id] = connection_info
        self.device_status[device_id] = "connected"
        
        # Perform device handshake and configuration
        self.perform_device_handshake(device_id)
        
        # Emit connection signal
        self.device_connected.emit(device_id, connection_info)
        
        logging.info(f"Device {device_id} connected successfully")
    
    def perform_device_handshake(self, device_id: str):
        """Perform initial handshake and configuration with connected device."""
        
        # Send handshake message
        handshake_message = {
            "type": "handshake",
            "timestamp": time.time(),
            "server_id": self.get_server_id(),
            "protocol_version": "2.0",
            "configuration": self.get_device_configuration()
        }
        
        self.send_message_to_device(device_id, handshake_message)
        
        # Request device capabilities and status
        self.request_device_capabilities(device_id)
        self.request_device_status(device_id)
    
    def send_message_to_device(self, device_id: str, message: dict) -> bool:
        """Send message to specific device."""
        
        if device_id not in self.connected_devices:
            logging.warning(f"Attempted to send message to disconnected device: {device_id}")
            return False
        
        try:
            connection = self.connected_devices[device_id]
            websocket = connection.get('websocket')
            
            if websocket and not websocket.closed:
                asyncio.create_task(websocket.send(json.dumps(message)))
                return True
            else:
                logging.warning(f"WebSocket connection to {device_id} is closed")
                return False
                
        except Exception as e:
            logging.error(f"Failed to send message to device {device_id}: {e}")
            return False
    
    def broadcast_message(self, message: dict, exclude_devices: List[str] = None):
        """Broadcast message to all connected devices."""
        
        exclude_devices = exclude_devices or []
        
        for device_id in self.connected_devices:
            if device_id not in exclude_devices:
                self.send_message_to_device(device_id, message)
```

**3.1.2 WebSocket Communication Manager**

```python
class WebSocketManager:
    """
    Manages WebSocket connections for real-time communication with mobile devices.
    Handles connection lifecycle, message routing, and error recovery.
    """
    
    def __init__(self, port_range: tuple, message_handler: Callable, connection_handler: Callable):
        self.port_range = port_range
        self.message_handler = message_handler
        self.connection_handler = connection_handler
        
        self.server = None
        self.active_connections = {}
        self.connection_lock = asyncio.Lock()
        
        # Event loops for async operation
        self.loop = None
        self.server_task = None
        
    async def start_server(self):
        """Start WebSocket server on available port."""
        
        for port in range(self.port_range[0], self.port_range[1] + 1):
            try:
                self.server = await websockets.serve(
                    self.handle_websocket_connection,
                    "0.0.0.0",
                    port,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=10
                )
                
                logging.info(f"WebSocket server started on port {port}")
                return port
                
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    continue
                else:
                    raise
        
        raise RuntimeError("No available ports in specified range")
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle incoming WebSocket connection from mobile device."""
        
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        device_id = None
        
        try:
            logging.info(f"New WebSocket connection from {client_address}")
            
            # Wait for device identification
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get('type') == 'device_identification':
                        device_id = data.get('device_id')
                        
                        if device_id:
                            # Register connection
                            async with self.connection_lock:
                                self.active_connections[device_id] = {
                                    'websocket': websocket,
                                    'address': client_address,
                                    'connected_at': time.time(),
                                    'last_activity': time.time()
                                }
                            
                            # Notify connection handler
                            self.connection_handler(device_id, 'connected', client_address)
                            
                            # Send acknowledgment
                            await websocket.send(json.dumps({
                                'type': 'connection_acknowledged',
                                'server_time': time.time()
                            }))
                            
                            break
                    
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON from {client_address}")
                    continue
            
            # Handle ongoing communication
            if device_id:
                await self.handle_device_communication(device_id, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"WebSocket connection closed: {client_address}")
            
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            
        finally:
            # Cleanup connection
            if device_id and device_id in self.active_connections:
                async with self.connection_lock:
                    del self.active_connections[device_id]
                
                self.connection_handler(device_id, 'disconnected', client_address)
    
    async def handle_device_communication(self, device_id: str, websocket):
        """Handle ongoing communication with connected device."""
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # Update last activity timestamp
                    if device_id in self.active_connections:
                        self.active_connections[device_id]['last_activity'] = time.time()
                    
                    # Route message to handler
                    self.message_handler(device_id, data)
                    
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON from device {device_id}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"Device {device_id} disconnected")
            
        except Exception as e:
            logging.error(f"Communication error with device {device_id}: {e}")
    
    async def send_message(self, device_id: str, message: dict):
        """Send message to specific device."""
        
        async with self.connection_lock:
            if device_id in self.active_connections:
                websocket = self.active_connections[device_id]['websocket']
                
                try:
                    await websocket.send(json.dumps(message))
                    return True
                    
                except websockets.exceptions.ConnectionClosed:
                    logging.warning(f"Connection to device {device_id} is closed")
                    del self.active_connections[device_id]
                    return False
                    
                except Exception as e:
                    logging.error(f"Failed to send message to device {device_id}: {e}")
                    return False
            else:
                logging.warning(f"Device {device_id} is not connected")
                return False
```

## 4. Real-Time Data Processing and Analysis

### 4.1 Real-Time Data Processing Architecture

The real-time processing system handles high-frequency data streams from multiple devices while maintaining low latency and high throughput for immediate feedback and monitoring.

**4.1.1 Data Processing Pipeline**

```python
class RealTimeDataProcessor(QObject):
    """
    High-performance real-time data processing system handling multi-modal
    sensor streams with temporal synchronization and quality assessment.
    """
    
    # Qt signals for UI updates
    data_processed = pyqtSignal(str, dict)
    quality_alert = pyqtSignal(str, float, str)
    processing_statistics = pyqtSignal(dict)
    
    def __init__(self, dependency_container: DependencyContainer):
        super().__init__()
        
        self.dependency_container = dependency_container
        self.config = dependency_container.get(ConfigurationManager).get_processing_config()
        
        # Processing components
        self.signal_processor = MultiModalSignalProcessor()
        self.quality_assessor = SignalQualityAssessor()
        self.ml_inference_engine = MLInferenceEngine()
        self.temporal_synchronizer = TemporalSynchronizer()
        
        # Data buffers for multi-device processing
        self.device_buffers = {}
        self.processing_queues = {}
        
        # Processing thread pool
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(8)  # Adjust based on system capabilities
        
        # Performance monitoring
        self.processing_statistics = ProcessingStatistics()
        
        # Initialize processing pipeline
        self.setup_processing_pipeline()
    
    def setup_processing_pipeline(self):
        """Initialize processing pipeline components."""
        
        # Configure signal processor
        self.signal_processor.configure(
            roi_count=3,
            signal_types=['rgb', 'thermal'],
            temporal_window=5.0  # 5 second processing window
        )
        
        # Initialize quality assessor
        self.quality_assessor.set_thresholds(
            minimum_snr=10.0,
            maximum_noise_level=0.3,
            minimum_stability=0.7
        )
        
        # Load ML inference models
        self.ml_inference_engine.load_models(
            gsr_model_path=self.config.get('models.gsr_prediction_path'),
            quality_model_path=self.config.get('models.quality_assessment_path')
        )
    
    def process_device_data(self, device_id: str, data: dict):
        """Process incoming data from specific device."""
        
        data_type = data.get('type')
        timestamp = data.get('timestamp', time.time())
        
        # Ensure device buffer exists
        if device_id not in self.device_buffers:
            self.device_buffers[device_id] = DeviceDataBuffer(
                buffer_size=1000,  # Buffer 33 seconds at 30 FPS
                temporal_window=5.0
            )
        
        # Add data to device buffer
        self.device_buffers[device_id].add_data(data_type, timestamp, data)
        
        # Check if sufficient data available for processing
        if self.device_buffers[device_id].has_sufficient_data():
            # Create processing task
            processing_task = DataProcessingTask(
                device_id=device_id,
                data_buffer=self.device_buffers[device_id].get_processing_window(),
                signal_processor=self.signal_processor,
                quality_assessor=self.quality_assessor,
                ml_engine=self.ml_inference_engine,
                callback=self.on_processing_complete
            )
            
            # Submit to thread pool
            self.thread_pool.start(processing_task)
    
    def on_processing_complete(self, device_id: str, results: dict):
        """Handle completed processing results."""
        
        # Update processing statistics
        self.processing_statistics.update(
            device_id=device_id,
            processing_time=results.get('processing_time'),
            data_quality=results.get('signal_quality')
        )
        
        # Check for quality alerts
        signal_quality = results.get('signal_quality', 0.0)
        if signal_quality < self.config.get('quality_thresholds.warning', 0.5):
            self.quality_alert.emit(
                device_id,
                signal_quality,
                results.get('quality_issues', '')
            )
        
        # Emit processed data
        self.data_processed.emit(device_id, results)
        
        # Emit processing statistics
        self.processing_statistics.emit(
            self.processing_statistics.get_current_statistics()
        )
```

**4.1.2 Multi-Modal Signal Processing**

```python
class MultiModalSignalProcessor:
    """
    Advanced signal processing for multi-modal physiological data with
    sophisticated filtering, feature extraction, and fusion capabilities.
    """
    
    def __init__(self):
        self.rgb_processor = RGBSignalProcessor()
        self.thermal_processor = ThermalSignalProcessor()
        self.fusion_processor = ModalityFusionProcessor()
        
        # Signal processing parameters
        self.sampling_rate = 30.0  # Hz
        self.filter_params = {
            'low_cut': 0.1,
            'high_cut': 5.0,
            'order': 4
        }
        
        # ROI processing configuration
        self.roi_config = {
            'index_finger': {'size': 20, 'weight': 1.0},
            'ring_finger': {'size': 20, 'weight': 1.0},
            'palm_center': {'size': 30, 'weight': 0.8}
        }
    
    def process_frame_sequence(self, frame_sequence: List[dict]) -> dict:
        """Process sequence of synchronized frames from multiple modalities."""
        
        processing_results = {
            'rgb_signals': [],
            'thermal_signals': [],
            'fused_signals': [],
            'feature_vectors': [],
            'temporal_features': {},
            'processing_metadata': {}
        }
        
        # Separate RGB and thermal frames
        rgb_frames = [f for f in frame_sequence if f.get('type') == 'rgb_frame']
        thermal_frames = [f for f in frame_sequence if f.get('type') == 'thermal_frame']
        
        # Process RGB signals
        if rgb_frames:
            rgb_results = self.rgb_processor.process_sequence(rgb_frames)
            processing_results['rgb_signals'] = rgb_results['roi_signals']
            processing_results['feature_vectors'].extend(rgb_results['features'])
        
        # Process thermal signals
        if thermal_frames:
            thermal_results = self.thermal_processor.process_sequence(thermal_frames)
            processing_results['thermal_signals'] = thermal_results['roi_signals']
            processing_results['feature_vectors'].extend(thermal_results['features'])
        
        # Perform modal fusion if both modalities available
        if rgb_frames and thermal_frames:
            fusion_results = self.fusion_processor.fuse_modalities(
                rgb_signals=processing_results['rgb_signals'],
                thermal_signals=processing_results['thermal_signals']
            )
            processing_results['fused_signals'] = fusion_results['fused_signals']
            processing_results['feature_vectors'].extend(fusion_results['features'])
        
        # Extract temporal features
        processing_results['temporal_features'] = self.extract_temporal_features(
            processing_results
        )
        
        return processing_results
    
    def extract_temporal_features(self, signal_data: dict) -> dict:
        """Extract temporal features from processed signals."""
        
        temporal_features = {}
        
        # Extract features from RGB signals
        if signal_data['rgb_signals']:
            rgb_temporal = self.compute_temporal_statistics(
                signal_data['rgb_signals']
            )
            temporal_features['rgb'] = rgb_temporal
        
        # Extract features from thermal signals
        if signal_data['thermal_signals']:
            thermal_temporal = self.compute_temporal_statistics(
                signal_data['thermal_signals']
            )
            temporal_features['thermal'] = thermal_temporal
        
        # Extract features from fused signals
        if signal_data['fused_signals']:
            fused_temporal = self.compute_temporal_statistics(
                signal_data['fused_signals']
            )
            temporal_features['fused'] = fused_temporal
        
        return temporal_features
    
    def compute_temporal_statistics(self, signal_sequence: List) -> dict:
        """Compute temporal statistical features from signal sequence."""
        
        if not signal_sequence:
            return {}
        
        # Convert to numpy array for efficient computation
        signal_array = np.array(signal_sequence)
        
        return {
            'mean': np.mean(signal_array, axis=0).tolist(),
            'std': np.std(signal_array, axis=0).tolist(),
            'min': np.min(signal_array, axis=0).tolist(),
            'max': np.max(signal_array, axis=0).tolist(),
            'range': (np.max(signal_array, axis=0) - np.min(signal_array, axis=0)).tolist(),
            'variance': np.var(signal_array, axis=0).tolist(),
            'skewness': scipy.stats.skew(signal_array, axis=0).tolist(),
            'kurtosis': scipy.stats.kurtosis(signal_array, axis=0).tolist(),
            'energy': np.sum(signal_array**2, axis=0).tolist(),
            'zero_crossings': self.count_zero_crossings(signal_array),
            'spectral_features': self.compute_spectral_features(signal_array)
        }
    
    def compute_spectral_features(self, signal_array: np.ndarray) -> dict:
        """Compute frequency domain features from signal."""
        
        spectral_features = {}
        
        for roi_idx in range(signal_array.shape[1]):
            roi_signal = signal_array[:, roi_idx]
            
            # Compute power spectral density
            frequencies, psd = scipy.signal.welch(
                roi_signal,
                fs=self.sampling_rate,
                nperseg=min(len(roi_signal), 256)
            )
            
            # Extract spectral statistics
            spectral_features[f'roi_{roi_idx}'] = {
                'dominant_frequency': frequencies[np.argmax(psd)],
                'spectral_centroid': np.sum(frequencies * psd) / np.sum(psd),
                'spectral_rolloff': self.compute_spectral_rolloff(frequencies, psd),
                'spectral_flux': self.compute_spectral_flux(psd),
                'total_power': np.sum(psd),
                'frequency_bands': self.compute_frequency_band_power(frequencies, psd)
            }
        
        return spectral_features
```

### 4.2 Machine Learning Integration

**4.2.1 ML Inference Engine**

```python
class MLInferenceEngine:
    """
    Machine learning inference engine supporting multiple model types
    and real-time prediction with uncertainty quantification.
    """
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
        self.prediction_history = {}
        
        # Model configuration
        self.default_model_config = {
            'batch_size': 1,
            'max_sequence_length': 150,  # 5 seconds at 30 FPS
            'feature_normalization': True,
            'uncertainty_estimation': True
        }
    
    def load_models(self, **model_paths):
        """Load ML models from specified paths."""
        
        for model_name, model_path in model_paths.items():
            try:
                if model_path.endswith('.tflite'):
                    model = self.load_tflite_model(model_path)
                elif model_path.endswith('.onnx'):
                    model = self.load_onnx_model(model_path)
                elif model_path.endswith('.pkl'):
                    model = self.load_sklearn_model(model_path)
                else:
                    raise ValueError(f"Unsupported model format: {model_path}")
                
                self.models[model_name] = model
                self.model_metadata[model_name] = self.extract_model_metadata(model_path)
                
                logging.info(f"Loaded model {model_name} from {model_path}")
                
            except Exception as e:
                logging.error(f"Failed to load model {model_name}: {e}")
                raise
    
    def load_tflite_model(self, model_path: str):
        """Load TensorFlow Lite model."""
        import tensorflow as tf
        
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        return {
            'type': 'tflite',
            'interpreter': interpreter,
            'input_details': interpreter.get_input_details(),
            'output_details': interpreter.get_output_details()
        }
    
    def predict_gsr(self, feature_data: dict, device_id: str) -> dict:
        """Predict GSR value from processed features."""
        
        if 'gsr_prediction' not in self.models:
            raise RuntimeError("GSR prediction model not loaded")
        
        model = self.models['gsr_prediction']
        
        try:
            # Prepare input features
            input_features = self.prepare_gsr_features(feature_data)
            
            # Perform prediction based on model type
            if model['type'] == 'tflite':
                prediction_result = self.predict_tflite(model, input_features)
            else:
                raise ValueError(f"Unsupported model type: {model['type']}")
            
            # Post-process prediction
            processed_result = self.post_process_gsr_prediction(
                prediction_result, device_id
            )
            
            # Update prediction history
            self.update_prediction_history(device_id, processed_result)
            
            return processed_result
            
        except Exception as e:
            logging.error(f"GSR prediction failed: {e}")
            return {
                'prediction': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def prepare_gsr_features(self, feature_data: dict) -> np.ndarray:
        """Prepare feature vector for GSR prediction model."""
        
        features = []
        
        # RGB signal features
        if 'rgb_signals' in feature_data:
            for roi_signal in feature_data['rgb_signals']:
                if isinstance(roi_signal, dict):
                    features.extend([
                        roi_signal.get('mean_r', 0.0),
                        roi_signal.get('mean_g', 0.0),
                        roi_signal.get('mean_b', 0.0),
                        roi_signal.get('variance', 0.0),
                        roi_signal.get('green_ac_component', 0.0)
                    ])
        
        # Thermal signal features
        if 'thermal_signals' in feature_data:
            for thermal_signal in feature_data['thermal_signals']:
                if isinstance(thermal_signal, dict):
                    features.extend([
                        thermal_signal.get('mean_temperature', 0.0),
                        thermal_signal.get('temperature_variance', 0.0),
                        thermal_signal.get('max_temperature', 0.0),
                        thermal_signal.get('min_temperature', 0.0)
                    ])
        
        # Temporal features
        if 'temporal_features' in feature_data:
            temporal = feature_data['temporal_features']
            for modality in ['rgb', 'thermal', 'fused']:
                if modality in temporal:
                    modal_features = temporal[modality]
                    features.extend([
                        np.mean(modal_features.get('mean', [0.0])),
                        np.mean(modal_features.get('std', [0.0])),
                        np.mean(modal_features.get('variance', [0.0]))
                    ])
        
        # Ensure consistent feature vector length
        feature_array = np.array(features, dtype=np.float32)
        
        # Pad or truncate to expected model input size
        expected_size = self.model_metadata.get('gsr_prediction', {}).get('input_size', 50)
        if len(feature_array) < expected_size:
            feature_array = np.pad(feature_array, (0, expected_size - len(feature_array)))
        elif len(feature_array) > expected_size:
            feature_array = feature_array[:expected_size]
        
        return feature_array.reshape(1, -1)  # Batch dimension
    
    def predict_tflite(self, model: dict, input_features: np.ndarray) -> dict:
        """Perform inference using TensorFlow Lite model."""
        
        interpreter = model['interpreter']
        input_details = model['input_details']
        output_details = model['output_details']
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], input_features)
        
        # Run inference
        interpreter.invoke()
        
        # Extract outputs
        prediction = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Extract confidence if available
        confidence = 1.0
        if len(output_details) > 1:
            confidence = interpreter.get_tensor(output_details[1]['index'])[0]
        
        return {
            'prediction': float(prediction),
            'confidence': float(confidence)
        }
    
    def post_process_gsr_prediction(self, raw_prediction: dict, device_id: str) -> dict:
        """Post-process raw model prediction."""
        
        prediction = raw_prediction['prediction']
        confidence = raw_prediction['confidence']
        
        # Apply temporal smoothing if history available
        if device_id in self.prediction_history:
            history = self.prediction_history[device_id]
            if len(history) > 0:
                # Simple exponential smoothing
                alpha = 0.3
                smoothed_prediction = alpha * prediction + (1 - alpha) * history[-1]['prediction']
                prediction = smoothed_prediction
        
        # Clamp prediction to physiologically reasonable range
        prediction = max(0.1, min(100.0, prediction))
        
        # Adjust confidence based on prediction stability
        if device_id in self.prediction_history:
            stability = self.compute_prediction_stability(device_id)
            confidence *= stability
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': time.time(),
            'device_id': device_id
        }
    
    def compute_prediction_stability(self, device_id: str) -> float:
        """Compute prediction stability coefficient."""
        
        if device_id not in self.prediction_history:
            return 1.0
        
        history = self.prediction_history[device_id]
        if len(history) < 5:
            return 1.0
        
        # Calculate coefficient of variation for recent predictions
        recent_predictions = [p['prediction'] for p in history[-10:]]
        mean_prediction = np.mean(recent_predictions)
        std_prediction = np.std(recent_predictions)
        
        if mean_prediction == 0:
            return 0.0
        
        cv = std_prediction / mean_prediction
        
        # Convert to stability measure (lower CV = higher stability)
        stability = 1.0 / (1.0 + cv)
        
        return stability
```

## 5. Data Visualization and User Interface

### 5.1 Advanced Visualization System

The visualization system provides comprehensive real-time and offline analysis capabilities with scientific-grade plotting and interactive exploration features.

**5.1.1 Visualization Manager**

```python
class VisualizationManager(QObject):
    """
    Comprehensive visualization system managing real-time data display,
    scientific plotting, and interactive analysis interfaces.
    """
    
    plot_updated = pyqtSignal(str)
    visualization_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Matplotlib configuration
        matplotlib.use('Qt5Agg')
        plt.style.use('seaborn-v0_8-darkgrid')  # Scientific plotting style
        
        # Plot managers
        self.real_time_plots = {}
        self.analysis_plots = {}
        self.comparison_plots = {}
        
        # Data management
        self.plot_data_manager = PlotDataManager()
        self.color_manager = ColorManager()
        
        # Performance optimization
        self.animation_manager = AnimationManager()
        
        self.setup_visualization_environment()
    
    def setup_visualization_environment(self):
        """Configure visualization environment and default settings."""
        
        # Configure matplotlib for optimal performance
        matplotlib.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'black',
            'axes.linewidth': 1.0,
            'xtick.direction': 'in',
            'ytick.direction': 'in',
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9
        })
    
    def create_real_time_plot(self, plot_id: str, config: dict) -> QWidget:
        """Create real-time plotting widget."""
        
        plot_widget = RealTimePlotWidget(
            plot_id=plot_id,
            config=config,
            data_manager=self.plot_data_manager,
            color_manager=self.color_manager
        )
        
        self.real_time_plots[plot_id] = plot_widget
        
        # Setup data update connections
        plot_widget.data_update_requested.connect(
            self.handle_plot_update_request
        )
        
        return plot_widget
    
    def update_real_time_data(self, plot_id: str, device_id: str, data: dict):
        """Update real-time plot with new data."""
        
        if plot_id in self.real_time_plots:
            self.real_time_plots[plot_id].add_data_point(device_id, data)
            
    def create_analysis_plot(self, analysis_type: str, data: dict, config: dict = None) -> QWidget:
        """Create analysis visualization widget."""
        
        if analysis_type == 'correlation_analysis':
            return self.create_correlation_plot(data, config)
        elif analysis_type == 'spectral_analysis':
            return self.create_spectral_plot(data, config)
        elif analysis_type == 'statistical_summary':
            return self.create_statistical_plot(data, config)
        elif analysis_type == 'time_series_comparison':
            return self.create_comparison_plot(data, config)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")


class RealTimePlotWidget(QWidget):
    """
    High-performance real-time plotting widget optimized for continuous
    data streaming with multiple channels and devices.
    """
    
    data_update_requested = pyqtSignal(str)
    
    def __init__(self, plot_id: str, config: dict, data_manager, color_manager):
        super().__init__()
        
        self.plot_id = plot_id
        self.config = config
        self.data_manager = data_manager
        self.color_manager = color_manager
        
        # Plot configuration
        self.max_points = config.get('max_points', 1000)
        self.update_interval = config.get('update_interval', 100)  # ms
        self.channels = config.get('channels', ['gsr_prediction'])
        
        # Data storage
        self.plot_data = {}
        self.device_colors = {}
        
        # Matplotlib setup
        self.figure = plt.Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Create subplots based on configuration
        self.create_subplots()
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_plots)
        self.animation_timer.start(self.update_interval)
    
    def create_subplots(self):
        """Create subplot layout based on configuration."""
        
        subplot_count = len(self.channels)
        self.subplots = {}
        
        for i, channel in enumerate(self.channels):
            ax = self.figure.add_subplot(subplot_count, 1, i + 1)
            
            # Configure subplot
            ax.set_title(self.get_channel_title(channel))
            ax.set_ylabel(self.get_channel_ylabel(channel))
            ax.grid(True, alpha=0.3)
            
            if i == subplot_count - 1:  # Last subplot
                ax.set_xlabel('Time (seconds)')
            
            self.subplots[channel] = ax
        
        self.figure.tight_layout()
    
    def add_data_point(self, device_id: str, data: dict):
        """Add new data point for specified device."""
        
        timestamp = data.get('timestamp', time.time())
        
        # Initialize device data if needed
        if device_id not in self.plot_data:
            self.plot_data[device_id] = {
                'timestamps': deque(maxlen=self.max_points),
                'data': {channel: deque(maxlen=self.max_points) for channel in self.channels}
            }
            
            # Assign color for device
            self.device_colors[device_id] = self.color_manager.get_device_color(device_id)
        
        # Add timestamp
        self.plot_data[device_id]['timestamps'].append(timestamp)
        
        # Add data for each channel
        for channel in self.channels:
            value = self.extract_channel_value(data, channel)
            self.plot_data[device_id]['data'][channel].append(value)
    
    def update_plots(self):
        """Update all subplots with latest data."""
        
        if not self.plot_data:
            return
        
        # Get current time for relative time calculation
        current_time = time.time()
        
        for channel, ax in self.subplots.items():
            ax.clear()
            
            # Reconfigure subplot
            ax.set_title(self.get_channel_title(channel))
            ax.set_ylabel(self.get_channel_ylabel(channel))
            ax.grid(True, alpha=0.3)
            
            # Plot data for each device
            for device_id, device_data in self.plot_data.items():
                if device_data['timestamps'] and device_data['data'][channel]:
                    # Convert to numpy arrays for efficient plotting
                    timestamps = np.array(device_data['timestamps'])
                    values = np.array(device_data['data'][channel])
                    
                    # Convert to relative time (last 60 seconds)
                    relative_times = timestamps - current_time
                    
                    # Plot with device-specific color
                    color = self.device_colors[device_id]
                    ax.plot(
                        relative_times, 
                        values, 
                        color=color, 
                        label=f"Device {device_id}",
                        linewidth=2,
                        alpha=0.8
                    )
            
            # Configure x-axis for time display
            ax.set_xlim(-60, 0)  # Show last 60 seconds
            ax.set_xlabel('Time (seconds ago)')
            
            # Add legend if multiple devices
            if len(self.plot_data) > 1:
                ax.legend(loc='upper left')
        
        # Refresh canvas
        self.canvas.draw_idle()
    
    def extract_channel_value(self, data: dict, channel: str) -> float:
        """Extract specific channel value from data dictionary."""
        
        if channel == 'gsr_prediction':
            return data.get('gsr_prediction', 0.0)
        elif channel == 'confidence':
            return data.get('confidence', 0.0)
        elif channel == 'signal_quality':
            return data.get('signal_quality', 0.0)
        elif channel == 'rgb_signal':
            rgb_data = data.get('rgb_signals', [])
            if rgb_data and len(rgb_data) > 0:
                return rgb_data[0].get('mean_g', 0.0)  # Green channel
            return 0.0
        elif channel == 'thermal_signal':
            thermal_data = data.get('thermal_signals', [])
            if thermal_data and len(thermal_data) > 0:
                return thermal_data[0].get('mean_temperature', 0.0)
            return 0.0
        else:
            return data.get(channel, 0.0)
    
    def get_channel_title(self, channel: str) -> str:
        """Get display title for channel."""
        
        titles = {
            'gsr_prediction': 'GSR Prediction (μS)',
            'confidence': 'Prediction Confidence',
            'signal_quality': 'Signal Quality',
            'rgb_signal': 'RGB Signal (Green Channel)',
            'thermal_signal': 'Thermal Signal (°C)'
        }
        
        return titles.get(channel, channel.title())
    
    def get_channel_ylabel(self, channel: str) -> str:
        """Get y-axis label for channel."""
        
        labels = {
            'gsr_prediction': 'GSR (μS)',
            'confidence': 'Confidence',
            'signal_quality': 'Quality Score',
            'rgb_signal': 'Amplitude',
            'thermal_signal': 'Temperature (°C)'
        }
        
        return labels.get(channel, 'Value')
```

This completes a substantial portion of the Python Desktop Application Design document. The document covers the application architecture, device management and communication, real-time data processing and analysis, machine learning integration, and data visualization systems with detailed implementation examples.

Would you like me to:
1. Continue with the remaining sections of this document (data management, configuration, testing, etc.)
2. Move on to create the next document in the series (Networking & Synchronization)
3. Create additional documents from Chapter 4

Let me know how you'd like to proceed!