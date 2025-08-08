# F3: Device Discovery & Handshake Sequence

```mermaid
sequenceDiagram
    participant PC as PC Server
    participant AN as Android Node
    
    Note over PC,AN: Discovery Phase
    PC->>AN: UDP Broadcast Discovery
    Note right of AN: Device listening on network
    
    alt Device Available
        AN-->>PC: Discovery Response (device_id, ip)
        Note left of PC: Add to discovered devices
        
        Note over PC,AN: Handshake Phase
        PC->>AN: TCP Connect
        PC->>AN: HelloMessage
        Note right of AN: Validate connection
        
        AN-->>PC: Capabilities Response
        Note over AN: capabilities:<br/>rgb_camera: true<br/>thermal_camera: true<br/>gsr_sensor: true<br/>preview_stream: true
        
        PC->>PC: Create ConnectedDevice
        PC-->>AN: Handshake Complete
        
        Note over PC,AN: Heartbeat Monitoring
        loop Every 5 seconds
            PC->>AN: Heartbeat Request
            AN-->>PC: Heartbeat Response
        end
        
    else Device Unavailable
        Note right of AN: No response
        PC->>PC: Discovery Timeout
        Note left of PC: Retry after delay
    end
    
    Note over PC,AN: Connection Failure Handling
    alt Heartbeat Lost
        PC->>AN: Heartbeat Request
        Note right of AN: Device disconnected
        PC->>PC: Mark Device as Lost
        PC->>PC: Attempt Reconnection
        
        loop Retry Attempts (max 3)
            PC->>AN: Reconnect Attempt
            alt Reconnection Success
                AN-->>PC: Connection Restored
                PC->>PC: Resume Normal Operation
            else Reconnection Failed
                PC->>PC: Increment Retry Count
            end
        end
        
        Note left of PC: Remove from active devices if max retries exceeded
    end
```

## Description
Details the device discovery protocol with UDP broadcast, TCP handshake, capability negotiation, and failure recovery mechanisms. Shows the reliability patterns for maintaining device connections.