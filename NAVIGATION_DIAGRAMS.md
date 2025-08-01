# Navigation Flow Diagram

## Current Navigation Structure

```mermaid
graph TD
    A[MainActivity<br/>Recording Interface] --> B[Options Menu]
    
    B --> C[Settings Activity]
    B --> D[Network Config]
    B --> E[File Browser]
    B --> F[Shimmer Config]
    B --> G[Sync Testing Menu]
    
    G --> G1[Test Flash Sync]
    G --> G2[Test Beep Sync] 
    G --> G3[Test Clock Sync]
    G --> G4[Show Sync Status]
    
    B --> H[About Dialog]
    
    C --> C1[Recording Settings]
    C --> C2[System Preferences]
    C --> C3[Shimmer MAC Config]
    
    D --> D1[Server IP Config]
    D --> D2[Port Configuration]
    D --> D3[Connection Testing]
    
    E --> E1[Session Files]
    E --> E2[Recording Data]
    E --> E3[Export Options]
    E --> E4[File Operations]
    
    F --> F1[Device Discovery]
    F --> F2[Sensor Configuration]
    F --> F3[Streaming Controls]
    F --> F4[Device Management]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
```

## Proposed Modern Navigation Structure

```mermaid
graph TD
    MainApp[Bucika GSR App] --> BottomNav[Bottom Navigation]
    
    BottomNav --> Tab1[🎬 Recording]
    BottomNav --> Tab2[📊 Monitoring]
    BottomNav --> Tab3[🗂️ Files]
    BottomNav --> Tab4[⚙️ Settings]
    BottomNav --> Tab5[🔧 Advanced]
    
    %% Recording Tab Flow
    Tab1 --> Rec1[Device Status Cards]
    Tab1 --> Rec2[Recording Controls FAB]
    Tab1 --> Rec3[Real-time Indicators]
    Tab1 --> Rec4[Quick Actions]
    
    Rec4 --> Rec4a[Calibration]
    Rec4 --> Rec4b[Hand Segmentation]
    Rec4 --> Rec4c[Sync Testing]
    
    %% Monitoring Tab Flow
    Tab2 --> Mon1[Live Data Dashboard]
    Tab2 --> Mon2[Sensor Health]
    Tab2 --> Mon3[Performance Metrics]
    Tab2 --> Mon4[Alert Center]
    
    Mon1 --> Mon1a[GSR Chart]
    Mon1 --> Mon1b[Thermal Display]
    Mon1 --> Mon1c[Video Preview]
    
    %% Files Tab Flow
    Tab3 --> File1[Session Browser]
    Tab3 --> File2[Search & Filter]
    Tab3 --> File3[Export Tools]
    Tab3 --> File4[Storage Management]
    
    File1 --> File1a[Grid View]
    File1 --> File1b[List View]
    File1 --> File1c[Timeline View]
    
    File3 --> File3a[Share Session]
    File3 --> File3b[Batch Export]
    File3 --> File3c[Cloud Sync]
    
    %% Settings Tab Flow
    Tab4 --> Set1[Device Settings]
    Tab4 --> Set2[Recording Preferences]
    Tab4 --> Set3[Network Configuration]
    Tab4 --> Set4[App Preferences]
    
    Set1 --> Set1a[Shimmer Config]
    Set1 --> Set1b[Camera Settings]
    Set1 --> Set1c[USB Devices]
    
    Set2 --> Set2a[Video Quality]
    Set2 --> Set2b[Sample Rates]
    Set2 --> Set2c[File Formats]
    
    Set3 --> Set3a[Server Settings]
    Set3 --> Set3b[WiFi Config]
    Set3 --> Set3c[Connection Test]
    
    %% Advanced Tab Flow
    Tab5 --> Adv1[System Diagnostics]
    Tab5 --> Adv2[Developer Tools]
    Tab5 --> Adv3[Experimental Features]
    Tab5 --> Adv4[Support & Logs]
    
    Adv1 --> Adv1a[Performance Monitor]
    Adv1 --> Adv1b[Memory Usage]
    Adv1 --> Adv1c[Battery Analysis]
    
    Adv2 --> Adv2a[Debug Console]
    Adv2 --> Adv2b[API Testing]
    Adv2 --> Adv2c[Log Viewer]
    
    %% Navigation Drawer (Secondary)
    MainApp --> NavDrawer[Navigation Drawer]
    NavDrawer --> Draw1[🏠 Home]
    NavDrawer --> Draw2[📋 Quick Settings]
    NavDrawer --> Draw3[🔔 Notifications]
    NavDrawer --> Draw4[❓ Help & Support]
    NavDrawer --> Draw5[ℹ️ About]
    
    %% Floating Action Button Context
    Tab1 --> FAB[Recording FAB]
    FAB --> FAB1[▶️ Start Recording]
    FAB --> FAB2[⏹️ Stop Recording]
    FAB --> FAB3[⏸️ Pause Recording]
    FAB --> FAB4[📸 Calibration Capture]
    
    %% Top App Bar Actions
    MainApp --> TopBar[Top App Bar]
    TopBar --> TopBar1[🔍 Search]
    TopBar --> TopBar2[🔔 Notifications]
    TopBar --> TopBar3[⋮ More Options]
    TopBar --> TopBar4[👤 Profile]
    
    %% Color Coding for User Flow Clarity
    style Tab1 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Tab2 fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    style Tab3 fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style Tab4 fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    style Tab5 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    
    style BottomNav fill:#ffffff,stroke:#333333,stroke-width:2px
    style NavDrawer fill:#f5f5f5,stroke:#666666,stroke-width:2px
    style FAB fill:#ff6b6b,stroke:#ffffff,stroke-width:2px
    style TopBar fill:#6200ea,stroke:#ffffff,stroke-width:2px
```

## Screen Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant M as MainActivity
    participant S as Settings
    participant F as FileManager
    participant Mon as Monitoring
    participant Rec as Recording Service
    
    U->>M: Launch App
    M->>M: Check Permissions
    M->>M: Initialize UI Components
    M->>U: Show Recording Interface
    
    U->>M: Tap Settings Tab
    M->>S: Navigate to Settings
    S->>U: Show Configuration Options
    
    U->>S: Configure Shimmer Device
    S->>M: Return with Config
    M->>M: Update Device Status
    
    U->>M: Tap Monitoring Tab
    M->>Mon: Show Live Dashboard
    Mon->>Mon: Start Data Visualization
    Mon->>U: Display Real-time Charts
    
    U->>M: Tap Recording FAB
    M->>Rec: Start Recording Service
    Rec->>M: Recording Status Update
    M->>U: Show Recording Indicators
    
    U->>M: Tap Files Tab
    M->>F: Show File Browser
    F->>F: Load Session Data
    F->>U: Display File List
    
    U->>F: Select Session
    F->>F: Show Session Details
    F->>U: Display File Actions
```

## Accessibility Navigation Flow

```mermaid
graph TD
    A[Screen Reader Navigation] --> B[Focus Management]
    
    B --> B1[Sequential Tab Order]
    B --> B2[Skip Links Available]
    B --> B3[Logical Heading Structure]
    B --> B4[Focus Indicators Visible]
    
    A --> C[Voice Commands]
    C --> C1["Say 'Start Recording'"]
    C --> C2["Say 'Open Settings'"]
    C --> C3["Say 'Show Files'"]
    C --> C4["Say 'Check Status'"]
    
    A --> D[Switch Control]
    D --> D1[Primary Action Highlighted]
    D --> D2[Secondary Actions Available]
    D --> D3[Navigation Controls]
    D --> D4[Exit Strategies]
    
    A --> E[Large Text Support]
    E --> E1[Dynamic Type Scaling]
    E --> E2[Layout Adapts to Text Size]
    E --> E3[Icons Remain Legible]
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#fce4ec
    style E fill:#f3e5f5
```

## Material Design 3 Component Mapping

```mermaid
graph LR
    subgraph "Current Components"
        CC1[Basic Buttons]
        CC2[LinearLayout Status]
        CC3[Options Menu]
        CC4[Simple TextViews]
        CC5[Basic RecyclerView]
    end
    
    subgraph "Material Design 3 Components"
        MD1[Filled/Outlined Buttons]
        MD2[Status Chips & Cards]
        MD3[Navigation Bar/Drawer]
        MD4[Typography Scale]
        MD5[Dynamic Lists]
    end
    
    CC1 --> MD1
    CC2 --> MD2
    CC3 --> MD3
    CC4 --> MD4
    CC5 --> MD5
    
    subgraph "New MD3 Additions"
        NEW1[Floating Action Button]
        NEW2[Top App Bar]
        NEW3[Progress Indicators]
        NEW4[Snackbars]
        NEW5[Dialog Variants]
    end
    
    style CC1 fill:#ffcdd2
    style CC2 fill:#ffcdd2
    style CC3 fill:#ffcdd2
    style CC4 fill:#ffcdd2
    style CC5 fill:#ffcdd2
    
    style MD1 fill:#c8e6c9
    style MD2 fill:#c8e6c9
    style MD3 fill:#c8e6c9
    style MD4 fill:#c8e6c9
    style MD5 fill:#c8e6c9
    
    style NEW1 fill:#e1f5fe
    style NEW2 fill:#e1f5fe
    style NEW3 fill:#e1f5fe
    style NEW4 fill:#e1f5fe
    style NEW5 fill:#e1f5fe
```