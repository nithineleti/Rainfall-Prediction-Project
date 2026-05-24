"""
Enhanced Watershed Features for Better Groundwater Prediction

This script adds detailed hydrological and topographic features:
1. Topographic Wetness Index (TWI) - water accumulation tendency
2. Slope aspects - directional influence on water flow
3. Curvature (plan & profile) - convergence/divergence zones
4. Topographic Position Index (TPI) - valley/ridge classification
5. Distance to streams - proximity to drainage network
6. Catchment areas - watershed delineation

These features are much more relevant for groundwater prediction
than uniform geology.
"""

import os
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from scipy import ndimage
from scipy.ndimage import distance_transform_edt
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIG ====================
DEM_FILE = "data/processed/dem_lucknow.tif"
SLOPE_FILE = "data/processed/slope_lucknow.tif"
FLOW_ACC_FILE = "data/processed/stage3/flow_acc_lucknow.tif"
STREAM_FILE = "data/processed/stage3/stream_network_lucknow.tif"

OUT_DIR = "data/processed/stage3"
os.makedirs(OUT_DIR, exist_ok=True)

# Output files
TWI_OUT = os.path.join(OUT_DIR, "twi_lucknow.tif")
ASPECT_OUT = os.path.join(OUT_DIR, "aspect_lucknow.tif")
PLAN_CURV_OUT = os.path.join(OUT_DIR, "plan_curvature_lucknow.tif")
PROF_CURV_OUT = os.path.join(OUT_DIR, "profile_curvature_lucknow.tif")
TPI_OUT = os.path.join(OUT_DIR, "tpi_lucknow.tif")
DIST_STREAM_OUT = os.path.join(OUT_DIR, "distance_to_stream_lucknow.tif")


def load_raster(filepath):
    """Load raster and return data + profile"""
    src = rasterio.open(filepath)
    data = src.read(1)
    profile = src.profile.copy()
    transform = src.transform
    src.close()
    return data, profile, transform


def save_raster(data, profile, filepath, dtype=np.float32, nodata=np.nan):
    """Save raster with specified dtype"""
    profile_out = profile.copy()
    profile_out.update(dtype=dtype, count=1, compress='lzw', nodata=nodata)
    with rasterio.open(filepath, 'w', **profile_out) as dst:
        dst.write(data.astype(dtype), 1)


def compute_twi(slope, flow_acc, pixel_size):
    """
    Topographic Wetness Index (TWI)
    TWI = ln(a / tan(β))
    where a = specific catchment area, β = slope
    
    Higher TWI = greater tendency for water accumulation
    """
    print("Computing Topographic Wetness Index (TWI)...")
    
    # Convert slope from degrees to radians
    slope_rad = np.deg2rad(slope)
    tan_slope = np.tan(slope_rad)
    
    # Avoid division by zero - set minimum slope
    tan_slope = np.where(tan_slope < 0.001, 0.001, tan_slope)
    
    # Specific catchment area (flow accumulation * pixel area)
    sca = flow_acc * (pixel_size ** 2)
    
    # TWI calculation
    twi = np.log(sca / tan_slope)
    
    # Handle invalid values
    twi = np.where(np.isinf(twi) | np.isnan(twi), 0, twi)
    
    print(f"  TWI range: {twi.min():.2f} to {twi.max():.2f}")
    return twi


def compute_aspect(dem):
    """
    Compute aspect (direction of slope)
    Returns aspect in degrees (0-360)
    North = 0°, East = 90°, South = 180°, West = 270°
    """
    print("Computing aspect...")
    
    # Compute gradients
    dy, dx = np.gradient(dem)
    
    # Aspect in radians, then convert to degrees
    aspect = np.arctan2(-dx, dy)
    aspect_deg = np.rad2deg(aspect)
    
    # Convert to compass direction (0-360)
    aspect_deg = (450 - aspect_deg) % 360
    
    # Flat areas (slope = 0) get aspect = -1
    slope_mag = np.sqrt(dx**2 + dy**2)
    aspect_deg = np.where(slope_mag < 0.0001, -1, aspect_deg)
    
    print(f"  Aspect range: {aspect_deg[aspect_deg >= 0].min():.1f}° to {aspect_deg.max():.1f}°")
    return aspect_deg


def compute_curvature(dem, pixel_size):
    """
    Compute plan and profile curvature
    
    Plan curvature: perpendicular to slope direction (convergence/divergence)
      - Positive = divergent (ridges, water disperses)
      - Negative = convergent (valleys, water accumulates)
    
    Profile curvature: parallel to slope direction (acceleration)
      - Positive = convex (deceleration, deposition)
      - Negative = concave (acceleration, erosion)
    """
    print("Computing curvatures...")
    
    # First derivatives
    zy, zx = np.gradient(dem, pixel_size)
    
    # Second derivatives
    zxy, zxx = np.gradient(zx, pixel_size)
    zyy, zyx = np.gradient(zy, pixel_size)
    
    # Slope
    p = zx
    q = zy
    
    # Plan curvature
    plan_curv = (zxx * q**2 - 2 * zxy * p * q + zyy * p**2) / ((p**2 + q**2) * np.sqrt(1 + p**2 + q**2)**3)
    plan_curv = np.where(np.isnan(plan_curv) | np.isinf(plan_curv), 0, plan_curv)
    
    # Profile curvature
    prof_curv = (zxx * p**2 + 2 * zxy * p * q + zyy * q**2) / ((p**2 + q**2) * (1 + p**2 + q**2)**1.5)
    prof_curv = np.where(np.isnan(prof_curv) | np.isinf(prof_curv), 0, prof_curv)
    
    print(f"  Plan curvature range: {plan_curv.min():.6f} to {plan_curv.max():.6f}")
    print(f"  Profile curvature range: {prof_curv.min():.6f} to {prof_curv.max():.6f}")
    
    return plan_curv, prof_curv


def compute_tpi(dem, radius=10):
    """
    Topographic Position Index (TPI)
    TPI = elevation - mean elevation in neighborhood
    
    Positive = ridges/hills
    Negative = valleys/depressions
    Near zero = flat areas or mid-slope
    
    Useful for identifying groundwater recharge (ridges) vs discharge (valleys) zones
    """
    print(f"Computing Topographic Position Index (radius={radius} pixels)...")
    
    # Mean filter
    mean_elev = ndimage.uniform_filter(dem, size=2*radius+1, mode='reflect')
    
    # TPI
    tpi = dem - mean_elev
    
    print(f"  TPI range: {tpi.min():.2f} to {tpi.max():.2f}")
    return tpi


def compute_distance_to_stream(stream, pixel_size):
    """
    Euclidean distance to nearest stream
    Important for groundwater-surface water interaction
    """
    print("Computing distance to streams...")
    
    # Binary stream mask (1 = stream, 0 = non-stream)
    stream_binary = (stream > 0).astype(np.uint8)
    
    # Distance transform (in pixels)
    dist_pixels = distance_transform_edt(1 - stream_binary)
    
    # Convert to meters
    dist_meters = dist_pixels * pixel_size * 1000  # assuming pixel_size in km
    
    print(f"  Distance range: {dist_meters.min():.1f} to {dist_meters.max():.1f} meters")
    return dist_meters


def main():
    print("="*70)
    print("ENHANCED WATERSHED FEATURE EXTRACTION")
    print("="*70)
    
    # Load base data
    print("\nLoading base datasets...")
    dem, profile, transform = load_raster(DEM_FILE)
    slope, _, _ = load_raster(SLOPE_FILE)
    flow_acc, _, _ = load_raster(FLOW_ACC_FILE)
    stream, _, _ = load_raster(STREAM_FILE)
    
    # Estimate pixel size in km
    pixel_size = transform[0]  # assuming square pixels
    print(f"Pixel size: {pixel_size:.6f} degrees (~{pixel_size * 111:.3f} km)")
    
    # 1. Topographic Wetness Index
    twi = compute_twi(slope, flow_acc, pixel_size)
    save_raster(twi, profile, TWI_OUT)
    print(f"✓ Saved: {TWI_OUT}")
    
    # 2. Aspect
    aspect = compute_aspect(dem)
    save_raster(aspect, profile, ASPECT_OUT)
    print(f"✓ Saved: {ASPECT_OUT}")
    
    # 3. Curvatures
    plan_curv, prof_curv = compute_curvature(dem, pixel_size)
    save_raster(plan_curv, profile, PLAN_CURV_OUT)
    print(f"✓ Saved: {PLAN_CURV_OUT}")
    save_raster(prof_curv, profile, PROF_CURV_OUT)
    print(f"✓ Saved: {PROF_CURV_OUT}")
    
    # 4. Topographic Position Index
    tpi = compute_tpi(dem, radius=10)
    save_raster(tpi, profile, TPI_OUT)
    print(f"✓ Saved: {TPI_OUT}")
    
    # 5. Distance to streams
    dist_stream = compute_distance_to_stream(stream, pixel_size)
    save_raster(dist_stream, profile, DIST_STREAM_OUT)
    print(f"✓ Saved: {DIST_STREAM_OUT}")
    
    print("\n" + "="*70)
    print("ENHANCED FEATURES SUMMARY")
    print("="*70)
    print("""
Created 6 new hydrologically-relevant features:

1. TWI (Topographic Wetness Index):
   - Identifies water accumulation zones
   - Higher values = potential groundwater recharge areas

2. Aspect:
   - Slope direction (0-360°)
   - Affects evapotranspiration and runoff patterns

3. Plan Curvature:
   - Negative = convergent flow (valleys, water accumulates)
   - Positive = divergent flow (ridges, water disperses)

4. Profile Curvature:
   - Negative = concave (flow acceleration)
   - Positive = convex (flow deceleration)

5. TPI (Topographic Position Index):
   - Positive = ridges/hills (recharge zones)
   - Negative = valleys (discharge zones)

6. Distance to Streams:
   - Proximity to surface water network
   - Important for groundwater-surface water interaction

These features are MUCH more informative than uniform geology!
""")
    
    print("\nNext steps:")
    print("1. Update src/features_stack.py to include these new features")
    print("2. Remove or keep geology (it has zero variance)")
    print("3. Retrain model with enhanced feature set")
    print("4. Check feature importance - hydrological features should dominate!")
    

if __name__ == "__main__":
    main()
