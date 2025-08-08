# Figure Generation Toolkit for Chapter 6

This directory contains a minimal plotting toolkit for generating the figures referenced in Chapter 6 and Appendices of the thesis. The toolkit is designed to process session logs and data files to create publication-quality figures.

## Files

- `metrics.py` - Data loading utilities for parsing log files and CSV data
- `make_fig.py` - Figure generation functions using matplotlib
- `README.md` - This documentation file

## Requirements

```bash
pip install matplotlib pandas numpy
```

## Usage

### Basic Figure Generation

```python
from make_fig import f_clock_offset, f_jitter, f_fps, f_gsr_rate, f_events

# Generate individual figures
f_clock_offset("sessions/s1/pc_sync.log", "F5_clock_offset.png")
f_jitter("sessions/s1/pc_sync.log", "F6_sync_jitter.png") 
f_fps("sessions/s1/rgb_frames.csv", "sessions/s1/th_frames.csv", "F7_fps.png")
f_gsr_rate("sessions/s1/gsr.csv", "F8_gsr_rate.png")
f_events("sessions/s1/events.log", "F14_events.png")
```

### Batch Generation

```bash
python make_fig.py
```

This generates all essential figures (F5, F6, F7, F8, F14) from sample session data.

## Data Format Requirements

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

## Figure Specifications

### Essential Figures (Chapter 6)

- **F1-F4**: System architecture and flow diagrams (manual creation)
- **F5**: Clock offset over time (line plot)
- **F6**: Sync jitter distribution (histogram/CDF)
- **F7**: Frame-rate stability RGB & thermal (time series)
- **F8**: GSR sampling stability (time series + histogram)
- **F9-F12**: Additional performance metrics (extend make_fig.py)
- **F13**: Calibration pair overlay (manual/OpenCV)
- **F14**: Known issues timeline (event plot)

### Diagnostic Figures (Appendix)

- **A1-A12**: Extended diagnostic analysis (see appendices.md)

## Output Settings

- Resolution: 300 DPI
- Format: PNG for draft, PDF for final
- Font size: ≥10 pt
- Consistent styling across all figures

## Customization

To adapt for your specific log formats:

1. Modify regex patterns in `metrics.py` loading functions
2. Update field names to match your CSV headers  
3. Adjust plot styling in `make_fig.py` functions
4. Add new figure generation functions as needed

## Notes

- Use 300 DPI for publication quality
- Mark re-sync events and errors with vertical lines
- Compute statistics over steady-state windows (exclude first/last 5-10s)
- Keep visual style consistent across all figures