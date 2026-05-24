#!/usr/bin/env python
"""
src/prioritize_watersheds.py

Prioritize watersheds for groundwater intervention based on multi-criteria analysis.

Criteria (weighted scoring):
1. Groundwater stress (30%) - Lower GWP = higher stress = higher priority
2. Improvement potential (25%) - Moderate GWP = best improvement potential
3. Population served (20%) - Urban/cropland areas (proxy for demand)
4. Feasibility (15%) - Slope, drainage suitability for structures
5. Cost-effectiveness (10%) - Smaller watersheds = cheaper interventions

Also recommends specific interventions:
- Check dams (medium slope, good streams)
- Percolation tanks (gentle slope, cropland)
- Recharge wells (urban, high GWP)
- Farm ponds (cropland dominant)
- Reforestation (degraded areas)

Outputs (data/processed/stage4/):
 - watersheds_prioritized.shp : Shapefile with priority scores & recommendations
 - watersheds_prioritized.csv : CSV table for analysis
 - priority_summary.txt : Text summary report

Usage:
    python src/prioritize_watersheds.py

Prerequisites:
    - src/characterize_watersheds.py (watersheds with extracted statistics)
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

# Paths
WATERSHEDS_CHAR_FILE = "data/processed/stage4/watersheds_characterized.shp"
WATERSHEDS_CHAR_CSV = "data/processed/stage4/watersheds_characterized.csv"
OUT_DIR = "data/processed/stage4"

# Outputs
OUT_SHP = os.path.join(OUT_DIR, "watersheds_prioritized.shp")
OUT_CSV = os.path.join(OUT_DIR, "watersheds_prioritized.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "priority_summary.txt")

# Weights for multi-criteria prioritization
WEIGHTS = {
    'stress': 0.30,        # Groundwater stress level
    'potential': 0.25,     # Improvement potential
    'population': 0.20,    # People served
    'feasibility': 0.15,   # Technical feasibility
    'cost': 0.10           # Cost-effectiveness
}


def normalize_series(series, reverse=False):
    """
    Normalize series to 0-1 range
    
    Parameters:
    -----------
    series : pd.Series
        Values to normalize
    reverse : bool
        If True, reverse the scale (high values → low scores)
    
    Returns:
    --------
    Normalized series (0-1 range)
    """
    min_val = series.min()
    max_val = series.max()
    
    if max_val == min_val:
        return pd.Series([0.5] * len(series), index=series.index)
    
    normalized = (series - min_val) / (max_val - min_val)
    
    if reverse:
        normalized = 1 - normalized
    
    return normalized


def calculate_priority_scores(gdf):
    """
    Calculate multi-criteria priority scores for each watershed
    
    Returns GeoDataFrame with added columns:
    - stress_score, potential_score, population_score, feasibility_score, cost_score
    - priority_score (weighted combination)
    - priority_class (High/Medium/Low)
    """
    
    print("\n" + "="*70)
    print("CALCULATING PRIORITY SCORES")
    print("="*70)
    
    # 1. Groundwater Stress Score (30%)
    # Lower GWP = higher stress = higher priority
    print("\n1. Groundwater Stress (30%):")
    print("   Lower GWP → Higher stress → Higher priority")
    
    gdf['stress_score'] = normalize_series(gdf['gwp_mean'], reverse=True)
    print(f"   ✓ Stress scores: {gdf['stress_score'].min():.3f} - {gdf['stress_score'].max():.3f}")
    
    # 2. Improvement Potential Score (25%)
    # Moderate GWP (0.3-0.7) has best improvement potential
    # Too low = hard to improve, too high = already good
    print("\n2. Improvement Potential (25%):")
    print("   Moderate GWP (0.3-0.7) → Best improvement potential")
    
    # Inverted U-shape: peak at GWP=0.5
    gdf['potential_score'] = 1 - abs(gdf['gwp_mean'] - 0.5) * 2
    gdf['potential_score'] = gdf['potential_score'].clip(0, 1)
    print(f"   ✓ Potential scores: {gdf['potential_score'].min():.3f} - {gdf['potential_score'].max():.3f}")
    
    # 3. Population Served Score (20%)
    # Urban/cropland areas = higher population/demand
    print("\n3. Population Served (20%):")
    print("   Urban (3x weight) + Cropland (1x weight)")
    
    gdf['pop_proxy'] = (gdf['urban'] * 3 + gdf['cropland'] * 1) * gdf['area_km2']
    gdf['population_score'] = normalize_series(gdf['pop_proxy'])
    print(f"   ✓ Population scores: {gdf['population_score'].min():.3f} - {gdf['population_score'].max():.3f}")
    
    # 4. Feasibility Score (15%)
    # Moderate slope (5-15°), adequate drainage
    print("\n4. Technical Feasibility (15%):")
    print("   Slope suitability + Drainage adequacy")
    
    # Slope suitability (5-15° ideal for most structures)
    slope_ideal = 10.0  # degrees
    slope_tolerance = 15.0
    slope_suit = 1 - abs(gdf['slope_mean'] - slope_ideal) / slope_tolerance
    slope_suit = slope_suit.clip(0, 1)
    
    # Drainage adequacy (moderate drainage density is good)
    drain_suit = normalize_series(gdf['drain_dens'])
    drain_suit = 1 - abs(drain_suit - 0.5) * 2  # Peak at median
    
    gdf['feasibility_score'] = (slope_suit + drain_suit) / 2
    print(f"   ✓ Feasibility scores: {gdf['feasibility_score'].min():.3f} - {gdf['feasibility_score'].max():.3f}")
    
    # 5. Cost-Effectiveness Score (10%)
    # Smaller watersheds = cheaper interventions
    print("\n5. Cost-Effectiveness (10%):")
    print("   Smaller areas → Lower costs → Higher score")
    
    gdf['cost_score'] = normalize_series(gdf['area_km2'], reverse=True)
    print(f"   ✓ Cost scores: {gdf['cost_score'].min():.3f} - {gdf['cost_score'].max():.3f}")
    
    # Weighted combination
    print("\n6. Computing Final Priority Score:")
    print(f"   Weights: {WEIGHTS}")
    
    gdf['priority_score'] = (
        gdf['stress_score'] * WEIGHTS['stress'] +
        gdf['potential_score'] * WEIGHTS['potential'] +
        gdf['population_score'] * WEIGHTS['population'] +
        gdf['feasibility_score'] * WEIGHTS['feasibility'] +
        gdf['cost_score'] * WEIGHTS['cost']
    )
    
    print(f"   ✓ Priority scores: {gdf['priority_score'].min():.3f} - {gdf['priority_score'].max():.3f}")
    
    # Classify into priority classes
    gdf['priority_class'] = pd.cut(
        gdf['priority_score'],
        bins=[0, 0.35, 0.65, 1.0],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    
    print(f"\n   Priority Distribution:")
    print(gdf['priority_class'].value_counts().sort_index().to_string())
    
    return gdf


def recommend_interventions(gdf):
    """
    Recommend specific interventions for each watershed based on characteristics
    
    Decision tree:
    1. Check dams: Medium slope (5-15°), good streams, <3 km²
    2. Percolation tanks: Gentle slope (<5°), cropland >30%, >1 km²
    3. Recharge wells: Urban >20%, high GWP, flat (<3°)
    4. Farm ponds: Cropland >50%, moderate slope
    5. Reforestation: Degraded areas, low forest cover
    
    Returns DataFrame with intervention details
    """
    
    print("\n" + "="*70)
    print("RECOMMENDING INTERVENTIONS")
    print("="*70)
    
    interventions = []
    
    for idx, row in gdf.iterrows():
        intervention = {
            'primary': '',
            'secondary': [],
            'cost_lakhs': 0,
            'recharge_mcm': 0,
            'structures': 0
        }
        
        # Decision tree
        
        # 1. Check dams (medium slope, streams, moderate area)
        if (5 <= row['slope_mean'] <= 15 and 
            row['stream_km'] > 1.5 and 
            row['area_km2'] < 3.0):
            
            n_dams = max(1, int(row['stream_km'] / 0.5))  # 1 per 500m stream
            intervention['primary'] = f"Check Dams ({n_dams} nos)"
            intervention['structures'] = n_dams
            intervention['cost_lakhs'] = n_dams * 8  # ₹8 lakhs per dam
            intervention['recharge_mcm'] = n_dams * 0.05  # 50,000 m³ per dam
        
        # 2. Percolation tanks (gentle slope, cropland)
        elif (row['slope_mean'] < 5 and 
              row['cropland'] > 30 and 
              row['area_km2'] > 1.0):
            
            n_tanks = max(1, int(row['area_km2'] / 2))  # 1 per 2 km²
            intervention['primary'] = f"Percolation Tanks ({n_tanks} nos)"
            intervention['structures'] = n_tanks
            intervention['cost_lakhs'] = n_tanks * 15  # ₹15 lakhs per tank
            intervention['recharge_mcm'] = n_tanks * 0.1  # 100,000 m³ per tank
        
        # 3. Recharge wells (urban, high GWP, flat)
        elif (row['urban'] > 20 and 
              row['gwp_mean'] > 0.5 and 
              row['slope_mean'] < 3):
            
            n_wells = max(2, int(row['urban'] / 10))  # 1 per 10% urban
            intervention['primary'] = f"Recharge Wells ({n_wells} nos)"
            intervention['structures'] = n_wells
            intervention['cost_lakhs'] = n_wells * 2.5  # ₹2.5 lakhs per well
            intervention['recharge_mcm'] = n_wells * 0.02  # 20,000 m³ per well
        
        # 4. Farm ponds (cropland dominant)
        elif row['cropland'] > 50:
            n_ponds = max(1, int(row['cropland'] / 25))
            intervention['primary'] = f"Farm Ponds ({n_ponds} nos)"
            intervention['structures'] = n_ponds
            intervention['cost_lakhs'] = n_ponds * 5  # ₹5 lakhs per pond
            intervention['recharge_mcm'] = n_ponds * 0.03  # 30,000 m³ per pond
        
        # 5. Reforestation (default for degraded areas)
        else:
            area_ha = row['area_km2'] * 100
            intervention['primary'] = f"Reforestation ({area_ha:.0f} ha)"
            intervention['structures'] = int(area_ha / 10)  # Treatment units
            intervention['cost_lakhs'] = area_ha * 0.5  # ₹50k per ha
            intervention['recharge_mcm'] = area_ha * 0.001  # Long-term benefit
        
        # Secondary interventions (always recommended)
        if row['forest'] < 10:
            intervention['secondary'].append("Increase green cover to 20%")
        
        if row['urban'] > 30:
            intervention['secondary'].append("Mandate rainwater harvesting")
        
        if row['slope_mean'] > 10:
            intervention['secondary'].append("Soil conservation (contour bunding)")
        
        if row['drain_dens'] < 0.5:
            intervention['secondary'].append("Improve drainage network")
        
        interventions.append(intervention)
    
    # Add to GeoDataFrame
    gdf['primary_intervention'] = [i['primary'] for i in interventions]
    gdf['secondary_interventions'] = ['; '.join(i['secondary']) for i in interventions]
    gdf['n_structures'] = [i['structures'] for i in interventions]
    gdf['cost_lakhs'] = [i['cost_lakhs'] for i in interventions]
    gdf['recharge_mcm'] = [i['recharge_mcm'] for i in interventions]
    
    # Intervention type summary
    print("\nIntervention Type Distribution:")
    intervention_types = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
    for int_type, count in intervention_types.items():
        print(f"  {int_type}: {count} watersheds")
    
    print(f"\nBudget & Impact Summary:")
    print(f"  Total estimated cost: ₹{gdf['cost_lakhs'].sum() / 100:.2f} Crores")
    print(f"  Expected annual recharge: {gdf['recharge_mcm'].sum():.2f} MCM")
    print(f"  Total structures: {gdf['n_structures'].sum():.0f}")
    
    return gdf


def generate_summary_report(gdf, output_path):
    """
    Generate text summary report for quick review
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("WATERSHED PRIORITIZATION SUMMARY REPORT\n")
        f.write("Lucknow District Groundwater Management Plan\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Date: {pd.Timestamp.now().strftime('%B %d, %Y')}\n")
        f.write(f"Total Watersheds: {len(gdf)}\n")
        f.write(f"Total Area: {gdf['area_km2'].sum():.2f} km²\n\n")
        
        f.write("PRIORITY DISTRIBUTION:\n")
        f.write("-" * 40 + "\n")
        priority_counts = gdf['priority_class'].value_counts().sort_index()
        for pclass, count in priority_counts.items():
            pct = count / len(gdf) * 100
            f.write(f"  {pclass} Priority: {count} watersheds ({pct:.1f}%)\n")
        
        f.write("\n\nBUDGET & IMPACT SUMMARY:\n")
        f.write("-" * 40 + "\n")
        f.write(f"  Total Budget: ₹{gdf['cost_lakhs'].sum() / 100:.2f} Crores\n")
        f.write(f"  Expected Recharge: {gdf['recharge_mcm'].sum():.2f} MCM/year\n")
        f.write(f"  Total Structures: {gdf['n_structures'].sum():.0f}\n")
        f.write(f"  Cost per MCM: ₹{gdf['cost_lakhs'].sum() * 10 / gdf['recharge_mcm'].sum():.2f} lakhs\n")
        
        f.write("\n\nINTERVENTION BREAKDOWN:\n")
        f.write("-" * 40 + "\n")
        intervention_types = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
        for int_type, count in intervention_types.items():
            int_cost = gdf[gdf['primary_intervention'].str.contains(int_type)]['cost_lakhs'].sum() / 100
            f.write(f"  {int_type}:\n")
            f.write(f"    Watersheds: {count}\n")
            f.write(f"    Budget: ₹{int_cost:.2f} Cr\n")
        
        f.write("\n\nTOP 10 PRIORITY WATERSHEDS:\n")
        f.write("-" * 40 + "\n")
        top10 = gdf.nlargest(10, 'priority_score')
        f.write(f"{'Rank':<6}{'ID':<6}{'Area':<8}{'Priority':<10}{'Intervention':<30}{'Cost':<10}\n")
        f.write("-" * 70 + "\n")
        
        for rank, (idx, row) in enumerate(top10.iterrows(), 1):
            intervention_short = row['primary_intervention'][:28]
            f.write(f"{rank:<6}{row['watershed_id']:<6}{row['area_km2']:<8.2f}"
                   f"{row['priority_class']:<10}{intervention_short:<30}"
                   f"₹{row['cost_lakhs']:<9.1f}\n")
        
        f.write("\n\n" + "="*70 + "\n")
        f.write("RECOMMENDATIONS FOR IMMEDIATE ACTION:\n")
        f.write("="*70 + "\n\n")
        
        high_priority = gdf[gdf['priority_class'] == 'High'].nlargest(5, 'priority_score')
        
        for rank, (idx, row) in enumerate(high_priority.iterrows(), 1):
            f.write(f"{rank}. Watershed ID: {row['watershed_id']} (Score: {row['priority_score']:.3f})\n")
            f.write(f"   Location: {row['centroid_lat']:.4f}°N, {row['centroid_lon']:.4f}°E\n")
            f.write(f"   Area: {row['area_km2']:.2f} km²\n")
            f.write(f"   Primary Intervention: {row['primary_intervention']}\n")
            f.write(f"   Estimated Cost: ₹{row['cost_lakhs']:.2f} lakhs\n")
            f.write(f"   Expected Impact: {row['recharge_mcm']:.3f} MCM/year\n")
            if row['secondary_interventions']:
                f.write(f"   Secondary Actions: {row['secondary_interventions']}\n")
            f.write("\n")
        
        f.write("="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    print(f"\n✓ Summary report saved: {output_path}")


def main():
    print("="*70)
    print("WATERSHED PRIORITIZATION & ACTION PLANNING")
    print("="*70)
    
    # Check prerequisites - try shapefile first, fallback to CSV
    use_csv_mode = False
    
    if os.path.exists(WATERSHEDS_CHAR_FILE):
        print(f"\nLoading characterized watersheds from: {WATERSHEDS_CHAR_FILE}")
        try:
            gdf = gpd.read_file(WATERSHEDS_CHAR_FILE)
            print(f"  Loaded {len(gdf)} watersheds")
        except Exception as e:
            print(f"  ⚠ Error loading shapefile: {e}")
            print(f"  Trying CSV fallback...")
            use_csv_mode = True
    elif os.path.exists(WATERSHEDS_CHAR_CSV):
        print(f"\n⚠ Shapefile not found, using CSV: {WATERSHEDS_CHAR_CSV}")
        use_csv_mode = True
    else:
        print(f"\n❌ Characterized watersheds not found!")
        print(f"  Tried: {WATERSHEDS_CHAR_FILE}")
        print(f"  Tried: {WATERSHEDS_CHAR_CSV}")
        print("\nPlease run characterize_watersheds.py first!")
        return
    
    if use_csv_mode:
        # Load from CSV (no geometry)
        df = pd.read_csv(WATERSHEDS_CHAR_CSV)
        print(f"  Loaded {len(df)} watersheds (CSV mode - no geometry)")
        # Convert to GeoDataFrame without geometry (will skip shapefile output)
        gdf = df
        gdf.to_file = None  # Disable shapefile output
    
    # Check required columns
    required_cols = ['watershed_id', 'area_km2', 'gwp_mean', 'slope_mean', 
                     'drain_dens', 'stream_km', 'cropland', 'urban', 'forest']
    missing = [col for col in required_cols if col not in gdf.columns]
    
    if missing:
        print(f"\n❌ Missing required columns: {missing}")
        print("Please re-run characterize_watersheds.py")
        return
    
    # Calculate priority scores
    gdf = calculate_priority_scores(gdf)
    
    # Recommend interventions
    gdf = recommend_interventions(gdf)
    
    # Add ranking
    gdf = gdf.sort_values('priority_score', ascending=False).reset_index(drop=True)
    gdf['rank'] = range(1, len(gdf) + 1)
    
    # Save results
    print("\n" + "="*70)
    print("SAVING OUTPUTS")
    print("="*70)
    
    print(f"\nSaving prioritized watersheds...")
    
    # Save shapefile if we have geometry
    if hasattr(gdf, 'to_file') and gdf.to_file is not None and 'geometry' in gdf.columns:
        try:
            gdf.to_file(OUT_SHP)
            print(f"✓ Saved shapefile: {OUT_SHP}")
        except Exception as e:
            print(f"⚠ Could not save shapefile: {e}")
            print(f"  Continuing with CSV only...")
    
    # Save CSV
    if 'geometry' in gdf.columns:
        csv_df = gdf.drop('geometry', axis=1)
    else:
        csv_df = gdf
    csv_df.to_csv(OUT_CSV, index=False)
    print(f"✓ Saved CSV: {OUT_CSV}")
    
    # Generate summary report
    generate_summary_report(gdf, OUT_SUMMARY)
    
    # Console summary
    print("\n" + "="*70)
    print("PRIORITIZATION COMPLETE!")
    print("="*70)
    
    print(f"\nStatistics:")
    print(f"  Total watersheds: {len(gdf)}")
    print(f"  High priority: {(gdf['priority_class'] == 'High').sum()}")
    print(f"  Medium priority: {(gdf['priority_class'] == 'Medium').sum()}")
    print(f"  Low priority: {(gdf['priority_class'] == 'Low').sum()}")
    
    print(f"\nBudget & Impact:")
    print(f"  Total cost: ₹{gdf['cost_lakhs'].sum() / 100:.2f} Crores")
    print(f"  Expected recharge: {gdf['recharge_mcm'].sum():.2f} MCM/year")
    print(f"  Cost per MCM: ₹{gdf['cost_lakhs'].sum() * 10 / gdf['recharge_mcm'].sum():.2f} lakhs")
    
    print(f"\nOutputs:")
    print(f"  1. Shapefile: {OUT_SHP}")
    print(f"  2. CSV: {OUT_CSV}")
    print(f"  3. Summary: {OUT_SUMMARY}")
    
    print(f"\n✓ Watersheds prioritized and ready for reporting!")
    print(f"\nNext step: python src/generate_watershed_reports.py")


if __name__ == "__main__":
    main()
