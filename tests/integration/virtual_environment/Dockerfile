# Virtual Test Environment Dockerfile
# 
# This Docker image provides a complete environment for running the virtual
# test environment without requiring local installation of dependencies.
# It includes all necessary Python packages and is optimized for both
# local development and CI usage.

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml pytest.ini ./
COPY PythonApp/requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    pytest>=8.4.0 \
    pytest-asyncio>=0.23.0 \
    psutil>=5.9.0 \
    numpy>=1.26.0 \
    opencv-python-headless>=4.12.0 \
    PyQt5>=5.15.11 \
    websockets>=13.1 \
    requests>=2.32.0 \
    pillow>=10.4.0

# Copy the application code
COPY PythonApp/ ./PythonApp/
COPY tests/ ./tests/
COPY protocol/ ./protocol/

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Create output directory
RUN mkdir -p /app/test_results

# Set environment variables for headless operation
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=""
ENV GSR_TEST_HEADLESS=true
ENV GSR_TEST_OUTPUT_DIR=/app/test_results

# Expose the default server port
EXPOSE 9000

# Set the entrypoint to the virtual test runner
ENTRYPOINT ["python", "-m", "tests.integration.virtual_environment.test_runner"]

# Default command runs a quick CI test
CMD ["--scenario", "ci", "--devices", "3", "--duration", "2.0", "--verbose"]