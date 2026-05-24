# -*- coding: utf-8 -*-
"""
Stage 5 Quality Check Script
-----------------------------
Visually inspect and validate the new predictions from ALOS DEM.
Generates comparison plots and quality metrics.

Usage:
    python scripts/quality_check_stage5.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure UTF-8 encoding for print statements
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import pandas as pd
import seaborn as sns
from path_config import DEM, SLOPE, RASTERS_DIR, TABLES_DIR, PREDICTIONS_DIR, FIGURES_DIR

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Output directory
OUT_DIR = str(FIGURES_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 80)
print("STAGE 5 QUALITY CHECK: ALOS DEM (12.5m) Analysis")
print("=" * 80)

# =============================================================================
# 1. DEM Comparison
# =============================================================================
print("\n[1/6] Comparing DEMs...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Old DEM (if backup exists)
old_dem_path = "backups/stage4_copernicus_20251025/dem_lucknow.tif"
new_dem_path = str(DEM)

if os.path.exists(old_dem_path):
    with rasterio.open(old_dem_path) as src:
        old_dem = src.read(1, masked=True)
        old_meta = src.meta
        show(old_dem, ax=axes[0], cmap='terrain', title='Old DEM (Copernicus 30m)')
        axes[0].set_title(f'Old DEM (Copernicus 30m)\nShape: {old_dem.shape}', fontsize=12, fontweight='bold')
else:
    axes[0].text(0.5, 0.5, 'Old DEM backup not found', ha='center', va='center', fontsize=14)
    axes[0].set_title('Old DEM (Not Available)', fontsize=12)

with rasterio.open(new_dem_path) as src:
    new_dem = src.read(1, masked=True)
    new_meta = src.meta
    show(new_dem, ax=axes[1], cmap='terrain', title='New DEM (ALOS 12.5m)')
    axes[1].set_title(f'New DEM (ALOS PALSAR 12.5m)\nShape: {new_dem.shape}', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '01_dem_comparison.png'), dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/01_dem_comparison.png")
plt.close()

# Statistics (using nanmin, nanmax, nanmean to handle NaN values)
print("\n  DEM Statistics:")
print(f"    New DEM - Min: {np.nanmin(new_dem):.2f}m, Max: {np.nanmax(new_dem):.2f}m, Mean: {np.nanmean(new_dem):.2f}m")
if os.path.exists(old_dem_path):
    print(f"    Old DEM - Min: {np.nanmin(old_dem):.2f}m, Max: {np.nanmax(old_dem):.2f}m, Mean: {np.nanmean(old_dem):.2f}m")

# =============================================================================
# 2. Slope Comparison
# =============================================================================
print("\n[2/6] Comparing Slope calculations...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

old_slope_path = "backups/stage4_copernicus_20251025/slope_lucknow.tif"
new_slope_path = str(SLOPE)

if os.path.exists(old_slope_path):
    with rasterio.open(old_slope_path) as src:
        old_slope = src.read(1, masked=True)
        show(old_slope, ax=axes[0], cmap='YlOrRd', title='Old Slope (from 30m DEM)')
        axes[0].set_title('Old Slope (from 30m DEM)', fontsize=12, fontweight='bold')
else:
    axes[0].text(0.5, 0.5, 'Old slope backup not found', ha='center', va='center', fontsize=14)
    axes[0].set_title('Old Slope (Not Available)', fontsize=12)

with rasterio.open(new_slope_path) as src:
    new_slope = src.read(1, masked=True)
    show(new_slope, ax=axes[1], cmap='YlOrRd', title='New Slope (from 12.5m DEM)')
    axes[1].set_title('New Slope (from 12.5m DEM)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '02_slope_comparison.png'), dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/02_slope_comparison.png")
plt.close()

print("\n  Slope Statistics:")
print(f"    New Slope - Min: {np.nanmin(new_slope):.2f}°, Max: {np.nanmax(new_slope):.2f}°, Mean: {np.nanmean(new_slope):.2f}°")
if os.path.exists(old_slope_path):
    print(f"    Old Slope - Min: {np.nanmin(old_slope):.2f}°, Max: {np.nanmax(old_slope):.2f}°, Mean: {np.nanmean(old_slope):.2f}°")

# =============================================================================
# 3. Drainage Features Comparison
# =============================================================================
print("\n[3/6] Comparing Drainage features...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Flow accumulation
old_flow_path = "backups/stage4_copernicus_20251025/stage3/flow_acc_lucknow.tif"
new_flow_path = os.path.join(str(RASTERS_DIR), "flow_acc_lucknow.tif")

if os.path.exists(old_flow_path):
    with rasterio.open(old_flow_path) as src:
        old_flow = src.read(1, masked=True)
        show(np.log10(old_flow + 1), ax=axes[0, 0], cmap='Blues', title='Old Flow Accumulation (log10)')
        axes[0, 0].set_title('Old Flow Accumulation\n(from 30m DEM, log scale)', fontsize=10, fontweight='bold')
else:
    axes[0, 0].text(0.5, 0.5, 'Old flow acc not found', ha='center', va='center', fontsize=12)
    axes[0, 0].set_title('Old Flow Acc (Not Available)', fontsize=10)

with rasterio.open(new_flow_path) as src:
    new_flow = src.read(1, masked=True)
    show(np.log10(new_flow + 1), ax=axes[0, 1], cmap='Blues', title='New Flow Accumulation (log10)')
    axes[0, 1].set_title('New Flow Accumulation\n(from 12.5m DEM, log scale)', fontsize=10, fontweight='bold')

# Drainage density
old_dd_path = "backups/stage4_copernicus_20251025/stage3/drainage_density_lucknow.tif"
new_dd_path = os.path.join(str(RASTERS_DIR), "drainage_density_lucknow.tif")

if os.path.exists(old_dd_path):
    with rasterio.open(old_dd_path) as src:
        old_dd = src.read(1, masked=True)
        show(old_dd, ax=axes[1, 0], cmap='viridis', title='Old Drainage Density')
        axes[1, 0].set_title('Old Drainage Density\n(from 30m DEM)', fontsize=10, fontweight='bold')
else:
    axes[1, 0].text(0.5, 0.5, 'Old drainage density not found', ha='center', va='center', fontsize=12)
    axes[1, 0].set_title('Old Drainage Density (Not Available)', fontsize=10)

with rasterio.open(new_dd_path) as src:
    new_dd = src.read(1, masked=True)
    show(new_dd, ax=axes[1, 1], cmap='viridis', title='New Drainage Density')
    axes[1, 1].set_title('New Drainage Density\n(from 12.5m DEM)', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '03_drainage_comparison.png'), dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/03_drainage_comparison.png")
plt.close()

# =============================================================================
# 4. ML Predictions Comparison
# =============================================================================
print("\n[4/6] Comparing ML Predictions...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

old_pred_path = "backups/stage4_copernicus_20251025/stage4/predicted_grp_class.tif"
new_pred_path = os.path.join(str(PREDICTIONS_DIR), "predicted_grp_class.tif")

# Class names and colors
class_names = {0: 'Poor', 1: 'Moderate', 2: 'High'}
class_colors = ['#d73027', '#fee08b', '#1a9850']  # Red, Yellow, Green

if os.path.exists(old_pred_path):
    with rasterio.open(old_pred_path) as src:
        old_pred = src.read(1, masked=True)
        im0 = axes[0].imshow(old_pred, cmap='RdYlGn', vmin=0, vmax=2)
        axes[0].set_title('Old ML Predictions\n(from 30m DEM features)', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # Add class distribution
        unique, counts = np.unique(old_pred.compressed(), return_counts=True)
        total = counts.sum()
        dist_text = "\n".join([f"{class_names.get(int(u), 'Unknown')}: {c/total*100:.1f}%" 
                               for u, c in zip(unique, counts)])
        axes[0].text(0.02, 0.98, dist_text, transform=axes[0].transAxes, 
                    fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
else:
    axes[0].text(0.5, 0.5, 'Old predictions not found', ha='center', va='center', fontsize=14)
    axes[0].set_title('Old ML Predictions (Not Available)', fontsize=12)

with rasterio.open(new_pred_path) as src:
    new_pred = src.read(1, masked=True)
    im1 = axes[1].imshow(new_pred, cmap='RdYlGn', vmin=0, vmax=2)
    axes[1].set_title('New ML Predictions\n(from 12.5m DEM features)', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    
    # Add class distribution
    unique, counts = np.unique(new_pred.compressed(), return_counts=True)
    total = counts.sum()
    dist_text = "\n".join([f"{class_names.get(int(u), 'Unknown')}: {c/total*100:.1f}%" 
                           for u, c in zip(unique, counts)])
    axes[1].text(0.02, 0.98, dist_text, transform=axes[1].transAxes, 
                fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Add colorbar
cbar = plt.colorbar(im1, ax=axes, orientation='horizontal', fraction=0.05, pad=0.05)
cbar.set_ticks([0, 1, 2])
cbar.set_ticklabels(['Poor (0)', 'Moderate (1)', 'High (2)'])
cbar.set_label('Groundwater Potential Zone', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, '04_predictions_comparison.png'), dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/04_predictions_comparison.png")
plt.close()

# =============================================================================
# 5. Model Performance Metrics
# =============================================================================
print("\n[5/6] Comparing Model Performance...")

old_cv_path = "backups/stage4_copernicus_20251025/stage4/cv_results.csv"
new_cv_path = os.path.join(str(TABLES_DIR), "cv_results.csv")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

if os.path.exists(old_cv_path) and os.path.exists(new_cv_path):
    old_cv = pd.read_csv(old_cv_path)
    new_cv = pd.read_csv(new_cv_path)
    
    # Accuracy comparison
    x = np.arange(len(old_cv))
    width = 0.35
    
    axes[0].bar(x - width/2, old_cv['accuracy'] * 100, width, label='Old (30m)', alpha=0.8, color='steelblue')
    axes[0].bar(x + width/2, new_cv['accuracy'] * 100, width, label='New (12.5m)', alpha=0.8, color='coral')
    axes[0].set_xlabel('Fold', fontsize=11)
    axes[0].set_ylabel('Accuracy (%)', fontsize=11)
    axes[0].set_title('Cross-Validation Accuracy Comparison', fontsize=12, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f'Fold {i+1}' for i in range(len(old_cv))])
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].axhline(y=old_cv['accuracy'].mean() * 100, color='steelblue', linestyle='--', alpha=0.5, label=f'Old Mean: {old_cv["accuracy"].mean()*100:.1f}%')
    axes[0].axhline(y=new_cv['accuracy'].mean() * 100, color='coral', linestyle='--', alpha=0.5, label=f'New Mean: {new_cv["accuracy"].mean()*100:.1f}%')
    
    # Balanced accuracy comparison
    axes[1].bar(x - width/2, old_cv['balanced_accuracy'] * 100, width, label='Old (30m)', alpha=0.8, color='steelblue')
    axes[1].bar(x + width/2, new_cv['balanced_accuracy'] * 100, width, label='New (12.5m)', alpha=0.8, color='coral')
    axes[1].set_xlabel('Fold', fontsize=11)
    axes[1].set_ylabel('Balanced Accuracy (%)', fontsize=11)
    axes[1].set_title('Balanced Accuracy Comparison', fontsize=12, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f'Fold {i+1}' for i in range(len(old_cv))])
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '05_performance_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUT_DIR}/05_performance_comparison.png")
    plt.close()
    
    # Print summary
    print("\n  Performance Summary:")
    print(f"    Old Model (30m) - Mean Accuracy: {old_cv['accuracy'].mean()*100:.2f}%, Balanced: {old_cv['balanced_accuracy'].mean()*100:.2f}%")
    print(f"    New Model (12.5m) - Mean Accuracy: {new_cv['accuracy'].mean()*100:.2f}%, Balanced: {new_cv['balanced_accuracy'].mean()*100:.2f}%")
    print(f"    Improvement: +{(new_cv['accuracy'].mean() - old_cv['accuracy'].mean())*100:.2f}% accuracy")
else:
    print("  ⚠ CV results not found for comparison")

# =============================================================================
# 6. Feature Importance
# =============================================================================
print("\n[6/6] Analyzing Feature Importance...")

feat_imp_path = os.path.join(str(TABLES_DIR), "feature_importances.csv")

if os.path.exists(feat_imp_path):
    feat_imp = pd.read_csv(feat_imp_path)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort by importance
    feat_imp_sorted = feat_imp.sort_values('importance', ascending=True)
    
    # Plot
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(feat_imp_sorted)))
    bars = ax.barh(feat_imp_sorted['feature'], feat_imp_sorted['importance'], color=colors)
    
    ax.set_xlabel('Importance', fontsize=11)
    ax.set_ylabel('Feature', fontsize=11)
    ax.set_title('Feature Importance (New Model with ALOS DEM)', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.3f}', 
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '06_feature_importance.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUT_DIR}/06_feature_importance.png")
    plt.close()
    
    print("\n  Feature Importance Rankings:")
    for idx, row in feat_imp_sorted.iloc[::-1].iterrows():
        print(f"    {row['feature']:20s}: {row['importance']:.4f}")
else:
    print("  ⚠ Feature importance file not found")

# =============================================================================
# Summary Report
# =============================================================================
print("\n" + "=" * 80)
print("QUALITY CHECK SUMMARY")
print("=" * 80)

summary = {
    'DEM Resolution': '12.5m (ALOS PALSAR)',
    'Grid Size': f'{new_dem.shape[0]} × {new_dem.shape[1]} pixels',
    'Total Pixels': f'{new_dem.shape[0] * new_dem.shape[1]:,}',
    'Valid Pixels': f'{np.sum(~new_pred.mask):,}',
    'Coverage': f'{np.sum(~new_pred.mask) / (new_pred.shape[0] * new_pred.shape[1]) * 100:.1f}%',
}

if os.path.exists(new_cv_path):
    new_cv = pd.read_csv(new_cv_path)
    summary['Mean CV Accuracy'] = f"{new_cv['accuracy'].mean()*100:.2f}%"
    summary['Mean Balanced Accuracy'] = f"{new_cv['balanced_accuracy'].mean()*100:.2f}%"

print("\nNew Model Specifications:")
for key, value in summary.items():
    print(f"  {key:25s}: {value}")

# Class distribution
unique, counts = np.unique(new_pred.compressed(), return_counts=True)
total = counts.sum()
print("\nGroundwater Potential Zone Distribution:")
for u, c in zip(unique, counts):
    class_name = class_names.get(int(u), 'Unknown')
    print(f"  {class_name:12s} ({int(u)}): {c:7,} pixels ({c/total*100:5.2f}%)")

print("\n" + "=" * 80)
print("✓ Quality check complete!")
print(f"✓ All figures saved to: {OUT_DIR}/")
print("=" * 80)

print("\nNext Steps:")
print("  1. Review all comparison figures in:", OUT_DIR)
print("  2. Open predictions in QGIS for detailed visual inspection")
print("  3. Validate predictions against well observations")
print("  4. Prepare stakeholder presentation materials")
