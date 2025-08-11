# Appendix E.3: Network Performance Analysis Evidence

## Overview

This appendix provides evidence for network performance claims in Chapter 6, including latency measurements and scalability testing results.

## Latency Measurements

### Ethernet Performance
- **Median Latency:** 15.1 ms
- **95th Percentile:** 19.9 ms
- **Mean Latency:** 15.1 ms
- **Sample Size:** 1000 measurements

### WiFi Performance
- **Median Latency:** 119.5 ms
- **95th Percentile:** 159.6 ms
- **Mean Latency:** 119.3 ms
- **Sample Size:** 1000 measurements

### TLS Encryption Overhead
- **Mean Overhead:** 12.1 ms
- **Median Overhead:** 12.0 ms

## Scalability Testing

- **Maximum Tested Devices:** 6
- **Reliable Device Limit:** 6
- **Timeout Increase Beyond Limit:** 4.8s average

### Device Count vs Performance

| Device Count | Average Timeout (s) | Reliable |
|--------------|--------------------|-----------|
| 1 | 1.2 | Yes |
| 2 | 1.3 | Yes |
| 3 | 1.4 | Yes |
| 4 | 1.5 | Yes |
| 5 | 1.6 | Yes |
| 6 | 1.7 | Yes |
| 7 | 4.8 | No |

## Evidence Files

Complete network performance data is available in:
`results/appendix_evidence/network_performance_20250811_012938.json`

**Citation Reference:** Reference as "Network performance measurements (Appendix E.3) show 95th percentile latencies of X ms on Ethernet and Y ms on WiFi."
