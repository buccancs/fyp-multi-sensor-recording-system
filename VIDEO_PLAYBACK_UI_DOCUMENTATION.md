
# Media & Stimuli Tab - New Video Playback Interface

## Layout Structure:

┌─────────────── Media & Stimuli Tab ───────────────┐
│                                                   │
│ ┌─── USB Camera Preview ──────────────────────┐   │
│ │ Real-time USB webcam preview for participant │   │
│ │ monitoring. Requires OpenCV and connected    │   │
│ │ USB camera.                                  │   │
│ │                                              │   │
│ │ Select Camera: [Camera 0 (640x480) ▼]       │   │
│ │ [Refresh] [Start Camera] [Stop Camera]      │   │
│ └──────────────────────────────────────────────┘   │
│                                                   │
│ ┌─── Video Playback for Emotion Elicitation ──┐   │
│ │ Play video files to elicit emotional        │   │
│ │ responses during experiments.                │   │
│ │ Supports: MP4, AVI, MOV, etc.               │   │
│ │                                              │   │
│ │ Video File: [No video selected]  [Browse...] │   │
│ │ [Play] [Pause] [Stop]                       │   │
│ │ Progress: [████████──────] 00:45 / 02:30    │   │
│ └──────────────────────────────────────────────┘   │
│                                                   │
│ ┌─── Media Display (640x480) ─────────────────┐   │
│ │                                              │   │
│ │         [Live Video/Camera Feed]             │   │
│ │         or                                   │   │
│ │         "No media active"                    │   │
│ │                                              │   │
│ └──────────────────────────────────────────────┘   │
│                                                   │
│ ┌─── Media Status ────────────────────────────┐   │
│ │ [10:45:23] Video: Video loaded: emotion.mp4  │   │
│ │ [10:45:24] Video: Video playback started     │   │
│ │ [10:45:30] Camera: Camera 0 preview started  │   │
│ └──────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘

## Key Features:

### Video Playback Controls:
• File browser with video format filtering
• Play/Pause/Stop controls with smart state management
• Progress slider with seeking capability
• Time display (current/total)
• Comprehensive error handling

### Camera Integration:
• USB camera detection and selection
• Live preview with real-time streaming
• Seamless switching between camera and video

### Research Workflow:
• Unified display for both camera monitoring and stimulus presentation
• Status logging for experiment tracking
• Session integration for synchronized recording
• Professional interface suitable for academic research

### Technical Implementation:
• OpenCV-based video playback with threading
• PyQt integration for smooth UI responsiveness
• Format support: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V, 3GP, OGV, MPG, MPEG
• Frame-accurate seeking and position tracking
• Automatic resource management and cleanup
