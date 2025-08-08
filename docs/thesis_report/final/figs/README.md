# Chapter 6 Figures Directory

This directory contains documentation and resources for the figures referenced in Chapter 6 and Appendices of the thesis. The architectural diagrams have been moved to Mermaid format for better maintainability and integration.

## Contents

- `README.md` - This documentation file
- `../diagrams/` - Mermaid diagrams for system architecture and flow diagrams

## Figure Organization

### Architectural Diagrams (Mermaid)
System architecture and flow diagrams are now implemented as Mermaid diagrams in the `../diagrams/` directory:

- **F1-F4**: System architecture, recording pipeline, device discovery, sync timeline
- **F14**: Known issues timeline  
- **A1, A6**: Diagnostic reliability analysis

### Performance Figures (Requires Session Data)
Quantitative performance figures require actual session data for implementation:

- **F5-F13**: Clock offset analysis, frame rates, GSR sampling, latency metrics

## Data Requirements for Performance Analysis

For implementing the quantitative performance figures (F5-F13), the following session data would be required:

### Sync Log Format (`pc_sync.log`)
```
[timestamp] t=1234.567, offset_ms=-2.3, q=0.95
[timestamp] t=1235.567, offset_ms=-1.8, q=0.94
```

### Frame CSV Format (`rgb_frames.csv`, `th_frames.csv`)
```
ts_ms,frame_id
1234567.89,1
1234601.23,2
```

### GSR CSV Format (`gsr.csv`)
```
Timestamp_ms,GSR_Value
1234567.89,12.34
1234575.89,12.45
```

### Events Log Format (`events.log`)
```
1234.567 UI_FREEZE
1245.123 DISC_FAIL
1256.789 RECONNECT
1267.456 HEARTBEAT_MISS
```

## Implementation Approach

### Mermaid Diagrams (Implemented)
System architecture and flow diagrams use Mermaid for:
- Version control friendly text format
- Easy maintenance and updates
- Automatic rendering in documentation
- High-quality PNG export capability

### Performance Analysis (Future Work)
Quantitative figures would require:
- Session data collection during pilot studies
- Statistical analysis toolkit (matplotlib/seaborn)
- Automated report generation from session logs

## Figure Specifications

### Current Implementation (Mermaid)
- **F1-F4, F14, A1, A6**: System architecture and diagnostic flow diagrams
- **Resolution**: Vector-based, scalable to any DPI
- **Format**: Markdown with Mermaid syntax, exportable to PNG/SVG
- **Styling**: Publication-ready with consistent color scheme

### Future Implementation (Performance Metrics)
- **F5-F13**: Quantitative analysis requiring session data
- **Resolution**: 300 DPI for publication
- **Format**: PNG for draft, PDF for final
- **Styling**: Matplotlib with consistent academic formatting

## Migration from Python Toolkit

The original Python plotting toolkit has been replaced with Mermaid diagrams for architectural visualizations. This provides:

- **Better maintainability**: Text-based diagrams in version control
- **No dependencies**: No need for Python/matplotlib for architectural diagrams  
- **Easier collaboration**: Diagrams can be edited directly in markdown
- **Professional quality**: Vector-based output suitable for publication

Performance analysis figures (F5-F13) would still require Python implementation when session data becomes available.