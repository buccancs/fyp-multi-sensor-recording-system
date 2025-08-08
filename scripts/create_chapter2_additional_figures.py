#!/usr/bin/env python3
"""
Create remaining figures for Chapter 2 - thermal cues, ML pipeline, and system architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
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
    'axes.grid': False
})

def create_output_dir():
    """Create output directory for figures"""
    output_dir = Path("/home/runner/work/bucika_gsr/bucika_gsr/docs/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def create_fig_2_6_thermal_facial_cues():
    """Figure 2.6 — Thermal facial cues (annotated image/diagram)"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Figure 2.6: Thermal Facial Cues for Stress Detection', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Draw face outline (simplified)
    face = patches.Circle((5, 6), 2.5, linewidth=3, edgecolor='black', facecolor='wheat', alpha=0.7)
    ax.add_patch(face)
    
    # Eyes
    left_eye = patches.Ellipse((4.2, 6.8), 0.4, 0.2, linewidth=2, edgecolor='black', facecolor='white')
    right_eye = patches.Ellipse((5.8, 6.8), 0.4, 0.2, linewidth=2, edgecolor='black', facecolor='white')
    ax.add_patch(left_eye)
    ax.add_patch(right_eye)
    
    # Nose
    nose = patches.Polygon([(5, 6.2), (4.9, 5.8), (5.1, 5.8)], closed=True, 
                          linewidth=2, edgecolor='black', facecolor='pink')
    ax.add_patch(nose)
    
    # Mouth
    mouth = patches.Arc((5, 5.2), 0.6, 0.3, angle=0, theta1=200, theta2=340,
                       linewidth=2, edgecolor='black')
    ax.add_patch(mouth)
    
    # Thermal regions with color coding
    
    # Nose tip region - cooling (blue)
    nose_region = patches.Circle((5, 5.7), 0.3, linewidth=3, 
                               edgecolor='blue', facecolor='lightblue', alpha=0.6)
    ax.add_patch(nose_region)
    
    # Periorbital/forehead regions - warming (red)
    left_periorbital = patches.Circle((4.2, 7.1), 0.4, linewidth=3, 
                                    edgecolor='red', facecolor='lightcoral', alpha=0.6)
    right_periorbital = patches.Circle((5.8, 7.1), 0.4, linewidth=3, 
                                     edgecolor='red', facecolor='lightcoral', alpha=0.6)
    forehead = patches.Ellipse((5, 7.8), 1.5, 0.6, linewidth=3, 
                             edgecolor='red', facecolor='lightcoral', alpha=0.6)
    
    ax.add_patch(left_periorbital)
    ax.add_patch(right_periorbital)
    ax.add_patch(forehead)
    
    # Nostril region for respiration
    left_nostril = patches.Circle((4.95, 5.9), 0.08, linewidth=2, 
                                edgecolor='orange', facecolor='yellow', alpha=0.8)
    right_nostril = patches.Circle((5.05, 5.9), 0.08, linewidth=2, 
                                 edgecolor='orange', facecolor='yellow', alpha=0.8)
    ax.add_patch(left_nostril)
    ax.add_patch(right_nostril)
    
    # Annotations with arrows
    
    # Nose cooling annotation
    ax.annotate('Nose Tip Cooling\n(0.1-0.5°C decrease)\nVasoconstriction', 
                xy=(5, 5.7), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                fontsize=11, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Forehead warming annotation
    ax.annotate('Forehead/Periorbital\nWarming\nIncreased blood flow', 
                xy=(5, 7.8), xytext=(7.5, 8.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=11, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8))
    
    # Respiration annotation
    ax.annotate('Respiration\nHeat Plume\n(Periodic)', 
                xy=(5, 5.9), xytext=(7.5, 5.5),
                arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                fontsize=11, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
    
    # Temperature scale bar
    scale_x, scale_y = 1, 2.5
    scale_height = 2
    scale_width = 0.3
    
    # Create temperature gradient
    gradient = np.linspace(0, 1, 100).reshape(-1, 1)
    extent = [scale_x, scale_x + scale_width, scale_y, scale_y + scale_height]
    ax.imshow(gradient, aspect='auto', cmap='coolwarm', extent=extent)
    
    # Scale labels
    ax.text(scale_x + scale_width + 0.1, scale_y + scale_height, '37°C', 
            va='center', fontsize=10, fontweight='bold')
    ax.text(scale_x + scale_width + 0.1, scale_y + scale_height/2, '35°C', 
            va='center', fontsize=10, fontweight='bold')
    ax.text(scale_x + scale_width + 0.1, scale_y, '33°C', 
            va='center', fontsize=10, fontweight='bold')
    
    ax.text(scale_x + scale_width/2, scale_y - 0.3, 'Temperature (°C)', 
            ha='center', fontsize=11, fontweight='bold')
    
    # Legend
    legend_y = 3.5
    ax.text(5, legend_y + 0.5, 'Stress Response Patterns:', 
            ha='center', va='center', fontsize=13, fontweight='bold')
    
    # Legend items
    cooling_legend = patches.Circle((3.5, legend_y), 0.2, linewidth=2, 
                                  edgecolor='blue', facecolor='lightblue', alpha=0.8)
    ax.add_patch(cooling_legend)
    ax.text(3.9, legend_y, 'Cooling regions (vasoconstriction)', 
            va='center', fontsize=11)
    
    warming_legend = patches.Circle((3.5, legend_y - 0.4), 0.2, linewidth=2, 
                                  edgecolor='red', facecolor='lightcoral', alpha=0.8)
    ax.add_patch(warming_legend)
    ax.text(3.9, legend_y - 0.4, 'Warming regions (increased blood flow)', 
            va='center', fontsize=11)
    
    respiration_legend = patches.Circle((3.5, legend_y - 0.8), 0.2, linewidth=2, 
                                      edgecolor='orange', facecolor='yellow', alpha=0.8)
    ax.add_patch(respiration_legend)
    ax.text(3.9, legend_y - 0.8, 'Respiration monitoring', 
            va='center', fontsize=11)
    
    # Note
    ax.text(5, 1, 'Note: Thermal changes are subtle (±0.1-0.5°C) but detectable\nwith high-sensitivity thermal cameras',
            ha='center', va='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.5))
    
    plt.tight_layout()
    return fig

def create_fig_2_7_ml_pipeline():
    """Figure 2.7 — ML pipeline for contactless GSR prediction (block diagram)"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Figure 2.7: Machine Learning Pipeline for Contactless GSR Prediction', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Input sources
    rgb_box = patches.Rectangle((1, 9), 2.5, 1.5, linewidth=2, 
                              edgecolor='green', facecolor='lightgreen', alpha=0.7)
    ax.add_patch(rgb_box)
    ax.text(2.25, 9.75, 'RGB Camera\nInput', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    thermal_box = patches.Rectangle((1, 7), 2.5, 1.5, linewidth=2, 
                                  edgecolor='red', facecolor='lightcoral', alpha=0.7)
    ax.add_patch(thermal_box)
    ax.text(2.25, 7.75, 'Thermal Camera\nInput', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    # RGB processing branch
    rgb_features_box = patches.Rectangle((5, 9), 2.5, 1.5, linewidth=2, 
                                       edgecolor='green', facecolor='lightgreen', alpha=0.5)
    ax.add_patch(rgb_features_box)
    ax.text(6.25, 9.75, 'RGB Features:\n• Facial Actions\n• rPPG/HRV\n• Micro-expressions', 
            ha='center', va='center', fontsize=10)
    
    # Thermal processing branch
    thermal_features_box = patches.Rectangle((5, 7), 2.5, 1.5, linewidth=2, 
                                           edgecolor='red', facecolor='lightcoral', alpha=0.5)
    ax.add_patch(thermal_features_box)
    ax.text(6.25, 7.75, 'Thermal Features:\n• Region Temps\n• Temperature ΔS\n• Respiration Rate', 
            ha='center', va='center', fontsize=10)
    
    # Feature fusion
    fusion_box = patches.Rectangle((9, 8), 3, 1.5, linewidth=3, 
                                 edgecolor='purple', facecolor='plum', alpha=0.7)
    ax.add_patch(fusion_box)
    ax.text(10.5, 8.75, 'Multimodal\nFeature Fusion', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    # ML model
    model_box = patches.Rectangle((13, 8), 2.5, 1.5, linewidth=2, 
                                edgecolor='blue', facecolor='lightblue', alpha=0.7)
    ax.add_patch(model_box)
    ax.text(14.25, 8.75, 'ML Model\n(Deep Learning)', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    # Outputs
    continuous_box = patches.Rectangle((9, 5.5), 3, 1, linewidth=2, 
                                     edgecolor='orange', facecolor='lightyellow', alpha=0.7)
    ax.add_patch(continuous_box)
    ax.text(10.5, 6, 'Continuous GSR\nPrediction (μS)', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    classification_box = patches.Rectangle((13, 5.5), 2.5, 1, linewidth=2, 
                                         edgecolor='orange', facecolor='lightyellow', alpha=0.7)
    ax.add_patch(classification_box)
    ax.text(14.25, 6, 'Stress Level\nClassification', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    # Training data (ground truth)
    training_box = patches.Rectangle((5, 4.5), 2.5, 1.5, linewidth=2, 
                                   edgecolor='darkgreen', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(training_box)
    ax.text(6.25, 5.25, 'Training Phase:\nGSR Ground Truth\n(Contact Sensor)', 
            ha='center', va='center', fontsize=10, fontweight='bold', style='italic')
    
    inference_box = patches.Rectangle((9, 3.5), 6.5, 0.8, linewidth=2, 
                                    edgecolor='darkblue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(inference_box)
    ax.text(12.25, 3.9, 'Inference Phase: Contactless Prediction (No GSR sensor required)', 
            ha='center', va='center', fontsize=11, fontweight='bold', style='italic')
    
    # Arrows
    # RGB to features
    ax.arrow(3.6, 9.75, 1.2, 0, head_width=0.15, head_length=0.15, fc='green', ec='green')
    
    # Thermal to features
    ax.arrow(3.6, 7.75, 1.2, 0, head_width=0.15, head_length=0.15, fc='red', ec='red')
    
    # Features to fusion
    ax.arrow(7.6, 9.5, 1.2, -0.5, head_width=0.15, head_length=0.15, fc='purple', ec='purple')
    ax.arrow(7.6, 8, 1.2, 0.5, head_width=0.15, head_length=0.15, fc='purple', ec='purple')
    
    # Fusion to model
    ax.arrow(12.1, 8.75, 0.7, 0, head_width=0.15, head_length=0.15, fc='blue', ec='blue')
    
    # Model to outputs
    ax.arrow(14.25, 7.9, 0, -1.2, head_width=0.15, head_length=0.15, fc='orange', ec='orange')
    ax.arrow(14.25, 7.9, -3, -1.2, head_width=0.15, head_length=0.15, fc='orange', ec='orange')
    
    # Training arrow
    ax.arrow(6.25, 4.4, 3.5, 3.8, head_width=0.15, head_length=0.15, fc='darkgreen', ec='darkgreen', 
             linestyle='--', alpha=0.7)
    
    # Processing details boxes
    processing_details = [
        (5, 10.8, 'Preprocessing:\n• Face detection\n• ROI extraction\n• Temporal alignment'),
        (9, 10.8, 'Synchronization:\n• Frame-level sync\n• Timestamp alignment\n• Data validation'),
        (13, 10.8, 'Post-processing:\n• Smoothing\n• Artifact removal\n• Calibration')
    ]
    
    for x, y, text in processing_details:
        detail_box = patches.Rectangle((x, y), 2.5, 0.8, linewidth=1, 
                                     edgecolor='gray', facecolor='lightgray', alpha=0.5)
        ax.add_patch(detail_box)
        ax.text(x + 1.25, y + 0.4, text, ha='center', va='center', fontsize=9)
    
    # Performance metrics box
    metrics_box = patches.Rectangle((1, 2), 14, 1, linewidth=2, 
                                  edgecolor='black', facecolor='lightyellow', alpha=0.5)
    ax.add_patch(metrics_box)
    ax.text(8, 2.5, 'Performance Metrics: RMSE, MAE, Correlation with Ground Truth GSR, Classification Accuracy', 
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_fig_2_8_system_architecture():
    """Figure 2.8 — System architecture and synchronisation (system diagram)"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Figure 2.8: System Architecture and Synchronization', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Shimmer sensor
    shimmer_box = patches.Rectangle((1, 8.5), 3, 2, linewidth=3, 
                                  edgecolor='blue', facecolor='lightblue', alpha=0.7)
    ax.add_patch(shimmer_box)
    ax.text(2.5, 9.5, 'Shimmer3 GSR+\n• EDA (128 Hz)\n• PPG (128 Hz)\n• IMU (128 Hz)', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Android device
    android_box = patches.Rectangle((1, 5.5), 3, 2.5, linewidth=3, 
                                  edgecolor='green', facecolor='lightgreen', alpha=0.7)
    ax.add_patch(android_box)
    ax.text(2.5, 6.75, 'Android Device\n• Topdon Thermal (25 Hz)\n• RGB Camera (30 Hz)\n• Local Storage', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Connectivity
    bluetooth_arrow = patches.FancyArrowPatch((2.5, 8.4), (2.5, 8.1),
                                            connectionstyle="arc3", 
                                            arrowstyle='->', mutation_scale=20,
                                            color='blue', linewidth=2)
    ax.add_patch(bluetooth_arrow)
    ax.text(3.2, 8.25, 'Bluetooth', ha='left', va='center', fontsize=10, color='blue')
    
    usb_line = patches.Rectangle((1.8, 5.3), 1.4, 0.1, linewidth=0, 
                               facecolor='orange', alpha=0.8)
    ax.add_patch(usb_line)
    ax.text(2.5, 5.1, 'USB-C', ha='center', va='center', fontsize=10, color='orange')
    
    # PC Coordinator
    pc_box = patches.Rectangle((7, 6), 4.5, 4, linewidth=3, 
                             edgecolor='purple', facecolor='plum', alpha=0.7)
    ax.add_patch(pc_box)
    ax.text(9.25, 8.5, 'PC Coordinator\n(Master Clock)', ha='center', va='center', 
            fontsize=13, fontweight='bold')
    
    pc_functions = [
        '• NTP Synchronization',
        '• LSL Stream Management',
        '• Data Fusion & Storage',
        '• Real-time Monitoring',
        '• Model Interface'
    ]
    
    for i, func in enumerate(pc_functions):
        ax.text(9.25, 8 - i*0.3, func, ha='center', va='center', fontsize=10)
    
    # Communication arrows
    # Shimmer to PC
    shimmer_to_pc = patches.FancyArrowPatch((4.1, 9.5), (6.9, 8.5),
                                          connectionstyle="arc3,rad=0.3", 
                                          arrowstyle='<->', mutation_scale=20,
                                          color='blue', linewidth=2)
    ax.add_patch(shimmer_to_pc)
    ax.text(5.5, 9.2, 'Bluetooth\nData Stream', ha='center', va='center', 
            fontsize=10, color='blue')
    
    # Android to PC
    android_to_pc = patches.FancyArrowPatch((4.1, 6.75), (6.9, 7.5),
                                          connectionstyle="arc3,rad=-0.3", 
                                          arrowstyle='<->', mutation_scale=20,
                                          color='green', linewidth=2)
    ax.add_patch(android_to_pc)
    ax.text(5.5, 6.8, 'WebSocket\nVideo/Thermal', ha='center', va='center', 
            fontsize=10, color='green')
    
    # Synchronization details
    sync_box = patches.Rectangle((12.5, 7.5), 3, 2, linewidth=2, 
                               edgecolor='red', facecolor='lightcoral', alpha=0.7)
    ax.add_patch(sync_box)
    ax.text(14, 8.5, 'Synchronization\n• <1ms precision\n• Common timestamps\n• Frame alignment', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Sampling rates
    rates_box = patches.Rectangle((12.5, 5), 3, 2, linewidth=2, 
                                edgecolor='orange', facecolor='lightyellow', alpha=0.7)
    ax.add_patch(rates_box)
    ax.text(14, 6, 'Sampling Rates\n• EDA: 128 Hz\n• Thermal: 25 Hz\n• RGB: 30 Hz', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Data flow
    ax.text(8, 4.5, 'Data Flow and Storage', ha='center', va='center', 
            fontsize=14, fontweight='bold')
    
    # Storage components
    storage_components = [
        (2, 3.5, 'Local\nAndroid\nStorage'),
        (6, 3.5, 'PC\nBuffer\n& Cache'),
        (10, 3.5, 'Synchronized\nDataset\nGeneration'),
        (14, 3.5, 'Export\nFormats\n(CSV/HDF5)')
    ]
    
    for x, y, text in storage_components:
        storage_box = patches.Rectangle((x-0.7, y-0.7), 1.4, 1.4, linewidth=2, 
                                      edgecolor='gray', facecolor='lightgray', alpha=0.7)
        ax.add_patch(storage_box)
        ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Storage flow arrows
    for i in range(len(storage_components) - 1):
        start_x = storage_components[i][0] + 0.7
        end_x = storage_components[i+1][0] - 0.7
        y = 3.5
        ax.arrow(start_x + 0.1, y, end_x - start_x - 0.2, 0, 
                head_width=0.1, head_length=0.2, fc='gray', ec='gray')
    
    # Quality indicators
    quality_box = patches.Rectangle((1, 1.5), 14, 1, linewidth=2, 
                                  edgecolor='darkgreen', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(quality_box)
    ax.text(8, 2, 'Quality Assurance: Timestamp validation, Data integrity checks, Missing sample detection, Cross-device synchronization verification', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Network topology note
    ax.text(8, 0.5, 'Network Topology: Star-mesh with PC as central coordinator\nAll devices maintain independent clocks synchronized via NTP', 
            ha='center', va='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """Create remaining Chapter 2 figures"""
    output_dir = create_output_dir()
    
    print("Creating remaining Chapter 2 figures...")
    
    # Create remaining figures
    figures = [
        ("fig_2_6_thermal_facial_cues", create_fig_2_6_thermal_facial_cues()),
        ("fig_2_7_ml_pipeline", create_fig_2_7_ml_pipeline()),
        ("fig_2_8_system_architecture", create_fig_2_8_system_architecture())
    ]
    
    # Save all figures
    for filename, fig in figures:
        filepath = output_dir / f"{filename}.png"
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close(fig)
    
    print("Remaining Chapter 2 figures created successfully!")

if __name__ == "__main__":
    main()