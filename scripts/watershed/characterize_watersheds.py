#!/usr/bin/env python
"""
src/characterize_watersheds.py

Extract watershed-level statistics from raster layers.

For each watershed polygon, computes:
- Groundwater potential (mean, std from ML model prediction)
- Terrain (slope mean/max, elevation mean/range)
- Hydrology (drainage density, stream length)
- Climate (rainfall)
- Land use distribution (forest, cropland, urban, water percentages)
- Geology type (if available)

Outputs (data/processed/stage4/):
 - watersheds_characterized.shp : Shapefile with all attributes
 - watersheds_characterized.csv : CSV table for analysis

Usage:
    python src/characterize_watersheds.py

Prerequisites:
    - src/delineate_watersheds.py (watershed boundaries)
    - ML model predictions (gwp_score_ml.tif) OR AHP scores
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd

# Set GDAL_DATA before importing geopandas (fixes GDAL warnings)
if 'GDAL_DATA' not in os.environ:
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if conda_prefix:
        gdal_data = os.path.join(conda_prefix, 'Library', 'share', 'gdal')
        if os.path.exists(gdal_data):
            os.environ['GDAL_DATA'] = gdal_data

import geopandas as gpd
from rasterstats import zonal_stats
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

from path_config import (
    VECTORS_DIR, TABLES_DIR, RASTERS_DIR,
    WATERSHEDS_CHARACTERIZED, SLOPE, DEM, LULC, RAINFALL,
    DRAINAGE_DENSITY, STREAM_NETWORK, GWP_AHP, NDVI
)

# Paths
WATERSHEDS_FILE = str(VECTORS_DIR / "watershed_boundaries_lucknow.shp")
OUT_DIR = str(VECTORS_DIR)

# Input raster layers
SLOPE_FILE = str(SLOPE)
DEM_FILE = str(DEM)
LULC_FILE = str(LULC)
RAINFALL_FILE = str(RAINFALL)
DRAINAGE_DENS_FILE = str(DRAINAGE_DENSITY)
STREAM_FILE = str(STREAM_NETWORK)

# Groundwater potential (try ML first, fallback to AHP)
GWP_ML_FILE = str(RASTERS_DIR / "gwp_score_ml.tif")
GWP_AHP_FILE = str(GWP_AHP)

# Optional layers
GEOLOGY_FILE = str(RASTERS_DIR / "geology_lucknow.tif")
NDVI_FILE = str(NDVI)

# Outputs
OUT_SHP = str(WATERSHEDS_CHARACTERIZED).replace('.shp', '_output.shp')
OUT_CSV = str(TABLES_DIR / "watersheds_characterized.csv")


def extract_zonal_stats_simple(gdf, raster_path, stat='mean'):
    """
    Extract zonal statistics from raster for each watershed polygon using rasterstats
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        Watershed polygons
    raster_path : str
        Path to raster file
    stat : str
        Statistic to compute ('mean', 'sum', 'max', 'min', 'std')
    
    Returns:
    --------
    Series with statistics for each polygon
    """
    
    if not os.path.exists(raster_path):
        print(f"  ⚠ Raster not found: {raster_path}")
        return pd.Series([np.nan] * len(gdf), index=gdf.index)
    
    print(f"  Reading: {os.path.basename(raster_path)}")
    
    try:
        # Use rasterstats to compute zonal statistics
        stats = zonal_stats(
            gdf.geometry,
            raster_path,
            stats=[stat],
            nodata=-9999,
            all_touched=True
        )
        
        # Extract the requested statistic
        results = [s[stat] if s and s[stat] is not None else np.nan for s in stats]
        
        return pd.Series(results, index=gdf.index)
        
    except Exception as e:
        print(f"  ⚠ Error computing zonal stats: {e}")
        return pd.Series([np.nan] * len(gdf), index=gdf.index)


def classify_lulc_distribution(gdf, lulc_path):
    """
    Calculate land use distribution (%) for each watershed using rasterstats
    
    LULC Classes (assumed):
    1 = Forest
    2 = Cropland
    3 = Urban/Built-up
    4 = Water bodies
    5 = Other/Barren
    
    Returns GeoDataFrame with added columns: forest, cropland, urban, water, other (all in %)
    """
    
    if not os.path.exists(lulc_path):
        print(f"  ⚠ LULC raster not found: {lulc_path}")
        gdf['forest'] = 0
        gdf['cropland'] = 0
        gdf['urban'] = 0
        gdf['water'] = 0
        gdf['other'] = 0
        return gdf
    
    print(f"\n  Classifying land use distribution from: {os.path.basename(lulc_path)}")
    
    # Initialize columns
    lulc_cols = ['forest', 'cropland', 'urban', 'water', 'other']
    for col in lulc_cols:
        gdf[col] = 0.0
    
    try:
        # Use rasterstats to get categorical statistics
        stats = zonal_stats(
            gdf.geometry,
            lulc_path,
            categorical=True,
            nodata=-9999,
            all_touched=True
        )
        
        for idx, stat_dict in enumerate(stats):
            if stat_dict:
                # Count total pixels
                total_pixels = sum(stat_dict.values())
                
                if total_pixels > 0:
                    # Calculate percentages (adjust class numbers based on your LULC scheme)
                    gdf.at[idx, 'forest'] = (stat_dict.get(1, 0) / total_pixels) * 100
                    gdf.at[idx, 'cropland'] = (stat_dict.get(2, 0) / total_pixels) * 100
                    gdf.at[idx, 'urban'] = (stat_dict.get(3, 0) / total_pixels) * 100
                    gdf.at[idx, 'water'] = (stat_dict.get(4, 0) / total_pixels) * 100
                    gdf.at[idx, 'other'] = (stat_dict.get(5, 0) / total_pixels) * 100
        
        print(f"    ✓ Classified {len(gdf)} watersheds")
        
    except Exception as e:
        print(f"  ⚠ Error classifying LULC: {e}")
    
    return gdf


def calculate_stream_length(gdf, stream_path):
    """
    Calculate total stream length (km) within each watershed
    
    Stream raster has 1=stream, 0=no stream
    We count stream pixels and convert to km
    """
    
    if not os.path.exists(stream_path):
        print(f"  ⚠ Stream network not found: {stream_path}")
        return pd.Series([0.0] * len(gdf), index=gdf.index)
    
    print(f"  Calculating stream length from: {os.path.basename(stream_path)}")
    
    try:
        # Get sum of stream pixels (1s)
        stats = zonal_stats(
            gdf.geometry,
            stream_path,
            stats=['sum'],
            nodata=0,
            all_touched=True
        )
        
        # Convert pixel count to km (assuming 12.5m resolution)
        pixel_size_m = 12.5
        results = []
        
        for s in stats:
            if s and s['sum'] is not None:
                stream_pixels = s['sum']
                stream_km = (stream_pixels * pixel_size_m) / 1000.0
                results.append(stream_km)
            else:
                results.append(0.0)
        
        return pd.Series(results, index=gdf.index)
        
    except Exception as e:
        print(f"  ⚠ Error calculating stream length: {e}")
        return pd.Series([0.0] * len(gdf), index=gdf.index)


def main():
    print("="*70)
    print("WATERSHED CHARACTERIZATION")
    print("="*70)
    
    # Check prerequisites
    if not os.path.exists(WATERSHEDS_FILE):
        print(f"\n❌ Watershed boundaries not found: {WATERSHEDS_FILE}")
        print("\nPlease run delineate_watersheds_grid.py first!")
        print("  Command: python src/delineate_watersheds_grid.py")
        return
    
    # Load watersheds
    print(f"\nLoading watershed boundaries from: {WATERSHEDS_FILE}")
    gdf = gpd.read_file(WATERSHEDS_FILE)
    print(f"  Loaded {len(gdf)} watersheds")
    print(f"  CRS: {gdf.crs}")
    
    # 1. GROUNDWATER POTENTIAL
    print("\n" + "="*70)
    print("1. EXTRACTING GROUNDWATER POTENTIAL")
    print("="*70)
    
    # Try ML predictions first, fallback to AHP
    if os.path.exists(GWP_ML_FILE):
        print("  Using ML model predictions")
        gdf['gwp_mean'] = extract_zonal_stats_simple(gdf, GWP_ML_FILE, 'mean')
        gdf['gwp_std'] = extract_zonal_stats_simple(gdf, GWP_ML_FILE, 'std')
    elif os.path.exists(GWP_AHP_FILE):
        print("  Using AHP scores (ML predictions not found)")
        gdf['gwp_mean'] = extract_zonal_stats_simple(gdf, GWP_AHP_FILE, 'mean')
        gdf['gwp_std'] = extract_zonal_stats_simple(gdf, GWP_AHP_FILE, 'std')
    else:
        print("  ⚠ Neither ML nor AHP groundwater scores found!")
        gdf['gwp_mean'] = np.nan
        gdf['gwp_std'] = np.nan
    
    print(f"\n  GWP Statistics:")
    print(f"    Mean GWP: {gdf['gwp_mean'].mean():.3f} (±{gdf['gwp_mean'].std():.3f})")
    print(f"    Range: {gdf['gwp_mean'].min():.3f} - {gdf['gwp_mean'].max():.3f}")
    
    # 2. TERRAIN CHARACTERISTICS
    print("\n" + "="*70)
    print("2. EXTRACTING TERRAIN CHARACTERISTICS")
    print("="*70)
    
    # Slope
    gdf['slope_mean'] = extract_zonal_stats_simple(gdf, SLOPE_FILE, 'mean')
    gdf['slope_max'] = extract_zonal_stats_simple(gdf, SLOPE_FILE, 'max')
    
    # Elevation
    gdf['elev_mean'] = extract_zonal_stats_simple(gdf, DEM_FILE, 'mean')
    gdf['elev_min'] = extract_zonal_stats_simple(gdf, DEM_FILE, 'min')
    gdf['elev_max'] = extract_zonal_stats_simple(gdf, DEM_FILE, 'max')
    gdf['elev_range'] = gdf['elev_max'] - gdf['elev_min']
    
    print(f"\n  Terrain Statistics:")
    print(f"    Mean slope: {gdf['slope_mean'].mean():.2f}° (max: {gdf['slope_max'].max():.2f}°)")
    print(f"    Mean elevation: {gdf['elev_mean'].mean():.1f}m")
    print(f"    Elevation range: {gdf['elev_range'].mean():.1f}m")
    
    # 3. HYDROLOGICAL FEATURES
    print("\n" + "="*70)
    print("3. EXTRACTING HYDROLOGICAL FEATURES")
    print("="*70)
    
    # Drainage density
    gdf['drain_dens'] = extract_zonal_stats_simple(gdf, DRAINAGE_DENS_FILE, 'mean')
    
    # Stream length
    gdf['stream_km'] = calculate_stream_length(gdf, STREAM_FILE)
    
    print(f"\n  Hydrology Statistics:")
    print(f"    Mean drainage density: {gdf['drain_dens'].mean():.3f} km/km²")
    print(f"    Total stream length: {gdf['stream_km'].sum():.2f} km")
    print(f"    Avg stream per watershed: {gdf['stream_km'].mean():.2f} km")
    
    # 4. CLIMATE
    print("\n" + "="*70)
    print("4. EXTRACTING CLIMATE DATA")
    print("="*70)
    
    gdf['rainfall'] = extract_zonal_stats_simple(gdf, RAINFALL_FILE, 'mean')
    
    print(f"\n  Climate Statistics:")
    print(f"    Mean annual rainfall: {gdf['rainfall'].mean():.1f} mm")
    print(f"    Range: {gdf['rainfall'].min():.1f} - {gdf['rainfall'].max():.1f} mm")
    
    # 5. LAND USE DISTRIBUTION
    print("\n" + "="*70)
    print("5. CLASSIFYING LAND USE DISTRIBUTION")
    print("="*70)
    
    gdf = classify_lulc_distribution(gdf, LULC_FILE)
    
    print(f"\n  LULC Statistics (District Average):")
    print(f"    Forest: {gdf['forest'].mean():.1f}%")
    print(f"    Cropland: {gdf['cropland'].mean():.1f}%")
    print(f"    Urban: {gdf['urban'].mean():.1f}%")
    print(f"    Water: {gdf['water'].mean():.1f}%")
    print(f"    Other: {gdf['other'].mean():.1f}%")
    
    # 6. OPTIONAL: GEOLOGY & NDVI
    print("\n" + "="*70)
    print("6. EXTRACTING OPTIONAL LAYERS (if available)")
    print("="*70)
    
    if os.path.exists(GEOLOGY_FILE):
        # For categorical data, use mode (most common)
        print(f"  Extracting geology type...")
        stats = zonal_stats(gdf.geometry, GEOLOGY_FILE, categorical=True, nodata=-9999)
        geology_mode = []
        for s in stats:
            if s:
                # Get most common value
                mode_val = max(s.items(), key=lambda x: x[1])[0] if s else np.nan
                geology_mode.append(mode_val)
            else:
                geology_mode.append(np.nan)
        gdf['geology'] = geology_mode
        print(f"    ✓ Geology extracted")
    else:
        print(f"  ⚠ Geology layer not available")
        gdf['geology'] = np.nan
    
    if os.path.exists(NDVI_FILE):
        gdf['ndvi_mean'] = extract_zonal_stats_simple(gdf, NDVI_FILE, 'mean')
        print(f"  ✓ NDVI extracted (mean: {gdf['ndvi_mean'].mean():.3f})")
    else:
        print(f"  ⚠ NDVI layer not available")
        gdf['ndvi_mean'] = np.nan
    
    # Save results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)
    
    # Shapefile
    print(f"\nSaving characterized watersheds...")
    gdf.to_file(OUT_SHP)
    print(f"✓ Saved shapefile: {OUT_SHP}")
    
    # CSV (without geometry)
    csv_df = gdf.drop('geometry', axis=1)
    csv_df.to_csv(OUT_CSV, index=False)
    print(f"✓ Saved CSV: {OUT_CSV}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("CHARACTERIZATION COMPLETE!")
    print("="*70)
    
    print(f"\nDataset Summary:")
    print(f"  Total watersheds: {len(gdf)}")
    print(f"  Total attributes: {len(gdf.columns)}")
    print(f"\nKey Attributes:")
    
    key_cols = ['watershed_id', 'area_km2', 'gwp_mean', 'slope_mean', 
                'drain_dens', 'rainfall', 'cropland', 'urban', 'forest']
    available_cols = [col for col in key_cols if col in gdf.columns]
    
    print(gdf[available_cols].describe().round(2).to_string())
    
    print(f"\n✓ Watersheds characterized and ready for prioritization!")
    print(f"\nNext step: python src/prioritize_watersheds.py")


if __name__ == "__main__":
    main()
