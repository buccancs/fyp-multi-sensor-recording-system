"""
Test Categories and Enumerations

Defines the test categories and classification systems used throughout
the evaluation suite.
"""

from enum import Enum, auto
from typing import Dict, Any
from dataclasses import dataclass


class TestCategory(Enum):
    """Test category classifications following the multi-level testing approach"""
    FOUNDATION = auto()      # Foundation Testing Layer - Unit tests
    INTEGRATION = auto()     # Integration Testing Layer - Component interactions
    SYSTEM = auto()         # System Testing Layer - End-to-end workflows
    PERFORMANCE = auto()    # Performance and Reliability Testing Layer


class TestType(Enum):
    """Specific test type classifications"""
    # Foundation Layer Types
    UNIT_ANDROID = auto()
    UNIT_PC = auto()
    ALGORITHM_VALIDATION = auto()
    
    # Integration Layer Types
    MULTI_DEVICE = auto()
    NETWORK_PERFORMANCE = auto()
    SYNCHRONIZATION = auto()
    
    # System Layer Types
    END_TO_END = auto()
    DATA_INTEGRITY = auto()
    WORKFLOW_VALIDATION = auto()
    
    # Performance Layer Types
    THROUGHPUT = auto()
    SCALABILITY = auto()
    RELIABILITY = auto()
    FAULT_TOLERANCE = auto()
    USABILITY = auto()


class TestPriority(Enum):
    """Test priority levels for execution ordering"""
    CRITICAL = 1    # Must pass for system to be functional
    HIGH = 2       # Important for research-grade quality
    MEDIUM = 3     # Valuable for optimization and robustness
    LOW = 4        # Nice-to-have features and edge cases


@dataclass
class TestConfiguration:
    """Configuration parameters for test execution"""
    timeout_seconds: int = 300
    retry_attempts: int = 3
    parallel_execution: bool = False
    cleanup_on_failure: bool = True
    collect_metrics: bool = True
    generate_reports: bool = True
    

@dataclass
class QualityThresholds:
    """Quality thresholds for test validation"""
    minimum_success_rate: float = 0.95         # 95% tests must pass
    maximum_execution_time: float = 1800.0     # 30 minutes max
    minimum_coverage: float = 0.80              # 80% code coverage
    maximum_memory_mb: int = 1000               # 1GB memory limit
    maximum_cpu_percent: float = 60.0           # 60% CPU usage limit
    maximum_latency_ms: float = 100.0           # 100ms latency limit
    minimum_quality_score: float = 0.85         # Overall quality score >0.85
    
    # Research-specific thresholds
    sync_precision_ms: float = 1.0              # 1ms synchronization precision
    data_quality_score: float = 0.8             # Data quality threshold
    measurement_accuracy: float = 0.95          # Measurement accuracy requirement