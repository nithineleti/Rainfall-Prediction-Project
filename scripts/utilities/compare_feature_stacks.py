"""
Compare old vs new feature stack
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("="*70)
print("FEATURE STACK COMPARISON")
print("="*70)

# Old feature set
old_features = [
    "Slope",
    "LULC",
    "Rainfall",
    "Geology (UNIFORM - no variance!)",
    "NDVI",
    "Flow Accumulation",
    "Stream Network",
    "Drainage Density",
    "GRP Score"
]

# New feature set
new_features = [
    "Slope",
    "LULC",
    "Rainfall",
    "NDVI",
    "Flow Accumulation",
    "Stream Network",
    "Drainage Density",
    "TWI (Water Accumulation)",
    "Aspect (Slope Direction)",
    "Plan Curvature (Convergence)",
    "Profile Curvature (Acceleration)",
    "TPI (Ridge/Valley)",
    "Distance to Streams",
    "GRP Score"
]

print(f"\nOLD: {len(old_features)} features")
print(f"NEW: {len(new_features)} features")
print(f"NET: +{len(new_features) - len(old_features)} features")

# Create comparison table
print("\n" + "="*70)
print("DETAILED COMPARISON")
print("="*70)

comparison = pd.DataFrame({
    'Old Feature Set (9 bands)': old_features + [''] * (len(new_features) - len(old_features)),
    'New Feature Set (14 bands)': new_features
})

print(comparison.to_string(index=False))

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 10))

# Left panel - Old features
ax1 = axes[0]
y_pos_old = np.arange(len(old_features))
colors_old = ['lightblue' if 'Geology' not in f else 'red' for f in old_features]
ax1.barh(y_pos_old, [1]*len(old_features), color=colors_old, alpha=0.7)
ax1.set_yticks(y_pos_old)
ax1.set_yticklabels(old_features, fontsize=10)
ax1.set_xlabel('Features Available', fontsize=12)
ax1.set_title('OLD Feature Stack\n(9 bands)\n⚠️ Includes uniform geology', 
              fontsize=14, fontweight='bold', color='darkred')
ax1.set_xlim(0, 1.5)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# Add note
ax1.text(0.5, -1, 'RED = No spatial variance', 
         ha='center', fontsize=10, color='red', fontweight='bold')

# Right panel - New features
ax2 = axes[1]
y_pos_new = np.arange(len(new_features))
colors_new = ['lightgreen' if any(x in f for x in ['TWI', 'Aspect', 'Curvature', 'TPI', 'Distance']) else 'lightblue' 
              for f in new_features]
ax2.barh(y_pos_new, [1]*len(new_features), color=colors_new, alpha=0.7)
ax2.set_yticks(y_pos_new)
ax2.set_yticklabels(new_features, fontsize=10)
ax2.set_xlabel('Features Available', fontsize=12)
ax2.set_title('NEW Feature Stack\n(14 bands)\n✅ Enhanced hydrological features', 
              fontsize=14, fontweight='bold', color='darkgreen')
ax2.set_xlim(0, 1.5)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# Add note
ax2.text(0.5, -1, 'GREEN = New watershed features', 
         ha='center', fontsize=10, color='green', fontweight='bold')

plt.suptitle('Feature Stack Enhancement for Watershed Analysis', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig('data/processed/stage3/figs/feature_stack_comparison.png', dpi=150, bbox_inches='tight')
print("\n✓ Saved: data/processed/stage3/figs/feature_stack_comparison.png")
plt.close()

# Summary statistics
print("\n" + "="*70)
print("KEY IMPROVEMENTS")
print("="*70)
print("""
1. REMOVED: Geology (uniform - no predictive power)
2. ADDED: 6 hydrological features with high spatial variance
   - TWI: Water accumulation potential
   - Aspect: Directional effects (evapotranspiration)
   - Plan Curvature: Flow convergence/divergence
   - Profile Curvature: Flow acceleration/deceleration
   - TPI: Ridge/valley classification
   - Distance to Streams: GW-SW interaction

3. RESULT: 
   - More features: 9 → 14 bands (+56% increase)
   - Better spatial detail: High-variance features replace zero-variance
   - Stronger hydrological relevance: Direct watershed processes
   
4. EXPECTED ML IMPROVEMENTS:
   - Higher accuracy (more informative features)
   - Better feature importance distribution
   - Improved spatial prediction patterns
   - Greater interpretability for stakeholders
""")
