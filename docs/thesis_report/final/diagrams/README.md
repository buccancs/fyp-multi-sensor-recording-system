# Chapter 6 Figures and Diagrams

This directory contains Mermaid diagrams for Chapter 6 figures and Appendix diagnostic visualizations. The diagrams can be rendered to PNG format using Mermaid CLI or online tools.

## Essential Figures (Chapter 6)

### System Architecture (§6.1 Achievements)
- **F1_system_architecture.md** - Complete system overview with PC controller and Android nodes
- **F2_recording_pipeline.md** - Recording workflow from discovery to data consolidation  
- **F3_device_discovery.md** - Device discovery protocol and handshake sequence

### Synchronization Analysis (§6.2 Evaluation)
- **F4_sync_timeline.md** - Synchronized start trigger timeline with clock offsets

### Issue Documentation (§6.3 Limitations)
- **F14_issues_timeline.md** - Known issues timeline during recording sessions

## Diagnostic Figures (Appendix G)

### System Reliability
- **A1_discovery_pattern.md** - Device discovery success patterns and failure modes
- **A6_reliability_overview.md** - Comprehensive system reliability metrics and error classification

## Generated PNG Files

The following PNG files have been generated from the Mermaid diagrams for immediate use:

### Essential Figures (Chapter 6)
- **F1_system_architecture.png** - Complete system overview (1200x800px)
- **F2_recording_pipeline.png** - Recording workflow sequence (1200x900px)  
- **F3_device_discovery.png** - Device discovery protocol (1000x1200px)
- **F4_sync_timeline.png** - Synchronized start timeline (1200x600px)
- **F14_issues_timeline.png** - Known issues timeline (1200x800px)

### Diagnostic Figures (Appendix G)
- **A1_discovery_pattern.png** - Discovery success flowchart (1000x800px)
- **A6_reliability_pie_chart.png** - Error distribution (1200x1000px)
- **A6_reliability_flowchart.png** - Error classification (1200x1000px)

All PNG files are generated at publication quality with neutral theme, white background, and appropriate sizing for thesis inclusion.

## Rendering to PNG

### Using Mermaid CLI
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Render individual diagrams
mmdc -i F1_system_architecture.md -o F1_system_architecture.png -t neutral -b white --width 1200 --height 800

# Batch render all diagrams  
for file in *.md; do
    mmdc -i "$file" -o "${file%.md}.png" -t neutral -b white --width 1200 --height 800
done
```

### Using Online Tools
1. Copy diagram content from `.md` files
2. Paste into [Mermaid Live Editor](https://mermaid.live/)
3. Export as PNG (recommended: 1200x800px, 300 DPI)

### Using GitHub/GitLab Integration
The diagrams render automatically in GitHub/GitLab markdown preview.

## Diagram Specifications

### Publication Standards
- **Resolution**: 300 DPI for final thesis
- **Format**: PNG with transparent background
- **Size**: 1200x800px minimum for complex diagrams
- **Fonts**: Sans-serif, minimum 10pt equivalent
- **Colors**: High contrast, colorblind-friendly palette

### Mermaid Styling
```css
/* Applied styling classes */
.pcStyle { fill:#e1f5fe; stroke:#01579b; stroke-width:2px }
.androidStyle { fill:#f3e5f5; stroke:#4a148c; stroke-width:2px }
.sensorStyle { fill:#e8f5e8; stroke:#1b5e20; stroke-width:2px }
.successStyle { fill:#c8e6c9; stroke:#2e7d32; stroke-width:2px }
.failStyle { fill:#ffcdd2; stroke:#c62828; stroke-width:2px }
.processStyle { fill:#e1f5fe; stroke:#0277bd; stroke-width:2px }
```

## Figure Placement in Thesis

### Chapter 6 Sections
- **§6.1 Achievements**: F1, F2, F3 (system architecture and flow)
- **§6.2 Evaluation**: F4 (synchronization analysis)
- **§6.3 Limitations**: F14 (known issues timeline)

### Appendix G: Diagnostic Analysis
- **Device Discovery**: A1 (success patterns)
- **System Reliability**: A6 (error classification and metrics)

## Data Requirements for Performance Figures

The architectural diagrams (F1-F4, F14, A1, A6) are based on system design and observed behavior patterns. For quantitative performance figures (F5-F13), actual session data would be required:

### Required Data Sources
- **Sync logs**: Clock offset measurements, timing quality
- **Frame CSVs**: Video frame timestamps for FPS analysis  
- **GSR data**: Sensor sampling timestamps and values
- **Event logs**: System errors, UI freezes, connection issues
- **Transfer logs**: File transfer times and success rates

### Missing Quantitative Figures
The following figures require actual session data for implementation:
- **F5**: Clock offset time series
- **F6**: Sync jitter distribution  
- **F7**: Frame-rate stability plots
- **F8**: GSR sampling analysis
- **F9-F13**: Additional performance metrics

## Customization

### Modifying Diagrams
1. Edit the Mermaid syntax in `.md` files
2. Validate syntax using [Mermaid Live Editor](https://mermaid.live/)
3. Re-render to PNG format
4. Update figure references in thesis chapters

### Adding New Diagrams
1. Create new `.md` file with Mermaid content
2. Follow naming convention: `[F|A][number]_[description].md`
3. Apply consistent styling classes
4. Document in this README

## Notes

- Diagrams are designed for black/white printing compatibility
- All text uses accessible font sizes and contrast ratios
- Complex diagrams are split into multiple views for clarity
- Timeline diagrams include quantitative timing annotations
- Error classification follows academic severity standards