# Project Restructure: From Groundwater Zones to Watershed Management

**Date:** October 29, 2025  
**Current Issue:** Project is named "Watershed-UP" but only predicts groundwater potential zones  
**Required Change:** Add watershed delineation + action plan generation for officials

---

## 🎯 New Project Objective

**PRIMARY:** Delineate micro-watersheds and provide actionable management plans for district/block officials

**SECONDARY:** Use groundwater potential prediction as ONE component of watershed prioritization

---

## 📋 What Needs to Change

### Current State vs. Required State

| Component | Current | Required |
|-----------|---------|----------|
| **Primary Output** | Groundwater potential map (raster) | Watershed boundaries (vector polygons) |
| **Deliverable** | Pixel-level classifications | Watershed-level action plans |
| **User** | Water planners (technical) | Block/district officials (administrative) |
| **Scale** | 12.5m pixels | Micro-watersheds (0.5-5 km²) |
| **Actionability** | "This pixel has high potential" | "Watershed #23 needs 3 check dams at these locations" |
| **Reports** | Statistical summaries | Action plans with budgets & timelines |

---

## 🔧 Technical Implementation Plan

### Phase 1: Add Watershed Delineation (Week 1)

#### 1.1 Implement Watershed Delineation Module

**New File:** `src/delineate_watersheds.py`

```python
"""
Delineate micro-watersheds from DEM using D8 flow routing

Outputs:
- watershed_boundaries_lucknow.shp (vector polygons)
- watershed_attributes.csv (area, perimeter, outlet coords)
- pour_points_lucknow.shp (watershed outlets)
"""

import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, Point
from scipy import ndimage

def delineate_watersheds(
    flow_dir,
    flow_acc,
    min_area_km2=0.5,
    max_area_km2=5.0,
    pixel_size_m=12.5
):
    """
    Delineate micro-watersheds using flow accumulation peaks
    
    Parameters:
    -----------
    flow_dir : ndarray
        D8 flow direction array
    flow_acc : ndarray
        Flow accumulation array
    min_area_km2 : float
        Minimum watershed area (km²)
    max_area_km2 : float
        Maximum watershed area (km²)
    pixel_size_m : float
        DEM pixel size in meters
    
    Returns:
    --------
    watersheds : ndarray
        Watershed ID for each pixel
    pour_points : list of (row, col)
        Outlet locations
    """
    
    # Convert area thresholds to pixel counts
    pixel_area_km2 = (pixel_size_m / 1000) ** 2
    min_pixels = int(min_area_km2 / pixel_area_km2)
    max_pixels = int(max_area_km2 / pixel_area_km2)
    
    # Find pour points (local maxima in flow accumulation)
    # These are points where multiple streams converge
    from scipy.ndimage import maximum_filter
    
    # Local maxima detection
    local_max = maximum_filter(flow_acc, size=20)
    pour_point_mask = (flow_acc == local_max) & (flow_acc > min_pixels)
    
    # Get pour point coordinates
    pour_points = np.argwhere(pour_point_mask)
    
    # Trace watersheds upstream from each pour point
    watersheds = np.zeros_like(flow_acc, dtype=np.int32)
    
    for watershed_id, (row, col) in enumerate(pour_points, start=1):
        # Trace all cells that drain to this pour point
        watershed_mask = trace_upstream(flow_dir, row, col)
        watersheds[watershed_mask] = watershed_id
    
    # Filter by size
    for ws_id in range(1, watersheds.max() + 1):
        ws_size = (watersheds == ws_id).sum()
        if ws_size < min_pixels or ws_size > max_pixels:
            watersheds[watersheds == ws_id] = 0
    
    # Renumber consecutively
    unique_ids = np.unique(watersheds[watersheds > 0])
    for new_id, old_id in enumerate(unique_ids, start=1):
        watersheds[watersheds == old_id] = new_id
    
    return watersheds, pour_points


def trace_upstream(flow_dir, outlet_row, outlet_col):
    """
    Trace all cells that drain to outlet point
    
    Uses reverse flow direction to find contributing area
    """
    rows, cols = flow_dir.shape
    contributing = np.zeros_like(flow_dir, dtype=bool)
    
    # D8 neighbor offsets (opposite direction)
    nbrs = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]
    reverse_nbrs = [(0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)]
    
    # Breadth-first search upstream
    queue = [(outlet_row, outlet_col)]
    contributing[outlet_row, outlet_col] = True
    
    while queue:
        r, c = queue.pop(0)
        
        # Check all neighbors that flow INTO this cell
        for i, (dr, dc) in enumerate(nbrs):
            nr, nc = r + dr, c + dc
            
            # Check bounds
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            
            # If neighbor flows to current cell, add to watershed
            if flow_dir[nr, nc] == i and not contributing[nr, nc]:
                contributing[nr, nc] = True
                queue.append((nr, nc))
    
    return contributing


def vectorize_watersheds(watersheds, transform, crs):
    """
    Convert watershed raster to vector polygons
    
    Returns GeoDataFrame with watershed attributes
    """
    # Extract shapes
    mask = watersheds > 0
    geoms = []
    values = []
    
    for geom, value in shapes(watersheds.astype(np.int32), mask=mask, transform=transform):
        geoms.append(shape(geom))
        values.append(int(value))
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'watershed_id': values,
        'geometry': geoms
    }, crs=crs)
    
    # Calculate attributes
    gdf['area_km2'] = gdf.geometry.area / 1e6  # Assuming UTM
    gdf['perimeter_m'] = gdf.geometry.length
    gdf['compactness'] = (4 * np.pi * gdf['area_km2'] * 1e6) / (gdf['perimeter_m'] ** 2)
    
    # Get centroid
    centroids = gdf.geometry.centroid
    gdf['centroid_lon'] = centroids.x
    gdf['centroid_lat'] = centroids.y
    
    return gdf


def main():
    print("="*70)
    print("MICRO-WATERSHED DELINEATION")
    print("="*70)
    
    # Load flow direction and accumulation
    with rasterio.open("data/processed/stage3/flow_dir_lucknow.tif") as src:
        flow_dir = src.read(1)
        transform = src.transform
        crs = src.crs
    
    with rasterio.open("data/processed/stage3/flow_acc_lucknow.tif") as src:
        flow_acc = src.read(1)
    
    # Delineate watersheds
    print("\nDelineating micro-watersheds (0.5-5 km²)...")
    watersheds, pour_points = delineate_watersheds(
        flow_dir, flow_acc,
        min_area_km2=0.5,
        max_area_km2=5.0,
        pixel_size_m=12.5
    )
    
    print(f"✓ Identified {watersheds.max()} micro-watersheds")
    
    # Save raster
    profile = {
        'driver': 'GTiff',
        'height': watersheds.shape[0],
        'width': watersheds.shape[1],
        'count': 1,
        'dtype': 'int32',
        'crs': crs,
        'transform': transform,
        'compress': 'lzw'
    }
    
    with rasterio.open("data/processed/stage4/watersheds_lucknow.tif", 'w', **profile) as dst:
        dst.write(watersheds, 1)
    
    print("✓ Saved: data/processed/stage4/watersheds_lucknow.tif")
    
    # Vectorize to polygons
    print("\nVectorizing to shapefile...")
    gdf = vectorize_watersheds(watersheds, transform, crs)
    
    gdf.to_file("data/processed/stage4/watershed_boundaries_lucknow.shp")
    print("✓ Saved: data/processed/stage4/watershed_boundaries_lucknow.shp")
    
    # Save attributes table
    gdf.drop('geometry', axis=1).to_csv("data/processed/stage4/watershed_attributes.csv", index=False)
    print("✓ Saved: data/processed/stage4/watershed_attributes.csv")
    
    # Extract pour points
    pour_point_geoms = []
    for row, col in pour_points:
        lon, lat = transform * (col, row)
        pour_point_geoms.append(Point(lon, lat))
    
    pour_gdf = gpd.GeoDataFrame({
        'point_id': range(1, len(pour_point_geoms) + 1),
        'geometry': pour_point_geoms
    }, crs=crs)
    
    pour_gdf.to_file("data/processed/stage4/pour_points_lucknow.shp")
    print("✓ Saved: data/processed/stage4/pour_points_lucknow.shp")
    
    print("\n" + "="*70)
    print("DELINEATION COMPLETE!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  Total watersheds: {len(gdf)}")
    print(f"  Area range: {gdf['area_km2'].min():.2f} - {gdf['area_km2'].max():.2f} km²")
    print(f"  Mean area: {gdf['area_km2'].mean():.2f} km²")
    print(f"  Total coverage: {gdf['area_km2'].sum():.2f} km²")


if __name__ == "__main__":
    main()
```

**Prerequisites:**
- Need to save flow direction in `derive_drainage.py` (currently not saved)

---

#### 1.2 Update derive_drainage.py to Save Flow Direction

**File:** `src/derive_drainage.py`

Add after line 169 (after computing flow direction):

```python
# Save flow direction (needed for watershed delineation)
OUT_FLOWDIR = os.path.join(OUT_DIR, "flow_dir_lucknow.tif")
profile_flowdir = profile_out.copy()
profile_flowdir.update(dtype='int8', nodata=-1)

with rasterio.open(OUT_FLOWDIR, 'w', **profile_flowdir) as dst:
    dst.write(flowdir.astype('int8'), 1)
print("Wrote flow direction to:", OUT_FLOWDIR)
```

---

### Phase 2: Watershed Characterization (Week 2)

#### 2.1 Extract Zonal Statistics for Each Watershed

**New File:** `src/characterize_watersheds.py`

```python
"""
Extract watershed-level statistics from raster layers

For each watershed:
- Mean groundwater potential score
- Dominant soil type
- Mean slope
- Mean rainfall
- LULC distribution
- Stream density
- Geology type
"""

import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd
from collections import Counter

def extract_zonal_stats(watershed_gdf, raster_path, stat='mean', categorical=False):
    """
    Extract statistics for each watershed polygon
    
    Parameters:
    -----------
    watershed_gdf : GeoDataFrame
        Watershed boundaries
    raster_path : str
        Path to raster file
    stat : str
        Statistic to compute ('mean', 'sum', 'max', 'min', 'std')
    categorical : bool
        If True, returns mode (most common value)
    
    Returns:
    --------
    Series with values for each watershed
    """
    
    with rasterio.open(raster_path) as src:
        raster = src.read(1)
        transform = src.transform
        
        results = []
        
        for idx, row in watershed_gdf.iterrows():
            # Mask raster to watershed polygon
            try:
                masked, _ = mask(src, [row.geometry], crop=True, nodata=np.nan)
                values = masked[0]
                values = values[np.isfinite(values)]
                
                if len(values) == 0:
                    results.append(np.nan)
                    continue
                
                if categorical:
                    # Most common value
                    counter = Counter(values.astype(int))
                    results.append(counter.most_common(1)[0][0])
                else:
                    # Numeric statistic
                    if stat == 'mean':
                        results.append(np.mean(values))
                    elif stat == 'sum':
                        results.append(np.sum(values))
                    elif stat == 'max':
                        results.append(np.max(values))
                    elif stat == 'min':
                        results.append(np.min(values))
                    elif stat == 'std':
                        results.append(np.std(values))
                    else:
                        results.append(np.mean(values))
            
            except Exception as e:
                print(f"Warning: Failed for watershed {idx}: {e}")
                results.append(np.nan)
        
        return pd.Series(results, index=watershed_gdf.index)


def classify_lulc_distribution(watershed_gdf, lulc_path):
    """
    Calculate LULC class distribution for each watershed
    
    Returns DataFrame with percentage of each class
    """
    
    with rasterio.open(lulc_path) as src:
        lulc_raster = src.read(1)
        
        results = []
        
        for idx, row in watershed_gdf.iterrows():
            try:
                masked, _ = mask(src, [row.geometry], crop=True, nodata=0)
                values = masked[0]
                values = values[values > 0]
                
                if len(values) == 0:
                    results.append({'forest': 0, 'cropland': 0, 'urban': 0, 'water': 0, 'other': 0})
                    continue
                
                counter = Counter(values.astype(int))
                total = len(values)
                
                # ESA WorldCover classes (simplified)
                lulc_dist = {
                    'forest': sum(counter.get(c, 0) for c in [10, 20]) / total * 100,  # Tree cover
                    'cropland': counter.get(40, 0) / total * 100,
                    'urban': counter.get(50, 0) / total * 100,
                    'water': sum(counter.get(c, 0) for c in [80, 90, 95]) / total * 100,
                    'other': sum(counter.get(c, 0) for c in [30, 60, 70, 100]) / total * 100
                }
                
                results.append(lulc_dist)
            
            except Exception as e:
                print(f"Warning: Failed for watershed {idx}: {e}")
                results.append({'forest': 0, 'cropland': 0, 'urban': 0, 'water': 0, 'other': 0})
        
        return pd.DataFrame(results, index=watershed_gdf.index)


def main():
    print("="*70)
    print("WATERSHED CHARACTERIZATION")
    print("="*70)
    
    # Load watershed boundaries
    gdf = gpd.read_file("data/processed/stage4/watershed_boundaries_lucknow.shp")
    print(f"\nLoaded {len(gdf)} watersheds")
    
    # Extract statistics from various layers
    print("\nExtracting zonal statistics...")
    
    # 1. Groundwater potential (from ML model)
    print("  - Groundwater potential score...")
    gdf['gwp_mean'] = extract_zonal_stats(gdf, "data/processed/stage4/gwp_score_ml.tif", stat='mean')
    gdf['gwp_std'] = extract_zonal_stats(gdf, "data/processed/stage4/gwp_score_ml.tif", stat='std')
    
    # 2. Terrain
    print("  - Slope...")
    gdf['slope_mean'] = extract_zonal_stats(gdf, "data/processed/slope_lucknow.tif", stat='mean')
    gdf['slope_max'] = extract_zonal_stats(gdf, "data/processed/slope_lucknow.tif", stat='max')
    
    print("  - Elevation...")
    gdf['elevation_mean'] = extract_zonal_stats(gdf, "data/processed/dem_lucknow.tif", stat='mean')
    gdf['elevation_range'] = (
        extract_zonal_stats(gdf, "data/processed/dem_lucknow.tif", stat='max') -
        extract_zonal_stats(gdf, "data/processed/dem_lucknow.tif", stat='min')
    )
    
    # 3. Hydrology
    print("  - Drainage density...")
    gdf['drainage_dens'] = extract_zonal_stats(gdf, "data/processed/stage3/drainage_density_lucknow.tif", stat='mean')
    
    print("  - Stream length...")
    gdf['stream_length_km'] = extract_zonal_stats(gdf, "data/processed/stage3/stream_network_lucknow.tif", stat='sum') * 0.0125  # pixel to km
    
    # 4. Rainfall
    print("  - Rainfall...")
    gdf['rainfall_mm'] = extract_zonal_stats(gdf, "data/processed/rain_mean_lucknow.tif", stat='mean')
    
    # 5. LULC distribution
    print("  - Land use distribution...")
    lulc_dist = classify_lulc_distribution(gdf, "data/processed/lulc_lucknow.tif")
    gdf = pd.concat([gdf, lulc_dist], axis=1)
    
    # 6. Geology (if available)
    try:
        print("  - Geology...")
        gdf['geology_type'] = extract_zonal_stats(gdf, "data/processed/stage3/geology_lucknow.tif", categorical=True)
    except:
        print("    (Geology data not available - skipping)")
    
    # Save characterized watersheds
    output_path = "data/processed/stage4/watersheds_characterized.shp"
    gdf.to_file(output_path)
    print(f"\n✓ Saved: {output_path}")
    
    # Save as CSV for easy viewing
    csv_path = "data/processed/stage4/watersheds_characterized.csv"
    gdf.drop('geometry', axis=1).to_csv(csv_path, index=False)
    print(f"✓ Saved: {csv_path}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("CHARACTERIZATION SUMMARY")
    print("="*70)
    
    print(f"\nGroundwater Potential:")
    print(f"  Mean: {gdf['gwp_mean'].mean():.3f} (±{gdf['gwp_mean'].std():.3f})")
    print(f"  Range: {gdf['gwp_mean'].min():.3f} - {gdf['gwp_mean'].max():.3f}")
    
    print(f"\nSlope:")
    print(f"  Mean: {gdf['slope_mean'].mean():.2f}° (±{gdf['slope_mean'].std():.2f}°)")
    print(f"  Max slope: {gdf['slope_max'].max():.2f}°")
    
    print(f"\nLand Use (district average %):")
    print(f"  Forest: {lulc_dist['forest'].mean():.1f}%")
    print(f"  Cropland: {lulc_dist['cropland'].mean():.1f}%")
    print(f"  Urban: {lulc_dist['urban'].mean():.1f}%")
    print(f"  Water: {lulc_dist['water'].mean():.1f}%")
    

if __name__ == "__main__":
    main()
```

---

### Phase 3: Action Plan Generation (Week 3-4)

#### 3.1 Prioritize Watersheds

**New File:** `src/prioritize_watersheds.py`

```python
"""
Prioritize watersheds for intervention based on multiple criteria:

1. Groundwater stress (declining water levels)
2. Groundwater potential (room for improvement)
3. Population/demand
4. Feasibility (slope, soil, accessibility)
5. Cost-benefit ratio

Output: Ranked list of watersheds with recommended interventions
"""

import geopandas as gpd
import pandas as pd
import numpy as np

def calculate_priority_score(gdf):
    """
    Multi-criteria prioritization using weighted scoring
    
    Criteria:
    - Groundwater stress: 30%
    - Improvement potential: 25%
    - Population served: 20%
    - Feasibility: 15%
    - Cost-effectiveness: 10%
    """
    
    # Normalize all scores to 0-1 range
    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())
    
    # 1. Groundwater stress (higher = more stressed = higher priority)
    # Use water level decline rate if available, else use low GWP as proxy
    gdf['stress_score'] = 1 - normalize(gdf['gwp_mean'])  # Lower GWP = higher stress
    
    # 2. Improvement potential (moderate GWP = best potential)
    # Inverted U-shape: 0.3-0.7 range is ideal
    gdf['potential_score'] = 1 - abs(gdf['gwp_mean'] - 0.5) * 2
    
    # 3. Population served (estimate from area and LULC)
    # Urban/cropland areas likely have higher population
    gdf['population_proxy'] = (gdf['urban'] * 3 + gdf['cropland'] * 1) * gdf['area_km2']
    gdf['population_score'] = normalize(gdf['population_proxy'])
    
    # 4. Feasibility (gentle slopes, good soil, adequate stream density)
    feasibility_factors = []
    
    # Slope suitability (5-15° ideal for most structures)
    slope_suit = 1 - abs(gdf['slope_mean'] - 10) / 15
    slope_suit = slope_suit.clip(0, 1)
    feasibility_factors.append(slope_suit)
    
    # Drainage density (moderate is good)
    drain_suit = 1 - abs(normalize(gdf['drainage_dens']) - 0.5) * 2
    feasibility_factors.append(drain_suit)
    
    gdf['feasibility_score'] = sum(feasibility_factors) / len(feasibility_factors)
    
    # 5. Cost-effectiveness (smaller watersheds = cheaper interventions)
    gdf['cost_score'] = 1 - normalize(gdf['area_km2'])  # Smaller = higher score
    
    # Weighted combination
    weights = {
        'stress': 0.30,
        'potential': 0.25,
        'population': 0.20,
        'feasibility': 0.15,
        'cost': 0.10
    }
    
    gdf['priority_score'] = (
        gdf['stress_score'] * weights['stress'] +
        gdf['potential_score'] * weights['potential'] +
        gdf['population_score'] * weights['population'] +
        gdf['feasibility_score'] * weights['feasibility'] +
        gdf['cost_score'] * weights['cost']
    )
    
    # Classify into priority classes
    gdf['priority_class'] = pd.cut(
        gdf['priority_score'],
        bins=[0, 0.3, 0.6, 1.0],
        labels=['Low', 'Medium', 'High']
    )
    
    return gdf


def recommend_interventions(row):
    """
    Recommend specific interventions based on watershed characteristics
    
    Returns:
    --------
    dict with:
        - primary_intervention: Main recommendation
        - secondary_interventions: List of supporting activities
        - estimated_cost: Budget estimate (₹ lakhs)
        - expected_impact: Potential recharge increase (MCM/year)
    """
    
    recommendations = {
        'primary_intervention': '',
        'secondary_interventions': [],
        'estimated_cost_lakhs': 0,
        'expected_recharge_mcm': 0
    }
    
    # Decision tree based on characteristics
    
    # 1. Check dams (medium slope, good stream density, < 2 km²)
    if (5 <= row['slope_mean'] <= 15 and 
        row['stream_length_km'] > 2 and 
        row['area_km2'] < 2.0):
        
        n_check_dams = max(1, int(row['stream_length_km'] / 0.5))  # 1 per 500m stream
        recommendations['primary_intervention'] = f"Check Dams ({n_check_dams} nos)"
        recommendations['estimated_cost_lakhs'] = n_check_dams * 8  # ₹8 lakhs per dam
        recommendations['expected_recharge_mcm'] = n_check_dams * 0.05  # 50,000 m³ per dam
    
    # 2. Percolation tanks (gentle slope, cropland, larger area)
    elif (row['slope_mean'] < 5 and 
          row['cropland'] > 30 and 
          row['area_km2'] > 1.0):
        
        n_tanks = max(1, int(row['area_km2'] / 2))  # 1 per 2 km²
        recommendations['primary_intervention'] = f"Percolation Tanks ({n_tanks} nos)"
        recommendations['estimated_cost_lakhs'] = n_tanks * 15  # ₹15 lakhs per tank
        recommendations['expected_recharge_mcm'] = n_tanks * 0.1  # 100,000 m³ per tank
    
    # 3. Recharge wells (urban areas, high GWP, flat terrain)
    elif (row['urban'] > 20 and 
          row['gwp_mean'] > 0.5 and 
          row['slope_mean'] < 3):
        
        n_wells = max(2, int(row['urban'] / 10))  # 1 per 10% urban
        recommendations['primary_intervention'] = f"Recharge Wells ({n_wells} nos)"
        recommendations['estimated_cost_lakhs'] = n_wells * 2.5  # ₹2.5 lakhs per well
        recommendations['expected_recharge_mcm'] = n_wells * 0.02  # 20,000 m³ per well
    
    # 4. Farm ponds (cropland dominant, moderate slope)
    elif row['cropland'] > 50:
        n_ponds = max(1, int(row['cropland'] / 20))
        recommendations['primary_intervention'] = f"Farm Ponds ({n_ponds} nos)"
        recommendations['estimated_cost_lakhs'] = n_ponds * 5  # ₹5 lakhs per pond
        recommendations['expected_recharge_mcm'] = n_ponds * 0.03
    
    # 5. Reforestation (degraded watersheds, low GWP)
    else:
        area_ha = row['area_km2'] * 100
        recommendations['primary_intervention'] = f"Reforestation ({area_ha:.0f} ha)"
        recommendations['estimated_cost_lakhs'] = area_ha * 0.5  # ₹50k per ha
        recommendations['expected_recharge_mcm'] = area_ha * 0.001  # Long-term benefit
    
    # Secondary interventions (always recommended)
    if row['forest'] < 10:
        recommendations['secondary_interventions'].append("Increase green cover (target 20%)")
    
    if row['urban'] > 30:
        recommendations['secondary_interventions'].append("Rainwater harvesting mandate")
    
    if row['slope_mean'] > 10:
        recommendations['secondary_interventions'].append("Soil conservation measures")
    
    return pd.Series(recommendations)


def main():
    print("="*70)
    print("WATERSHED PRIORITIZATION & ACTION PLAN")
    print("="*70)
    
    # Load characterized watersheds
    gdf = gpd.read_file("data/processed/stage4/watersheds_characterized.shp")
    print(f"\nLoaded {len(gdf)} watersheds")
    
    # Calculate priority scores
    print("\nCalculating priority scores...")
    gdf = calculate_priority_score(gdf)
    
    # Recommend interventions
    print("Generating intervention recommendations...")
    interventions = gdf.apply(recommend_interventions, axis=1)
    gdf = pd.concat([gdf, interventions], axis=1)
    
    # Sort by priority
    gdf = gdf.sort_values('priority_score', ascending=False).reset_index(drop=True)
    gdf['rank'] = range(1, len(gdf) + 1)
    
    # Save prioritized watersheds
    output_shp = "data/processed/stage4/watersheds_prioritized.shp"
    gdf.to_file(output_shp)
    print(f"\n✓ Saved: {output_shp}")
    
    output_csv = "data/processed/stage4/watersheds_prioritized.csv"
    gdf.drop('geometry', axis=1).to_csv(output_csv, index=False)
    print(f"✓ Saved: {output_csv}")
    
    # Generate summary report
    print("\n" + "="*70)
    print("PRIORITIZATION SUMMARY")
    print("="*70)
    
    print(f"\nPriority Distribution:")
    print(gdf['priority_class'].value_counts().to_string())
    
    print(f"\nTop 10 Priority Watersheds:")
    top10 = gdf.head(10)[['rank', 'watershed_id', 'priority_score', 'priority_class', 
                          'primary_intervention', 'estimated_cost_lakhs', 'area_km2']]
    print(top10.to_string(index=False))
    
    print(f"\nIntervention Type Distribution:")
    intervention_counts = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
    print(intervention_counts.to_string())
    
    print(f"\nBudget Summary:")
    total_cost = gdf['estimated_cost_lakhs'].sum()
    total_recharge = gdf['expected_recharge_mcm'].sum()
    print(f"  Total estimated cost: ₹{total_cost:.2f} crores")
    print(f"  Expected recharge increase: {total_recharge:.2f} MCM/year")
    print(f"  Cost per MCM: ₹{total_cost * 10 / total_recharge:.2f} lakhs")
    
    # Generate action plan for top priorities
    print("\n" + "="*70)
    print("IMMEDIATE ACTION PLAN (Top 5 Watersheds)")
    print("="*70)
    
    for idx, row in gdf.head(5).iterrows():
        print(f"\n{idx+1}. Watershed ID: {row['watershed_id']} (Priority: {row['priority_class']})")
        print(f"   Location: {row['centroid_lat']:.4f}°N, {row['centroid_lon']:.4f}°E")
        print(f"   Area: {row['area_km2']:.2f} km²")
        print(f"   Primary Intervention: {row['primary_intervention']}")
        print(f"   Estimated Cost: ₹{row['estimated_cost_lakhs']:.2f} lakhs")
        print(f"   Expected Impact: {row['expected_recharge_mcm']:.3f} MCM/year")
        if row['secondary_interventions']:
            print(f"   Secondary:")
            for intervention in row['secondary_interventions']:
                print(f"      - {intervention}")


if __name__ == "__main__":
    main()
```

---

#### 3.2 Generate Official Reports

**New File:** `src/generate_watershed_reports.py`

```python
"""
Generate actionable reports for district/block officials

Outputs:
1. Executive Summary PDF
2. Watershed-wise action plans (Excel)
3. Budget allocation table
4. Implementation timeline (Gantt chart)
5. GIS maps for field teams
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def create_executive_summary_pdf(gdf, output_pdf="reports/Executive_Summary.pdf"):
    """
    Create multi-page PDF report for officials
    """
    
    with PdfPages(output_pdf) as pdf:
        
        # Page 1: Title & Overview
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.5, 0.9, "LUCKNOW DISTRICT", ha='center', fontsize=24, weight='bold')
        fig.text(0.5, 0.85, "Micro-Watershed Action Plan 2025-26", ha='center', fontsize=18)
        fig.text(0.5, 0.80, f"Total Watersheds: {len(gdf)}", ha='center', fontsize=14)
        
        # Key statistics
        stats_text = f"""
        SUMMARY STATISTICS
        
        District Coverage: {gdf['area_km2'].sum():.2f} km²
        
        Watersheds by Priority:
          • High Priority: {(gdf['priority_class'] == 'High').sum()} watersheds
          • Medium Priority: {(gdf['priority_class'] == 'Medium').sum()} watersheds
          • Low Priority: {(gdf['priority_class'] == 'Low').sum()} watersheds
        
        Total Budget Estimate: ₹{gdf['estimated_cost_lakhs'].sum() / 100:.2f} Crores
        
        Expected Annual Recharge: {gdf['expected_recharge_mcm'].sum():.2f} MCM
        
        Recommended Interventions:
        """
        
        fig.text(0.1, 0.65, stats_text, fontsize=12, verticalalignment='top', family='monospace')
        
        # Intervention breakdown
        interventions = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
        y_pos = 0.30
        for intervention, count in interventions.items():
            fig.text(0.15, y_pos, f"  • {intervention}: {count} watersheds", fontsize=11)
            y_pos -= 0.03
        
        plt.axis('off')
        pdf.savefig(fig)
        plt.close()
        
        # Page 2: Priority Map
        fig, ax = plt.subplots(figsize=(8.5, 11))
        
        # Color by priority
        colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        gdf.plot(column='priority_class', ax=ax, legend=True, 
                cmap='RdYlGn_r', edgecolor='black', linewidth=0.5)
        
        ax.set_title("Watershed Priority Map", fontsize=16, weight='bold')
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor=colors['High'], label='High Priority'),
            mpatches.Patch(facecolor=colors['Medium'], label='Medium Priority'),
            mpatches.Patch(facecolor=colors['Low'], label='Low Priority')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()
        
        # Page 3: Top 20 Priority Watersheds Table
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        top20 = gdf.head(20)[['rank', 'watershed_id', 'area_km2', 'priority_class',
                              'primary_intervention', 'estimated_cost_lakhs']]
        
        table_data = []
        table_data.append(['Rank', 'ID', 'Area\n(km²)', 'Priority', 'Intervention', 'Cost\n(₹ lakhs)'])
        
        for _, row in top20.iterrows():
            table_data.append([
                f"{row['rank']}",
                f"{row['watershed_id']}",
                f"{row['area_km2']:.2f}",
                row['priority_class'],
                row['primary_intervention'][:25],  # Truncate
                f"{row['estimated_cost_lakhs']:.1f}"
            ])
        
        table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                        colWidths=[0.08, 0.08, 0.12, 0.12, 0.40, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Header row styling
        for i in range(6):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title("Top 20 Priority Watersheds for Immediate Action", 
                    fontsize=14, weight='bold', pad=20)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
    print(f"✓ Executive Summary PDF created: {output_pdf}")


def create_action_plan_excel(gdf, output_excel="reports/Watershed_Action_Plans.xlsx"):
    """
    Create detailed Excel workbook with multiple sheets
    """
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        
        # Sheet 1: Summary
        summary = pd.DataFrame({
            'Metric': [
                'Total Watersheds',
                'High Priority',
                'Medium Priority',
                'Low Priority',
                'Total Area (km²)',
                'Total Budget (₹ Crores)',
                'Expected Recharge (MCM/year)',
                'Average Cost per Watershed (₹ lakhs)'
            ],
            'Value': [
                len(gdf),
                (gdf['priority_class'] == 'High').sum(),
                (gdf['priority_class'] == 'Medium').sum(),
                (gdf['priority_class'] == 'Low').sum(),
                gdf['area_km2'].sum(),
                gdf['estimated_cost_lakhs'].sum() / 100,
                gdf['expected_recharge_mcm'].sum(),
                gdf['estimated_cost_lakhs'].mean()
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: All Watersheds (sorted by priority)
        ws_df = gdf.drop('geometry', axis=1)[[
            'rank', 'watershed_id', 'area_km2', 'priority_score', 'priority_class',
            'gwp_mean', 'slope_mean', 'rainfall_mm', 'cropland', 'urban',
            'primary_intervention', 'estimated_cost_lakhs', 'expected_recharge_mcm',
            'centroid_lat', 'centroid_lon'
        ]]
        ws_df.to_excel(writer, sheet_name='All Watersheds', index=False)
        
        # Sheet 3: High Priority Only
        high_priority = ws_df[ws_df['priority_class'] == 'High']
        high_priority.to_excel(writer, sheet_name='High Priority', index=False)
        
        # Sheet 4: Budget Allocation by Block (placeholder - needs block boundary data)
        # For now, group by area quadrants
        gdf['quadrant'] = pd.cut(gdf['centroid_lat'], bins=4, labels=['North', 'Central-North', 'Central-South', 'South'])
        
        budget_by_area = gdf.groupby('quadrant').agg({
            'watershed_id': 'count',
            'area_km2': 'sum',
            'estimated_cost_lakhs': 'sum',
            'expected_recharge_mcm': 'sum'
        }).rename(columns={
            'watershed_id': 'Number of Watersheds',
            'area_km2': 'Total Area (km²)',
            'estimated_cost_lakhs': 'Budget (₹ lakhs)',
            'expected_recharge_mcm': 'Expected Recharge (MCM)'
        })
        
        budget_by_area.to_excel(writer, sheet_name='Budget by Area')
        
        # Sheet 5: Implementation Timeline
        timeline = pd.DataFrame({
            'Watershed ID': gdf.head(20)['watershed_id'],
            'Priority': gdf.head(20)['priority_class'],
            'Intervention': gdf.head(20)['primary_intervention'],
            'Start Month': ['April 2025'] * 20,
            'Duration (months)': [6] * 20,  # Simplified
            'Responsible Officer': ['Block Development Officer'] * 20,
            'Status': ['Proposed'] * 20
        })
        timeline.to_excel(writer, sheet_name='Timeline', index=False)
    
    print(f"✓ Action Plan Excel created: {output_excel}")


def main():
    print("="*70)
    print("GENERATING OFFICIAL REPORTS")
    print("="*70)
    
    # Load prioritized watersheds
    gdf = gpd.read_file("data/processed/stage4/watersheds_prioritized.shp")
    print(f"\nLoaded {len(gdf)} watersheds")
    
    # Create output directory
    import os
    os.makedirs("reports", exist_ok=True)
    
    # Generate PDF report
    print("\nCreating executive summary PDF...")
    create_executive_summary_pdf(gdf)
    
    # Generate Excel workbook
    print("Creating detailed action plan Excel...")
    create_action_plan_excel(gdf)
    
    print("\n" + "="*70)
    print("REPORTS GENERATED SUCCESSFULLY!")
    print("="*70)
    print("\nOutputs:")
    print("  1. reports/Executive_Summary.pdf (for presentations)")
    print("  2. reports/Watershed_Action_Plans.xlsx (detailed planning)")
    print("\nNext Steps:")
    print("  1. Share with District Magistrate / Collector")
    print("  2. Present to Block Development Officers")
    print("  3. Allocate budget and assign responsibilities")
    print("  4. Begin field surveys for top 10 priority watersheds")


if __name__ == "__main__":
    main()
```

---

### Phase 4: Integration with Existing System (Week 5)

#### 4.1 Update Pipeline

**File:** `run_complete_pipeline.py` (update)

Add watershed delineation stages:

```python
# After Stage 3 (features extraction)

print("\n" + "="*70)
print("STAGE 4A: WATERSHED DELINEATION")
print("="*70)
subprocess.run(["python", "src/delineate_watersheds.py"], check=True)

print("\n" + "="*70)
print("STAGE 4B: WATERSHED CHARACTERIZATION")
print("="*70)
subprocess.run(["python", "src/characterize_watersheds.py"], check=True)

print("\n" + "="*70)
print("STAGE 4C: PRIORITIZATION & ACTION PLANNING")
print("="*70)
subprocess.run(["python", "src/prioritize_watersheds.py"], check=True)

print("\n" + "="*70)
print("STAGE 4D: REPORT GENERATION")
print("="*70)
subprocess.run(["python", "src/generate_watershed_reports.py"], check=True)
```

---

#### 4.2 Update Streamlit App

**File:** `app/pages/05_Watershed_Management.py` (new)

```python
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Watershed Management", layout="wide")

st.title("🌊 Watershed Management Dashboard")

# Load data
@st.cache_data
def load_watersheds():
    gdf = gpd.read_file("data/processed/stage4/watersheds_prioritized.shp")
    return gdf

gdf = load_watersheds()

# Sidebar filters
st.sidebar.header("Filters")
priority_filter = st.sidebar.multiselect(
    "Priority Class",
    options=['High', 'Medium', 'Low'],
    default=['High', 'Medium', 'Low']
)

area_range = st.sidebar.slider(
    "Watershed Area (km²)",
    min_value=float(gdf['area_km2'].min()),
    max_value=float(gdf['area_km2'].max()),
    value=(float(gdf['area_km2'].min()), float(gdf['area_km2'].max()))
)

# Filter data
filtered = gdf[
    (gdf['priority_class'].isin(priority_filter)) &
    (gdf['area_km2'] >= area_range[0]) &
    (gdf['area_km2'] <= area_range[1])
]

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Watersheds", len(filtered))

with col2:
    st.metric("High Priority", (filtered['priority_class'] == 'High').sum())

with col3:
    total_cost = filtered['estimated_cost_lakhs'].sum() / 100
    st.metric("Total Budget", f"₹{total_cost:.2f} Cr")

with col4:
    total_recharge = filtered['expected_recharge_mcm'].sum()
    st.metric("Expected Recharge", f"{total_recharge:.2f} MCM")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📍 Map View", "📊 Statistics", "📋 Action Plans", "💰 Budget"])

with tab1:
    st.subheader("Watershed Priority Map")
    
    # Interactive map using plotly
    fig = px.choropleth_mapbox(
        filtered,
        geojson=filtered.geometry,
        locations=filtered.index,
        color='priority_score',
        hover_name='watershed_id',
        hover_data=['area_km2', 'primary_intervention', 'estimated_cost_lakhs'],
        mapbox_style="open-street-map",
        zoom=9,
        center={"lat": filtered.centroid.y.mean(), "lon": filtered.centroid.x.mean()},
        opacity=0.6,
        color_continuous_scale="RdYlGn"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Watershed Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution pie chart
        priority_counts = filtered['priority_class'].value_counts()
        fig_pie = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="Priority Distribution",
            color=priority_counts.index,
            color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Intervention type distribution
        interventions = filtered['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
        fig_bar = px.bar(
            x=interventions.values,
            y=interventions.index,
            orientation='h',
            title="Recommended Interventions",
            labels={'x': 'Number of Watersheds', 'y': 'Intervention Type'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Scatter: Cost vs Impact
    st.subheader("Cost-Benefit Analysis")
    fig_scatter = px.scatter(
        filtered,
        x='estimated_cost_lakhs',
        y='expected_recharge_mcm',
        size='area_km2',
        color='priority_class',
        hover_name='watershed_id',
        labels={
            'estimated_cost_lakhs': 'Estimated Cost (₹ lakhs)',
            'expected_recharge_mcm': 'Expected Recharge (MCM/year)'
        },
        title="Cost vs. Expected Impact"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Top Priority Action Plans")
    
    # Display top 20 watersheds
    top20 = filtered.head(20).drop('geometry', axis=1)[[
        'rank', 'watershed_id', 'area_km2', 'priority_class',
        'primary_intervention', 'estimated_cost_lakhs', 'expected_recharge_mcm'
    ]]
    
    st.dataframe(top20, use_container_width=True)
    
    # Detailed view for selected watershed
    st.subheader("Detailed Watershed View")
    selected_ws = st.selectbox("Select Watershed", filtered['watershed_id'].values)
    
    ws_row = filtered[filtered['watershed_id'] == selected_ws].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Information**")
        st.write(f"- Rank: {ws_row['rank']}")
        st.write(f"- Area: {ws_row['area_km2']:.2f} km²")
        st.write(f"- Priority: {ws_row['priority_class']}")
        st.write(f"- Location: {ws_row['centroid_lat']:.4f}°N, {ws_row['centroid_lon']:.4f}°E")
        
        st.write("**Physical Characteristics**")
        st.write(f"- Mean Slope: {ws_row['slope_mean']:.2f}°")
        st.write(f"- Rainfall: {ws_row['rainfall_mm']:.0f} mm")
        st.write(f"- GW Potential: {ws_row['gwp_mean']:.3f}")
    
    with col2:
        st.write("**Recommended Intervention**")
        st.write(f"- Primary: {ws_row['primary_intervention']}")
        st.write(f"- Estimated Cost: ₹{ws_row['estimated_cost_lakhs']:.2f} lakhs")
        st.write(f"- Expected Recharge: {ws_row['expected_recharge_mcm']:.3f} MCM/year")
        
        st.write("**Land Use**")
        st.write(f"- Forest: {ws_row['forest']:.1f}%")
        st.write(f"- Cropland: {ws_row['cropland']:.1f}%")
        st.write(f"- Urban: {ws_row['urban']:.1f}%")

with tab4:
    st.subheader("Budget Allocation")
    
    # Budget summary
    total_budget = filtered['estimated_cost_lakhs'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_budget = filtered[filtered['priority_class'] == 'High']['estimated_cost_lakhs'].sum()
        st.metric("High Priority Budget", f"₹{high_budget/100:.2f} Cr")
    
    with col2:
        med_budget = filtered[filtered['priority_class'] == 'Medium']['estimated_cost_lakhs'].sum()
        st.metric("Medium Priority Budget", f"₹{med_budget/100:.2f} Cr")
    
    with col3:
        low_budget = filtered[filtered['priority_class'] == 'Low']['estimated_cost_lakhs'].sum()
        st.metric("Low Priority Budget", f"₹{low_budget/100:.2f} Cr")
    
    # Budget by intervention type
    budget_by_intervention = filtered.groupby(
        filtered['primary_intervention'].str.extract(r'(.*?)\s*\(')[0]
    )['estimated_cost_lakhs'].sum().sort_values(ascending=False)
    
    fig_budget = px.bar(
        x=budget_by_intervention.values,
        y=budget_by_intervention.index,
        orientation='h',
        title="Budget Distribution by Intervention Type",
        labels={'x': 'Budget (₹ lakhs)', 'y': 'Intervention Type'}
    )
    st.plotly_chart(fig_budget, use_container_width=True)
    
    # Download reports
    st.subheader("Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Executive Summary (PDF)"):
            st.info("PDF generation in progress...")
            # Trigger PDF generation
    
    with col2:
        if st.button("Download Action Plans (Excel)"):
            st.info("Excel generation in progress...")
            # Trigger Excel generation
```

---

## 📊 Expected Outputs

### 1. Spatial Data Products

| File | Type | Description |
|------|------|-------------|
| `watersheds_lucknow.tif` | Raster | Watershed ID for each pixel |
| `watershed_boundaries_lucknow.shp` | Vector | Polygon boundaries |
| `pour_points_lucknow.shp` | Vector | Outlet locations |
| `watersheds_prioritized.shp` | Vector | With all attributes + rankings |

### 2. Tabular Reports

| File | Format | Audience |
|------|--------|----------|
| `watershed_attributes.csv` | CSV | Technical teams |
| `watersheds_characterized.csv` | CSV | Analysis |
| `watersheds_prioritized.csv` | CSV | Decision makers |
| `Watershed_Action_Plans.xlsx` | Excel | Block officials |

### 3. Visual Reports

| File | Format | Audience |
|------|--------|----------|
| `Executive_Summary.pdf` | PDF | District Collector, Politicians |
| Priority maps (PNG/PDF) | Image | Presentations |
| Budget charts | Image/Interactive | Finance department |

---

## 🎯 Success Criteria

### Technical Validation
- ✅ Watershed boundaries match stream network topology
- ✅ Pour points located at convergence zones
- ✅ Area distribution: 80%+ watersheds in 0.5-5 km² range
- ✅ No overlapping watersheds
- ✅ 100% coverage of district area

### Actionability for Officials
- ✅ Each watershed has specific intervention recommendation
- ✅ Cost estimates within ±20% accuracy
- ✅ GPS coordinates for field verification
- ✅ Priority ranking based on data-driven criteria
- ✅ Implementation timeline feasible (6-12 months)

### Integration with Groundwater Prediction
- ✅ GWP scores used in prioritization
- ✅ Structure site selection uses GWP + slope + hydrology
- ✅ Expected recharge estimates tied to GWP improvement potential

---

## 📅 Implementation Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Watershed delineation | Boundaries + pour points |
| 2 | Characterization | Zonal statistics for all layers |
| 3 | Prioritization | Ranked list with scores |
| 4 | Action planning | Intervention recommendations |
| 5 | Report generation | PDF + Excel outputs |
| 6 | Streamlit integration | Interactive dashboard |

**Total:** 6 weeks to fully functional watershed management system

---

## 🔄 How This Changes the Project

### Before (Groundwater Only):
```
DEM → Features → ML Model → Pixel Predictions → "This pixel has high GWP"
```

### After (Watershed + Groundwater):
```
DEM → Drainage → Watersheds (polygons)
              ↓
          Features → ML Model → Pixel Predictions
              ↓
    Zonal Stats → Watershed Characterization
              ↓
         Prioritization → Specific Interventions
              ↓
     Action Plans for Officials → "Build 3 check dams in Watershed #23"
```

---

## 💡 Key Benefits

1. **Administrative Alignment**: Watersheds are natural planning units
2. **Actionable Outputs**: Specific structures at specific locations
3. **Budget Planning**: Cost estimates per watershed
4. **Responsibility Assignment**: Each watershed → one Block officer
5. **Scalability**: Template for all 75 UP districts
6. **Policy Compatibility**: Matches IWMP, PMKSY, ABY frameworks
7. **Groundwater Integration**: GWP used for prioritization

---

## 🚀 Next Steps

**Immediate:**
1. Approve this restructure plan
2. Update project README.md
3. Begin implementation (Week 1)

**Short-term (6 weeks):**
1. Complete all code modules
2. Test on Lucknow district
3. Generate pilot reports

**Long-term (3 months):**
1. Present to UP Groundwater Department
2. Pilot in 2-3 districts
3. Scale to entire state

---

**This restructure transforms Watershed-UP from a "prediction tool" into a complete "decision support system" for watershed-based groundwater management! 🎯**
