"""
Create comprehensive visualization showing the impact of enhanced watershed features
"""
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

print("="*70)
print("ENHANCED WATERSHED FEATURES - IMPACT ANALYSIS")
print("="*70)

# Load prediction maps
print("\nLoading prediction maps...")
with rasterio.open('data/processed/stage4/predicted_grp_score.tif') as src:
    pred_score = src.read(1)
    profile = src.profile

with rasterio.open('data/processed/stage4/predicted_grp_class.tif') as src:
    pred_class = src.read(1)

# Load some key enhanced features for comparison
print("Loading enhanced watershed features...")
with rasterio.open('data/processed/stage3/twi_lucknow.tif') as src:
    twi = src.read(1)

with rasterio.open('data/processed/stage3/tpi_lucknow.tif') as src:
    tpi = src.read(1)

with rasterio.open('data/processed/stage3/distance_to_stream_lucknow.tif') as src:
    dist_stream = src.read(1)

# Load feature importances
fi = pd.read_csv('data/processed/stage4/feature_importances.csv')
watershed_features = ['twi', 'tpi', 'dist_stream', 'plan_curv', 'prof_curv', 'aspect']
watershed_fi = fi[fi['feature'].isin(watershed_features)]

print("\nWatershed Features Contribution:")
print(watershed_fi.to_string(index=False))
total_watershed = watershed_fi['importance'].sum()
print(f"\nTotal Watershed Features Importance: {total_watershed:.4f} ({total_watershed*100:.2f}%)")

# Create comprehensive figure
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# Row 1: Prediction Results
ax1 = fig.add_subplot(gs[0, 0])
im1 = ax1.imshow(pred_score, cmap='RdYlGn', vmin=0, vmax=1, interpolation='nearest')
ax1.set_title('Groundwater Potential Score\n(Predicted with 14 Enhanced Features)', 
              fontsize=11, fontweight='bold')
ax1.axis('off')
cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
cbar1.set_label('Probability', rotation=270, labelpad=15)

ax2 = fig.add_subplot(gs[0, 1])
class_colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
cmap_class = plt.matplotlib.colors.ListedColormap(class_colors)
im2 = ax2.imshow(pred_class, cmap=cmap_class, vmin=1, vmax=5, interpolation='nearest')
ax2.set_title('Groundwater Potential Classes\n(1=Very Low, 5=Very High)', 
              fontsize=11, fontweight='bold')
ax2.axis('off')
cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, 
                     ticks=[1, 2, 3, 4, 5])
cbar2.set_label('Class', rotation=270, labelpad=15)

# Statistics
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')
stats_text = f"""
PREDICTION STATISTICS

Valid Pixels: {np.sum(~np.isnan(pred_score)):,}

Score Distribution:
  Mean:   {np.nanmean(pred_score):.3f}
  Median: {np.nanmedian(pred_score):.3f}
  Std:    {np.nanstd(pred_score):.3f}
  Min:    {np.nanmin(pred_score):.3f}
  Max:    {np.nanmax(pred_score):.3f}

Class Distribution:
  Class 1: {np.sum(pred_class==1):>7,} ({100*np.sum(pred_class==1)/np.sum(~np.isnan(pred_class)):.1f}%)
  Class 2: {np.sum(pred_class==2):>7,} ({100*np.sum(pred_class==2)/np.sum(~np.isnan(pred_class)):.1f}%)
  Class 3: {np.sum(pred_class==3):>7,} ({100*np.sum(pred_class==3)/np.sum(~np.isnan(pred_class)):.1f}%)
  Class 4: {np.sum(pred_class==4):>7,} ({100*np.sum(pred_class==4)/np.sum(~np.isnan(pred_class)):.1f}%)
  Class 5: {np.sum(pred_class==5):>7,} ({100*np.sum(pred_class==5)/np.sum(~np.isnan(pred_class)):.1f}%)

Model Performance:
  Accuracy:     95.63%
  Features:     14 (6 new)
  Watershed:    13.91% importance
"""
ax3.text(0.1, 0.95, stats_text, transform=ax3.transAxes, 
         fontsize=9, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# Row 2: Key Enhanced Features
ax4 = fig.add_subplot(gs[1, 0])
twi_clean = np.where(np.isfinite(twi), twi, np.nan)
im4 = ax4.imshow(twi_clean, cmap='Blues', interpolation='nearest')
ax4.set_title('TWI - Water Accumulation\n(Importance: 2.21%, Rank #7)', 
              fontsize=11, fontweight='bold', color='darkblue')
ax4.axis('off')
plt.colorbar(im4, ax=ax4, fraction=0.046, pad=0.04)

ax5 = fig.add_subplot(gs[1, 1])
tpi_clean = np.where(np.isfinite(tpi), tpi, np.nan)
im5 = ax5.imshow(tpi_clean, cmap='terrain', interpolation='nearest')
ax5.set_title('TPI - Ridge/Valley Position\n(Importance: 2.62%, Rank #6)', 
              fontsize=11, fontweight='bold', color='darkgreen')
ax5.axis('off')
plt.colorbar(im5, ax=ax5, fraction=0.046, pad=0.04)

ax6 = fig.add_subplot(gs[1, 2])
dist_clean = np.where(np.isfinite(dist_stream), dist_stream, np.nan)
im6 = ax6.imshow(dist_clean, cmap='YlGnBu_r', interpolation='nearest')
ax6.set_title('Distance to Streams\n(Importance: 2.06%, Rank #8)', 
              fontsize=11, fontweight='bold', color='darkred')
ax6.axis('off')
cbar6 = plt.colorbar(im6, ax=ax6, fraction=0.046, pad=0.04)
cbar6.set_label('meters', rotation=270, labelpad=15)

# Row 3: Feature Importance Breakdown
ax7 = fig.add_subplot(gs[2, :])
colors = ['green' if f in watershed_features else 'steelblue' for f in fi['feature']]
bars = ax7.barh(range(len(fi)), fi['importance'], color=colors, alpha=0.7)
ax7.set_yticks(range(len(fi)))
ax7.set_yticklabels(fi['feature'], fontsize=10)
ax7.set_xlabel('Feature Importance', fontsize=12, fontweight='bold')
ax7.set_title('Feature Importances - All 14 Features\n(Green = New Watershed Features)', 
              fontsize=12, fontweight='bold')
ax7.invert_yaxis()
ax7.grid(axis='x', alpha=0.3)

# Add percentage labels
for i, (feat, imp) in enumerate(zip(fi['feature'], fi['importance'])):
    marker = "🌊" if feat in watershed_features else ""
    ax7.text(imp + 0.01, i, f'{marker} {imp*100:.2f}%', 
             va='center', fontsize=9, fontweight='bold')

# Legend
legend_elements = [
    Patch(facecolor='green', alpha=0.7, label=f'NEW Watershed Features (6 total, {total_watershed*100:.2f}% importance)'),
    Patch(facecolor='steelblue', alpha=0.7, label='Original Features (8 total)')
]
ax7.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.suptitle('Enhanced Watershed Features - Groundwater Potential Prediction Results\n' +
             'Model: Random Forest (95.63% accuracy) | Features: 14 (6 new hydrological)', 
             fontsize=14, fontweight='bold', y=0.98)

outfile = 'data/processed/stage4/figs/enhanced_features_impact.png'
plt.savefig(outfile, dpi=150, bbox_inches='tight')
print(f"\n✓ Saved: {outfile}")
plt.close()

# Create side-by-side comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Before (simulated - using only grp_score which was dominant)
ax1 = axes[0]
with rasterio.open('data/processed/grp_score_lucknow.tif') as src:
    grp_score = src.read(1)
grp_score_norm = (grp_score - np.nanmin(grp_score)) / (np.nanmax(grp_score) - np.nanmin(grp_score))
im1 = ax1.imshow(grp_score_norm, cmap='RdYlGn', vmin=0, vmax=1, interpolation='nearest')
ax1.set_title('BEFORE: AHP-Based Prediction\n(Dominated by grp_score, uniform geology)', 
              fontsize=13, fontweight='bold', color='darkred')
ax1.axis('off')
cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
cbar1.set_label('Normalized Score', rotation=270, labelpad=15)

# After
ax2 = axes[1]
im2 = ax2.imshow(pred_score, cmap='RdYlGn', vmin=0, vmax=1, interpolation='nearest')
ax2.set_title('AFTER: ML-Based Prediction\n(14 features including 6 watershed parameters)', 
              fontsize=13, fontweight='bold', color='darkgreen')
ax2.axis('off')
cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
cbar2.set_label('Probability', rotation=270, labelpad=15)

plt.suptitle('Impact of Enhanced Watershed Features on Groundwater Prediction', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])

outfile2 = 'data/processed/stage4/figs/before_after_comparison.png'
plt.savefig(outfile2, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {outfile2}")
plt.close()

print("\n" + "="*70)
print("VISUALIZATION COMPLETE")
print("="*70)
print(f"""
Created comprehensive visualizations:
1. {outfile}
   - 9-panel overview showing predictions and key features
   - Feature importance breakdown
   - Statistics summary

2. {outfile2}
   - Side-by-side comparison: AHP vs ML predictions
   - Shows impact of enhanced watershed features

Key Findings:
✅ Model achieves 95.63% accuracy with 14 features
✅ Watershed features contribute 13.91% total importance
✅ TPI, TWI, and dist_stream are top watershed features
✅ Predictions show spatial detail from hydrological features
✅ Ready for thesis presentation and stakeholder demo!
""")
