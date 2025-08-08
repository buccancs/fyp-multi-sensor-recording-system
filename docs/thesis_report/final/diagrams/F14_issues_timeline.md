# F14: Known Issues Timeline

```mermaid
timeline
    title System Issues During Recording Session
    
    section Early Session (0-30s)
        5-8s    : Device Discovery Failed (Node 1)
        12s     : Node 1 Reconnect Success
        15-18s  : Calibration Failure
        23-27s  : UI Freeze Episode 1
        25s     : Calibration Retry Success
    
    section Mid Session (30-60s)
        34-36s  : Node 2 Heartbeat Loss
        38-41s  : RGB Frame Drops
        45-48s  : Device Discovery Failed (Node 3)
        52s     : Node 3 Reconnect Success
        58-61s  : GSR Sampling Gaps
    
    section Late Session (60-120s)
        67-71s  : UI Freeze Episode 2
        73-76s  : Thermal Frame Drops
        78-80s  : Node 1 Heartbeat Loss
        89-92s  : UI Freeze Episode 3
        95-97s  : Node 3 Heartbeat Loss
        105-108s: Node 1 Transfer Retry
        112-114s: Node 2 Transfer Retry
```

## Issue Classification

### Critical Issues (System Blocking)
- **Device Discovery Failures**: Devices not found on first attempt
- **UI Freeze Episodes**: Complete UI unresponsiveness requiring restart
- **Calibration Failures**: Thermal-RGB alignment errors

### Active Issues (Degraded Performance)
- **Heartbeat Losses**: Temporary connection interruptions
- **Frame Drops**: Missed video frames during high load
- **Transfer Retries**: File transfer requiring multiple attempts
- **Sampling Gaps**: Missing sensor data points

### Recovery Patterns
- **Discovery**: 3-7 second recovery time with automatic retry
- **UI Freezes**: 4-5 second duration, manual intervention required
- **Heartbeat**: 2-3 second recovery with automatic reconnection
- **Calibration**: 10 second retry cycle with operator assistance

## Description
Documents the timeline and frequency of known system limitations during a typical recording session. Shows issue clustering, recovery patterns, and operator intervention points.