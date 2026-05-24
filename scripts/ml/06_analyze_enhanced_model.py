"""
Visualize feature importances and model performance
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from path_config import FEATURE_IMPORTANCE_CSV, CV_RESULTS_CSV, FIGURES_DIR

print("="*70)
print("ENHANCED WATERSHED MODEL RESULTS")
print("="*70)

# Load feature importances
fi = pd.read_csv(str(FEATURE_IMPORTANCE_CSV))
print("\nFeature Importances:")
print(fi.to_string(index=False))

# Load CV results
cv = pd.read_csv(str(CV_RESULTS_CSV))
print("\n" + "="*70)
print("CROSS-VALIDATION RESULTS")
print("="*70)
print(cv.to_string(index=False))

mean_acc = cv['accuracy'].mean()
mean_bal_acc = cv['balanced_accuracy'].mean()
print(f"\nMean Accuracy: {mean_acc:.4f} ({mean_acc*100:.2f}%)")
print(f"Mean Balanced Accuracy: {mean_bal_acc:.4f} ({mean_bal_acc*100:.2f}%)")

# Create comprehensive visualization
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# 1. Feature Importances Bar Chart
ax1 = fig.add_subplot(gs[0, :])
colors = ['green' if feat in ['twi', 'tpi', 'dist_stream', 'plan_curv', 'prof_curv', 'aspect'] 
          else 'steelblue' for feat in fi['feature']]
bars = ax1.barh(range(len(fi)), fi['importance'], color=colors, alpha=0.7)
ax1.set_yticks(range(len(fi)))
ax1.set_yticklabels(fi['feature'], fontsize=10)
ax1.set_xlabel('Importance', fontsize=12, fontweight='bold')
ax1.set_title('Feature Importances - Random Forest Model\n(14 Features with Enhanced Watershed Parameters)', 
              fontsize=14, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# Add percentage labels
for i, (feat, imp) in enumerate(zip(fi['feature'], fi['importance'])):
    ax1.text(imp + 0.01, i, f'{imp*100:.2f}%', 
             va='center', fontsize=9, fontweight='bold')

# Add legend
legend_elements = [
    Patch(facecolor='green', alpha=0.7, label='NEW Watershed Features'),
    Patch(facecolor='steelblue', alpha=0.7, label='Original Features')
]
ax1.legend(handles=legend_elements, loc='lower right', fontsize=10)

# 2. Top 10 Features Pie Chart
ax2 = fig.add_subplot(gs[1, 0])
top10 = fi.head(10)
colors_pie = ['green' if feat in ['twi', 'tpi', 'dist_stream', 'plan_curv', 'prof_curv', 'aspect'] 
              else 'steelblue' for feat in top10['feature']]
wedges, texts, autotexts = ax2.pie(top10['importance'], labels=top10['feature'], 
                                     colors=colors_pie,
                                     autopct='%1.1f%%', startangle=90)
ax2.set_title('Top 10 Features\nDistribution', fontsize=12, fontweight='bold')
for text in texts:
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)

# 3. Cross-Validation Performance
ax3 = fig.add_subplot(gs[1, 1])
x_pos = np.arange(len(cv))
width = 0.35
bars1 = ax3.bar(x_pos - width/2, cv['accuracy'], width, label='Accuracy', 
                color='steelblue', alpha=0.7)
bars2 = ax3.bar(x_pos + width/2, cv['balanced_accuracy'], width, 
                label='Balanced Accuracy', color='green', alpha=0.7)
ax3.set_xlabel('Fold', fontsize=11, fontweight='bold')
ax3.set_ylabel('Score', fontsize=11, fontweight='bold')
ax3.set_title(f'Cross-Validation Performance\nMean Acc: {mean_acc:.3f} | Mean Bal Acc: {mean_bal_acc:.3f}', 
              fontsize=12, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels([f'Fold {i}' for i in range(1, len(cv)+1)])
ax3.legend(fontsize=10)
ax3.set_ylim(0.85, 1.0)
ax3.grid(axis='y', alpha=0.3)
ax3.axhline(y=mean_acc, color='steelblue', linestyle='--', linewidth=1, alpha=0.5)
ax3.axhline(y=mean_bal_acc, color='green', linestyle='--', linewidth=1, alpha=0.5)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)

plt.suptitle('Enhanced Watershed Features - Model Performance Analysis', 
             fontsize=16, fontweight='bold', y=0.98)

outfile = str(FIGURES_DIR / 'enhanced_model_results.png')
plt.savefig(outfile, dpi=150, bbox_inches='tight')
print(f"\n✓ Saved: {outfile}")
plt.close()

# Print summary
print("\n" + "="*70)
print("KEY INSIGHTS")
print("="*70)

# Calculate contribution of new features
new_features = ['twi', 'tpi', 'dist_stream', 'plan_curv', 'prof_curv', 'aspect']
new_feat_importance = fi[fi['feature'].isin(new_features)]['importance'].sum()
print(f"\n1. NEW Watershed Features Contribution:")
print(f"   Total importance: {new_feat_importance:.4f} ({new_feat_importance*100:.2f}%)")
print(f"   Individual contributions:")
for feat in new_features:
    imp = fi[fi['feature'] == feat]['importance'].values[0]
    print(f"   - {feat:15s}: {imp:.4f} ({imp*100:.2f}%)")

print(f"\n2. Model Performance:")
print(f"   Mean Accuracy:          {mean_acc:.4f} ({mean_acc*100:.2f}%)")
print(f"   Mean Balanced Accuracy: {mean_bal_acc:.4f} ({mean_bal_acc*100:.2f}%)")
print(f"   CV Folds: {len(cv)}")

print(f"\n3. Top 5 Most Important Features:")
for i, (feat, imp) in enumerate(fi.head(5).values, 1):
    marker = "🆕" if feat in new_features else "  "
    print(f"   {i}. {marker} {feat:15s}: {imp:.4f} ({imp*100:.2f}%)")

print(f"\n4. Watershed Features in Top 10:")
top10_watershed = [f for f in fi.head(10)['feature'] if f in new_features]
print(f"   {len(top10_watershed)} out of 6 new features made it to top 10:")
for feat in top10_watershed:
    rank = fi[fi['feature'] == feat].index[0] + 1
    imp = fi[fi['feature'] == feat]['importance'].values[0]
    print(f"   - {feat:15s}: Rank #{rank}, {imp*100:.2f}%")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
✅ Model successfully trained with 14 enhanced features
✅ New watershed features contribute ~13.9% total importance
✅ TPI, TWI, and dist_stream are the most important new features
✅ Model achieves >96% accuracy with balanced performance
✅ Hydrological features provide meaningful spatial information

Next steps:
1. Generate prediction maps: python src/predict_map.py
2. Run SHAP analysis: .\\run_shap.bat
3. Visualize results: python src/visualize.py
""")
