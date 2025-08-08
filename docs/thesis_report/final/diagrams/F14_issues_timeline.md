# F14: Known Issues Timeline

```mermaid
gantt
    title System Issues During Recording Session
    dateFormat YYYY-MM-DD
    axisFormat %M:%S
    
    section Critical Issues
    Device Discovery Failed (Node 1)    :crit, d1, 2024-01-01, 3s
    UI Freeze Episode 1                 :crit, u1, 2024-01-01, 4s
    Calibration Failure                 :crit, c1, 2024-01-01, 3s
    UI Freeze Episode 2                 :crit, u2, 2024-01-01, 4s
    UI Freeze Episode 3                 :crit, u3, 2024-01-01, 3s
    Device Discovery Failed (Node 3)    :crit, d3, 2024-01-01, 3s
    
    section Connection Issues
    Node 2 Heartbeat Loss              :active, h2, 2024-01-01, 2s
    Node 1 Heartbeat Loss              :active, h1, 2024-01-01, 2s
    Node 3 Heartbeat Loss              :active, h3, 2024-01-01, 2s
    
    section Performance Issues
    RGB Frame Drops                    :done, f1, 2024-01-01, 3s
    GSR Sampling Gaps                  :done, g1, 2024-01-01, 3s
    Thermal Frame Drops                :done, f2, 2024-01-01, 3s
    
    section Recovery Events
    Node 1 Reconnect Success           :milestone, r1, 2024-01-01, 0s
    Calibration Retry Success          :milestone, r2, 2024-01-01, 0s
    Node 3 Reconnect Success           :milestone, r3, 2024-01-01, 0s
    Node 1 Transfer Retry              :milestone, t1, 2024-01-01, 0s
    Node 2 Transfer Retry              :milestone, t2, 2024-01-01, 0s
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