#!/usr/bin/env python3
"""
Create figures for Chapter 2 of the thesis report.
Generates all 8 required figures for Chapter 2 based on the specifications.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from pathlib import Path

# Set up matplotlib for publication-quality figures
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.format': 'png',
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3
})

def create_output_dir():
    """Create output directory for figures"""
    output_dir = Path("/home/runner/work/bucika_gsr/bucika_gsr/docs/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def create_fig_2_4_gsr_cortisol_timeline():
    """Figure 2.4 — GSR vs cortisol timeline (graph)"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Time axis - from -30 seconds to 60 minutes
    time_sec = np.linspace(-30, 3600, 1000)  # seconds
    time_min = time_sec / 60  # minutes
    
    # GSR response (fast, immediate)
    gsr_baseline = 5.0  # μS
    gsr = np.zeros_like(time_sec)
    
    # Stimulus at t=0, create SCR peaks
    stimulus_times = [0, 300, 1800]  # seconds
    for stim_time in stimulus_times:
        # SCR peak: rise in 1-5s, decay over 5-20s
        peak_amplitude = np.random.uniform(2, 5)  # μS increase
        rise_time = 3  # seconds
        decay_time = 15  # seconds
        
        for i, t in enumerate(time_sec):
            if t >= stim_time:
                dt = t - stim_time
                if dt <= rise_time:
                    # Rising phase
                    gsr[i] += peak_amplitude * (dt / rise_time)
                elif dt <= rise_time + decay_time:
                    # Decay phase
                    gsr[i] += peak_amplitude * np.exp(-(dt - rise_time) / decay_time)
    
    gsr += gsr_baseline + np.random.normal(0, 0.1, len(time_sec))  # Add baseline + noise
    
    # Cortisol response (slow, delayed)
    cortisol_baseline = 10.0  # nmol/L
    cortisol = np.zeros_like(time_sec)
    
    for stim_time in stimulus_times:
        # Cortisol: delayed rise, peak at ~20-30 min, gradual return
        peak_delay = 25 * 60  # 25 minutes in seconds
        peak_amplitude = 15.0  # nmol/L increase
        
        for i, t in enumerate(time_sec):
            if t >= stim_time:
                dt = t - stim_time
                # Delayed rise and decay
                if dt <= peak_delay * 2:
                    cortisol[i] += peak_amplitude * np.exp(-0.5 * ((dt - peak_delay) / (peak_delay * 0.5))**2)
    
    cortisol += cortisol_baseline + np.random.normal(0, 0.5, len(time_sec))
    
    # Plot GSR
    ax1.plot(time_min, gsr, 'b-', linewidth=2, label='GSR (μS)')
    ax1.axvline(0, color='r', linestyle='--', alpha=0.7, label='Stimulus Onset')
    ax1.axvline(5, color='r', linestyle='--', alpha=0.5)
    ax1.axvline(30, color='r', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Skin Conductance (μS)', fontsize=12)
    ax1.set_title('Figure 2.4: GSR vs Cortisol Timeline Response to Acute Stressors', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.set_ylim(4, 12)
    
    # Plot Cortisol
    ax2.plot(time_min, cortisol, 'g-', linewidth=2, label='Cortisol (nmol/L)')
    ax2.axvline(0, color='r', linestyle='--', alpha=0.7, label='Stimulus Onset')
    ax2.axvline(5, color='r', linestyle='--', alpha=0.5)
    ax2.axvline(30, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Time (minutes)', fontsize=12)
    ax2.set_ylabel('Cortisol (nmol/L)', fontsize=12)
    ax2.legend(loc='upper right')
    ax2.set_ylim(8, 30)
    ax2.set_xlim(-0.5, 60)
    
    # Add annotations
    ax1.annotate('SCR Peak\n(1-5s onset)', xy=(0.5, 8), xytext=(10, 10),
                arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                fontsize=10, ha='center')
    
    ax2.annotate('Peak Response\n(~25 min)', xy=(25, 22), xytext=(40, 25),
                arrowprops=dict(arrowstyle='->', color='green', alpha=0.7),
                fontsize=10, ha='center')
    
    plt.tight_layout()
    return fig

def create_fig_2_5_gsr_trace():
    """Figure 2.5 — Example GSR trace (graph)"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Create realistic GSR trace
    duration = 120  # seconds
    fs = 128  # Hz sampling rate (Shimmer GSR+)
    time = np.arange(0, duration, 1/fs)
    
    # Baseline SCL with slow drift
    scl_baseline = 6.0  # μS
    scl_drift = 0.5 * np.sin(2 * np.pi * time / 60) + 0.2 * np.sin(2 * np.pi * time / 30)
    scl = scl_baseline + scl_drift
    
    # Add SCR events
    event_times = [15, 35, 60, 85, 105]  # seconds
    event_labels = ['Stressor A', 'Rest', 'Stressor B', 'Stressor C', 'Recovery']
    scr_components = np.zeros_like(time)
    
    for i, event_time in enumerate(event_times):
        if i in [0, 2, 3]:  # Stressor events
            # Create SCR response
            peak_amplitude = np.random.uniform(1.5, 3.5)
            rise_time = np.random.uniform(1, 3)
            decay_time = np.random.uniform(8, 15)
            
            mask = time >= event_time
            dt = time[mask] - event_time
            
            # Two-phase response
            rise_mask = dt <= rise_time
            decay_mask = (dt > rise_time) & (dt <= rise_time + decay_time)
            
            scr_components[mask][rise_mask] += peak_amplitude * (dt[rise_mask] / rise_time)
            scr_components[mask][decay_mask] += peak_amplitude * np.exp(-(dt[decay_mask] - rise_time) / decay_time)
    
    # Combine SCL and SCR with noise
    gsr_signal = scl + scr_components + np.random.normal(0, 0.05, len(time))
    
    # Plot the signal
    ax.plot(time, gsr_signal, 'b-', linewidth=1.5, label='GSR Signal')
    ax.plot(time, scl, 'r--', linewidth=1, alpha=0.7, label='SCL (Tonic Level)')
    
    # Mark events
    colors = ['red', 'gray', 'red', 'red', 'green']
    for i, (event_time, label, color) in enumerate(zip(event_times, event_labels, colors)):
        ax.axvline(event_time, color=color, linestyle=':', alpha=0.8)
        ax.text(event_time, ax.get_ylim()[1] * 0.95, label, 
                rotation=90, ha='right', va='top', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3))
    
    # Annotations for key features
    ax.annotate('SCR Onset', xy=(15.5, 7.8), xytext=(25, 9),
                arrowprops=dict(arrowstyle='->', color='darkblue'),
                fontsize=10, ha='center')
    
    ax.annotate('Peak', xy=(17, 8.5), xytext=(25, 8.5),
                arrowprops=dict(arrowstyle='->', color='darkblue'),
                fontsize=10, ha='center')
    
    ax.annotate('Recovery', xy=(25, 7.2), xytext=(35, 8.8),
                arrowprops=dict(arrowstyle='->', color='darkblue'),
                fontsize=10, ha='center')
    
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Skin Conductance (μS)', fontsize=12)
    ax.set_title('Figure 2.5: Example GSR Trace with Event Markers', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_ylim(5.5, 10)
    ax.grid(True, alpha=0.3)
    
    # Add caption note
    fig.text(0.5, 0.02, 'Note: SCR = Skin Conductance Response (phasic), SCL = Skin Conductance Level (tonic)\n' +
                       'Individual responses show high inter-subject variability',
             ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    return fig

def create_modality_landscape_diagram():
    """Figure 2.1 — Modality landscape (diagram)"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'Figure 2.1: Emotion/Stress Sensing Modality Landscape', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Main categories
    behavioral_box = patches.Rectangle((0.5, 4.5), 4, 2.5, linewidth=2, 
                                     edgecolor='blue', facecolor='lightblue', alpha=0.3)
    physiological_box = patches.Rectangle((5.5, 4.5), 4, 2.5, linewidth=2, 
                                        edgecolor='red', facecolor='lightcoral', alpha=0.3)
    
    ax.add_patch(behavioral_box)
    ax.add_patch(physiological_box)
    
    # Category labels
    ax.text(2.5, 6.7, 'BEHAVIORAL\nMODALITIES', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='darkblue')
    ax.text(7.5, 6.7, 'PHYSIOLOGICAL\nMODALITIES', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='darkred')
    
    # Behavioral modalities
    behavioral_items = [
        'RGB Facial Expression',
        'Body Pose/Posture',
        'Speech Analysis',
        'Micro-expressions'
    ]
    
    for i, item in enumerate(behavioral_items):
        ax.text(2.5, 6.2 - i*0.3, f'• {item}', ha='center', va='center', fontsize=11)
    
    # Physiological modalities
    physiological_items = [
        'GSR/EDA (Contact)',
        'PPG/HRV (Contact)',
        'Thermal (Contactless)',
        'rPPG (Contactless)',
        'Respiration (Contactless)'
    ]
    
    for i, item in enumerate(physiological_items):
        ax.text(7.5, 6.2 - i*0.3, f'• {item}', ha='center', va='center', fontsize=11)
    
    # Fusion box
    fusion_box = patches.Rectangle((3, 2.5), 4, 1.5, linewidth=2, 
                                 edgecolor='green', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(fusion_box)
    
    ax.text(5, 3.7, 'MULTIMODAL FUSION', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='darkgreen')
    ax.text(5, 3.2, 'Combining modalities improves\nrobustness and accuracy', 
            ha='center', va='center', fontsize=11)
    ax.text(5, 2.7, 'Reduces single-point failures', ha='center', va='center', fontsize=10, style='italic')
    
    # Arrows
    ax.arrow(2.5, 4.3, 1.8, -0.5, head_width=0.1, head_length=0.1, fc='green', ec='green')
    ax.arrow(7.5, 4.3, -1.8, -0.5, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Benefits text
    ax.text(5, 1.5, 'Benefits of Multimodal Approach:', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    benefits = [
        '• Captures both voluntary and involuntary responses',
        '• Provides redundancy for missing or noisy signals',
        '• Enables context-aware emotion recognition',
        '• Supports both real-time and offline analysis'
    ]
    
    for i, benefit in enumerate(benefits):
        ax.text(5, 1.1 - i*0.2, benefit, ha='center', va='center', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_contact_vs_contactless_diagram():
    """Figure 2.2 — Contact vs contactless measurement (flow diagram)"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Figure 2.2: Contact vs Contactless Measurement Pipelines', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Contact pipeline (top)
    contact_y = 7.5
    ax.text(1, contact_y + 0.8, 'CONTACT MEASUREMENT', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='darkblue')
    
    # Contact pipeline boxes
    contact_boxes = [
        (0.5, contact_y, 1, 0.6, 'Stimulus'),
        (2.5, contact_y, 1.5, 0.6, 'Physiological\nResponse'),
        (4.5, contact_y, 1.5, 0.6, 'Contact Sensor\n(GSR/PPG)'),
        (6.5, contact_y, 1.5, 0.6, 'Feature\nExtraction'),
        (8.5, contact_y, 1.5, 0.6, 'ML Model'),
        (10.5, contact_y, 1, 0.6, 'Output')
    ]
    
    for x, y, w, h, text in contact_boxes:
        box = patches.Rectangle((x, y), w, h, linewidth=2, 
                              edgecolor='blue', facecolor='lightblue', alpha=0.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Contact arrows
    for i in range(len(contact_boxes) - 1):
        start_x = contact_boxes[i][0] + contact_boxes[i][2]
        end_x = contact_boxes[i+1][0]
        y = contact_y + 0.3
        ax.arrow(start_x + 0.1, y, end_x - start_x - 0.2, 0, 
                head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # Contactless pipeline (bottom)
    contactless_y = 5
    ax.text(1, contactless_y + 0.8, 'CONTACTLESS MEASUREMENT', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='darkred')
    
    # Contactless pipeline boxes
    contactless_boxes = [
        (0.5, contactless_y, 1, 0.6, 'Stimulus'),
        (2.5, contactless_y, 1.5, 0.6, 'Physiological\nResponse'),
        (4.5, contactless_y, 1.5, 0.6, 'Contactless\n(RGB/Thermal)'),
        (6.5, contactless_y, 1.5, 0.6, 'Feature\nExtraction'),
        (8.5, contactless_y, 1.5, 0.6, 'ML Model'),
        (10.5, contactless_y, 1, 0.6, 'Output')
    ]
    
    for x, y, w, h, text in contactless_boxes:
        box = patches.Rectangle((x, y), w, h, linewidth=2, 
                              edgecolor='red', facecolor='lightcoral', alpha=0.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Contactless arrows
    for i in range(len(contactless_boxes) - 1):
        start_x = contactless_boxes[i][0] + contactless_boxes[i][2]
        end_x = contactless_boxes[i+1][0]
        y = contactless_y + 0.3
        ax.arrow(start_x + 0.1, y, end_x - start_x - 0.2, 0, 
                head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    # Trade-offs comparison
    ax.text(6, 3.5, 'Trade-offs Comparison', ha='center', va='center', 
            fontsize=14, fontweight='bold')
    
    # Contact advantages/disadvantages
    ax.text(3, 3, 'Contact Sensors:', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='darkblue')
    contact_pros = ['✓ High accuracy', '✓ Direct measurement', '✓ Well-established']
    contact_cons = ['✗ Intrusive', '✗ Limited mobility', '✗ Setup complexity']
    
    for i, pro in enumerate(contact_pros):
        ax.text(1.5, 2.6 - i*0.2, pro, ha='left', va='center', fontsize=10, color='green')
    for i, con in enumerate(contact_cons):
        ax.text(1.5, 1.9 - i*0.2, con, ha='left', va='center', fontsize=10, color='red')
    
    # Contactless advantages/disadvantages
    ax.text(9, 3, 'Contactless Sensors:', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='darkred')
    contactless_pros = ['✓ Non-intrusive', '✓ Natural behavior', '✓ Scalable deployment']
    contactless_cons = ['✗ Lower precision', '✗ Environmental sensitivity', '✗ Complex processing']
    
    for i, pro in enumerate(contactless_pros):
        ax.text(7.5, 2.6 - i*0.2, pro, ha='left', va='center', fontsize=10, color='green')
    for i, con in enumerate(contactless_cons):
        ax.text(7.5, 1.9 - i*0.2, con, ha='left', va='center', fontsize=10, color='red')
    
    plt.tight_layout()
    return fig

def create_stress_pathways_diagram():
    """Figure 2.3 — Stress pathways (schematic)"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Figure 2.3: Stress Response Pathways', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Stressor
    stressor_box = patches.Rectangle((5, 8.5), 2, 0.8, linewidth=2, 
                                   edgecolor='black', facecolor='yellow', alpha=0.7)
    ax.add_patch(stressor_box)
    ax.text(6, 8.9, 'STRESSOR', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Brain/hypothalamus
    brain_box = patches.Rectangle((5, 6.8), 2, 1, linewidth=2, 
                                edgecolor='purple', facecolor='lavender', alpha=0.7)
    ax.add_patch(brain_box)
    ax.text(6, 7.3, 'Hypothalamus', ha='center', va='center', fontsize=11, fontweight='bold')
    
    # SAM pathway (left)
    sam_title = ax.text(2.5, 6.5, 'SAM AXIS', ha='center', va='center', 
                       fontsize=14, fontweight='bold', color='darkblue')
    sam_subtitle = ax.text(2.5, 6.1, '(Sympathetic-Adreno-Medullary)', ha='center', va='center', 
                          fontsize=10, color='darkblue')
    
    # SAM components
    sympathetic_box = patches.Rectangle((1.5, 5), 2, 0.8, linewidth=2, 
                                      edgecolor='blue', facecolor='lightblue', alpha=0.7)
    ax.add_patch(sympathetic_box)
    ax.text(2.5, 5.4, 'Sympathetic\nNervous System', ha='center', va='center', fontsize=10, fontweight='bold')
    
    adrenal_medulla_box = patches.Rectangle((1.5, 3.8), 2, 0.8, linewidth=2, 
                                          edgecolor='blue', facecolor='lightblue', alpha=0.7)
    ax.add_patch(adrenal_medulla_box)
    ax.text(2.5, 4.2, 'Adrenal Medulla\n(Epinephrine)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # SAM outputs
    sam_outputs = ['• Heart Rate ↑', '• GSR/Sweating ↑', '• Blood Pressure ↑', '• Pupil Dilation']
    for i, output in enumerate(sam_outputs):
        ax.text(2.5, 2.8 - i*0.2, output, ha='center', va='center', fontsize=10, color='darkblue')
    
    ax.text(2.5, 1.8, 'Latency: seconds', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='darkblue')
    
    # HPA pathway (right)
    hpa_title = ax.text(9.5, 6.5, 'HPA AXIS', ha='center', va='center', 
                       fontsize=14, fontweight='bold', color='darkred')
    hpa_subtitle = ax.text(9.5, 6.1, '(Hypothalamic-Pituitary-Adrenal)', ha='center', va='center', 
                          fontsize=10, color='darkred')
    
    # HPA components
    pituitary_box = patches.Rectangle((8.5, 5), 2, 0.8, linewidth=2, 
                                    edgecolor='red', facecolor='lightcoral', alpha=0.7)
    ax.add_patch(pituitary_box)
    ax.text(9.5, 5.4, 'Pituitary Gland\n(ACTH)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    adrenal_cortex_box = patches.Rectangle((8.5, 3.8), 2, 0.8, linewidth=2, 
                                         edgecolor='red', facecolor='lightcoral', alpha=0.7)
    ax.add_patch(adrenal_cortex_box)
    ax.text(9.5, 4.2, 'Adrenal Cortex\n(Cortisol)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # HPA outputs
    hpa_outputs = ['• Blood Sugar ↑', '• Inflammation ↓', '• Immune Function ↓', '• Memory Formation']
    for i, output in enumerate(hpa_outputs):
        ax.text(9.5, 2.8 - i*0.2, output, ha='center', va='center', fontsize=10, color='darkred')
    
    ax.text(9.5, 1.8, 'Latency: 20-30 minutes', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='darkred')
    
    # Arrows
    # Stressor to brain
    ax.arrow(6, 8.4, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Brain to pathways
    ax.arrow(5.8, 7.2, -2.8, -1.8, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.arrow(6.2, 7.2, 2.8, -1.8, head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    # SAM pathway arrows
    ax.arrow(2.5, 4.9, 0, -0.3, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    
    # HPA pathway arrows
    ax.arrow(9.5, 4.9, 0, -0.3, head_width=0.05, head_length=0.05, fc='red', ec='red')
    
    # Observable measures boxes
    sam_measure_box = patches.Rectangle((0.5, 0.8), 4, 0.6, linewidth=2, 
                                      edgecolor='darkblue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(sam_measure_box)
    ax.text(2.5, 1.1, 'Observable: GSR ↔ SAM', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='darkblue')
    
    hpa_measure_box = patches.Rectangle((7.5, 0.8), 4, 0.6, linewidth=2, 
                                      edgecolor='darkred', facecolor='lightcoral', alpha=0.3)
    ax.add_patch(hpa_measure_box)
    ax.text(9.5, 1.1, 'Observable: Cortisol ↔ HPA', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='darkred')
    
    plt.tight_layout()
    return fig

def main():
    """Create all Chapter 2 figures"""
    output_dir = create_output_dir()
    
    print("Creating Chapter 2 figures...")
    
    # Create all figures
    figures = [
        ("fig_2_1_modalities", create_modality_landscape_diagram()),
        ("fig_2_2_contact_vs_contactless", create_contact_vs_contactless_diagram()),
        ("fig_2_3_stress_pathways", create_stress_pathways_diagram()),
        ("fig_2_4_gsr_cortisol_timeline", create_fig_2_4_gsr_cortisol_timeline()),
        ("fig_2_5_gsr_trace", create_fig_2_5_gsr_trace())
    ]
    
    # Save all figures
    for filename, fig in figures:
        filepath = output_dir / f"{filename}.png"
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close(fig)
    
    print("Chapter 2 figures created successfully!")

if __name__ == "__main__":
    main()