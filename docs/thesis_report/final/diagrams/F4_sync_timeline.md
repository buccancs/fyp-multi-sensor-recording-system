# F4: Synchronized Start Trigger Timeline

```mermaid
gantt
    title Synchronized Recording Start Timeline
    dateFormat X
    axisFormat %L ms
    
    section PC Master
    Generate Master Timestamp     :milestone, m1, 0, 0ms
    Broadcast Start Commands      :active, 0, 5ms
    
    section Android Node 1
    Receive Start Command         :2, 7ms
    Apply Clock Offset (-2.1ms)   :3, 9ms
    Begin RGB Capture            :milestone, 4, 10ms
    Begin Thermal Capture        :milestone, 5, 10ms
    Begin GSR Logging            :milestone, 6, 10ms
    
    section Android Node 2  
    Receive Start Command         :7, 6ms
    Apply Clock Offset (+1.3ms)   :8, 8ms
    Begin RGB Capture            :milestone, 9, 11ms
    Begin Thermal Capture        :milestone, 10, 11ms
    Begin GSR Logging            :milestone, 11, 11ms
    
    section Android Node 3
    Receive Start Command         :12, 8ms
    Apply Clock Offset (-0.7ms)   :13, 10ms
    Begin RGB Capture            :milestone, 14, 12ms
    Begin Thermal Capture        :milestone, 15, 12ms
    Begin GSR Logging            :milestone, 16, 12ms
    
    section Synchronization Window
    Target Sync Window (±5ms)     :crit, sync, 5, 15ms
```

## Timeline Analysis
- **Master Timestamp**: t=0 (PC local time)
- **Node 1 Offset**: -2.1ms → Effective start at t=10ms
- **Node 2 Offset**: +1.3ms → Effective start at t=11ms  
- **Node 3 Offset**: -0.7ms → Effective start at t=12ms
- **Sync Jitter**: 2ms range (within ±5ms target window)

## Description
Shows temporal alignment of recording start across distributed nodes. Each device applies its calculated clock offset to achieve synchronized capture initiation within the target timing window.