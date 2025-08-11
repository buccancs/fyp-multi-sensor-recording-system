# Virtual Test Environment Makefile
# 
# This Makefile provides convenient targets for running the virtual test
# environment in various configurations. It simplifies common development
# and testing workflows.

.PHONY: help test quick-test stress-test ci-test docker-test clean examples
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
VENV_DIR := venv
RESULTS_DIR := test_results
CONFIGS_DIR := test_configs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "Virtual Test Environment - Available Targets"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# Setup and installation
setup: ## Install dependencies and setup environment
	@echo "$(BLUE)Setting up virtual test environment...$(NC)"
	@cd ../../../ && $(PYTHON) -m pip install --upgrade pip setuptools wheel
	@cd ../../../ && $(PYTHON) -m pip install -e .
	@cd ../../../ && $(PYTHON) -m pip install pytest pytest-asyncio psutil numpy opencv-python-headless
	@mkdir -p $(RESULTS_DIR) $(CONFIGS_DIR)
	@echo "$(GREEN)✓ Setup completed$(NC)"

# Basic tests
test: setup ## Run default test (quick scenario)
	@echo "$(BLUE)Running default virtual test...$(NC)"
	@$(PYTHON) test_runner.py --scenario quick --devices 3 --duration 2.0 --verbose

quick-test: setup ## Run quick test (1 minute, 2 devices)
	@echo "$(BLUE)Running quick test...$(NC)"
	@$(PYTHON) test_runner.py --scenario quick --devices 2 --duration 1.0 --verbose

ci-test: setup ## Run CI test (conservative settings)
	@echo "$(BLUE)Running CI test...$(NC)"
	@$(PYTHON) test_runner.py --scenario ci --devices 3 --duration 2.0 --verbose

stress-test: setup ## Run stress test (6 devices, 10 minutes)
	@echo "$(BLUE)Running stress test...$(NC)"
	@$(PYTHON) test_runner.py --scenario stress --devices 6 --duration 10.0 --verbose

sync-test: setup ## Run synchronization test
	@echo "$(BLUE)Running synchronization test...$(NC)"
	@$(PYTHON) test_runner.py --scenario sync --devices 5 --duration 5.0 --verbose

# Docker targets
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t gsr-virtual-test -f Dockerfile ../../..

docker-test: docker-build ## Run test in Docker container
	@echo "$(BLUE)Running Docker test...$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@docker run --rm \
		-v $(PWD)/$(RESULTS_DIR):/app/test_results \
		-e GSR_TEST_CI_MODE=true \
		gsr-virtual-test --scenario ci --devices 3 --duration 2.0 --verbose

docker-compose-test: ## Run test using Docker Compose
	@echo "$(BLUE)Running Docker Compose test...$(NC)"
	@docker-compose up --abort-on-container-exit virtual-test

docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	@docker-compose down --remove-orphans || true
	@docker rmi gsr-virtual-test || true
	@docker system prune -f

# Development and examples
examples: setup ## Run example usage scripts
	@echo "$(BLUE)Running usage examples...$(NC)"
	@$(PYTHON) examples.py

quick-examples: setup ## Run quick examples only
	@echo "$(BLUE)Running quick examples...$(NC)"
	@$(PYTHON) quick_test.py

validate-config: ## Validate test configurations
	@echo "$(BLUE)Validating test configurations...$(NC)"
	@$(PYTHON) -c "
from test_config import TestScenario, create_test_matrix
scenarios = create_test_matrix()
for scenario in scenarios:
    issues = scenario.config.validate()
    if issues:
        print(f'$(YELLOW)WARNING$(NC): {scenario.name} has issues: {issues}')
    else:
        print(f'$(GREEN)✓$(NC) {scenario.name} configuration valid')
"

# Testing matrix
test-matrix: setup ## Run test matrix (multiple scenarios)
	@echo "$(BLUE)Running test matrix...$(NC)"
	@for scenario in quick ci; do \
		echo "$(BLUE)Testing scenario: $$scenario$(NC)"; \
		$(PYTHON) test_runner.py --scenario $$scenario --devices 2 --duration 1.0 || true; \
		sleep 5; \
	done

# Performance and monitoring
performance-test: setup ## Run performance baseline test
	@echo "$(BLUE)Running performance test...$(NC)"
	@$(PYTHON) test_runner.py --scenario stress --devices 4 --duration 5.0 --verbose

memory-test: setup ## Run memory leak detection test
	@echo "$(BLUE)Running memory leak detection test...$(NC)"
	@$(PYTHON) -c "
import asyncio
from test_config import VirtualTestConfig
from test_runner import VirtualTestRunner
import logging

async def memory_test():
    config = VirtualTestConfig(
        test_name='memory_test',
        device_count=3,
        test_duration_minutes=3.0,
        enable_performance_monitoring=True,
        monitoring_interval_seconds=10.0,
        memory_leak_threshold_mb=50.0
    )
    
    runner = VirtualTestRunner(config, logging.getLogger())
    metrics = await runner.run_test()
    
    print(f'Peak memory: {metrics.peak_memory_mb:.1f}MB')
    print(f'Memory leak detection: {\"PASSED\" if metrics.performance_passed else \"FAILED\"}')
    
    return metrics.overall_passed

result = asyncio.run(memory_test())
exit(0 if result else 1)
"

# Utilities
clean: ## Clean test results and temporary files
	@echo "$(BLUE)Cleaning test results...$(NC)"
	@rm -rf $(RESULTS_DIR)/*
	@rm -rf __pycache__ .pytest_cache
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean docker-clean ## Clean everything including Docker resources

status: ## Show system status and requirements
	@echo "$(BLUE)System Status$(NC)"
	@echo "============="
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "$(BLUE)Test Environment Status$(NC)"
	@echo "========================="
	@echo "Results directory: $(RESULTS_DIR) ($$(ls -la $(RESULTS_DIR) 2>/dev/null | wc -l) files)"
	@echo "Available scenarios: quick, ci, stress, sync"
	@echo "Last test: $$(ls -t $(RESULTS_DIR)/*_report.json 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"

results: ## Show recent test results
	@echo "$(BLUE)Recent Test Results$(NC)"
	@echo "==================="
	@if [ -d "$(RESULTS_DIR)" ] && [ "$$(ls -A $(RESULTS_DIR))" ]; then \
		for report in $$(ls -t $(RESULTS_DIR)/*_report.json 2>/dev/null | head -5); do \
			if [ -f "$$report" ]; then \
				test_name=$$(basename "$$report" _report.json); \
				passed=$$(grep -o '"overall_passed": *[^,}]*' "$$report" | cut -d: -f2 | tr -d ' "'); \
				devices=$$(grep -o '"devices_connected": *"[^"]*"' "$$report" | cut -d: -f2 | tr -d ' "'); \
				samples=$$(grep -o '"data_samples_collected": *[^,}]*' "$$report" | cut -d: -f2 | tr -d ' '); \
				if [ "$$passed" = "true" ]; then \
					echo "$(GREEN)✓$(NC) $$test_name: $$devices devices, $$samples samples"; \
				else \
					echo "$(RED)✗$(NC) $$test_name: $$devices devices, $$samples samples"; \
				fi; \
			fi; \
		done; \
	else \
		echo "No test results found. Run 'make test' to generate results."; \
	fi

# Debugging and development
debug: setup ## Run test with debug logging
	@echo "$(BLUE)Running debug test...$(NC)"
	@GSR_TEST_LOG_LEVEL=DEBUG $(PYTHON) test_runner.py --scenario quick --devices 1 --duration 0.5 --verbose

minimal: setup ## Run minimal test (fastest possible)
	@echo "$(BLUE)Running minimal test...$(NC)"
	@$(PYTHON) test_runner.py --scenario quick --devices 1 --duration 0.2 --verbose

shell: setup ## Start interactive Python shell with environment loaded
	@echo "$(BLUE)Starting interactive shell...$(NC)"
	@$(PYTHON) -c "
from test_config import *
from test_runner import *
from virtual_device_client import *
from synthetic_data_generator import *
print('Virtual test environment loaded. Available classes:')
print('- VirtualTestConfig, TestScenario')
print('- VirtualTestRunner')  
print('- VirtualDeviceClient, VirtualDeviceConfig')
print('- SyntheticDataGenerator')
print('\\nTry: config = VirtualTestConfig()')
import code; code.interact(local=locals())
"

# Help for CI/CD
ci-help: ## Show CI/CD integration help
	@echo "$(BLUE)CI/CD Integration Examples$(NC)"
	@echo "=========================="
	@echo ""
	@echo "GitHub Actions:"
	@echo "  - name: Run Virtual GSR Test"
	@echo "    run: |"
	@echo "      cd tests/integration/virtual_environment"
	@echo "      make ci-test"
	@echo ""
	@echo "Docker CI:"
	@echo "  docker run --rm gsr-virtual-test --scenario ci --devices 3"
	@echo ""
	@echo "Local CI simulation:"
	@echo "  make ci-test"
	@echo ""
	@echo "For more details, see README.md"

# Documentation
docs: ## Generate/update documentation
	@echo "$(BLUE)Documentation locations:$(NC)"
	@echo "- README.md: Comprehensive usage guide"
	@echo "- examples.py: Code examples and patterns"
	@echo "- test_config.py: Configuration options"
	@echo "- Dockerfile: Container configuration"
	@echo "- docker-compose.yml: Multi-service setup"