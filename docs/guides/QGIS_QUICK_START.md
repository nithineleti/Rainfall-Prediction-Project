# QGIS Characterization - Quick Start Guide

## 🎯 Goal
Replace synthetic watershed data with **real zonal statistics** extracted from actual rasters (GWP, slope, elevation, LULC, etc.)

---

## ⚡ Quick Steps (5-10 minutes)

### Step 1: Open QGIS Desktop
1. Launch **QGIS Desktop** application
2. Wait for it to fully load

### Step 2: Open Python Console
1. Click **Plugins** → **Python Console**  
   (or press `Ctrl+Alt+P`)
2. A Python console appears at the bottom of QGIS window

### Step 3: Run Characterization Script
**Copy and paste this ONE LINE into the console:**

```python
exec(open('G:/PROJECTS/watershed-up/qgis_characterize_watersheds.py').read())
```

Press `Enter` and wait 2-5 minutes for processing.

---

## ✅ Expected Output

You should see progress messages like:
```
Working directory: G:\PROJECTS\watershed-up
QGIS version: 3.x.x
✓ Loaded 144 watersheds
✓ Added fields
✓ Processing GWP (1/7)...
✓ Processing Slope (2/7)...
✓ Processing Elevation (3/7)...
...
✓ Saved: data/processed/stage4/watersheds_characterized.shp
✓ Saved: data/processed/stage4/watersheds_characterized.csv
```

### Output Files Created:
- ✅ `data/processed/stage4/watersheds_characterized.shp` - Shapefile with real stats
- ✅ `data/processed/stage4/watersheds_characterized.csv` - CSV backup
- ✅ `data/processed/stage4/watersheds_characterized_qgis.log` - Processing log

---

## 🔍 Verification

After script completes, check the CSV file:

```powershell
Get-Content data/processed/stage4/watersheds_characterized.csv | Select-Object -First 5
```

You should see real values for:
- `gwp_mean` (0.0 to 1.0)
- `slope_mean` (degrees)
- `elev_mean` (meters)
- `forest`, `cropland`, `urban` (percentages)
- etc.

---

## 🔄 Next Steps (After QGIS Completes)

Once QGIS finishes, return to this terminal and run:

```powershell
# Step 1: Re-run prioritization with real data
python src/prioritize_watersheds.py

# Step 2: Regenerate reports
python src/generate_watershed_reports.py

# Step 3: Refresh Streamlit dashboard
# (it will automatically load the new data)
```

---

## ⚠️ Troubleshooting

**If script fails:**
1. Check that all rasters exist in `data/processed/stage3/`
2. Run step-by-step using QGIS_INSTRUCTIONS.md (Block-by-Block approach)
3. Check the log file for specific errors

**Common Issues:**
- **CRS mismatch**: Script will reproject automatically
- **Missing raster**: Will skip that layer and continue
- **Memory issues**: QGIS uses efficient chunk processing

---

## 📊 What Gets Extracted (Real Data)

### From Rasters (Zonal Statistics):
1. **GWP** (`predicted_grp_score.tif`): Mean + StdDev
2. **Slope** (`slope_lucknow.tif`): Mean + Max
3. **Elevation** (`dem_lucknow.tif`): Mean + Min + Max + Range
4. **Drainage Density** (calculated from stream network)
5. **Rainfall** (`rainfall_lucknow.tif`): Mean

### From LULC (Percentage Coverage):
6. **Forest** - Percentage of watershed
7. **Cropland** - Percentage of watershed
8. **Urban** - Percentage of watershed
9. **Water** - Percentage of watershed
10. **Other** - Remaining land use

---

## 💡 Why QGIS Instead of Python?

**Problem**: Windows conda environment has GDAL DLL issues  
**Solution**: QGIS has its own working Python with all geospatial libraries pre-installed

**QGIS Python includes:**
- ✅ geopandas (working)
- ✅ rasterio (working)
- ✅ GDAL/PROJ (working)
- ✅ Zonal statistics tools
- ✅ No environment conflicts

---

## 🎯 Ready to Run?

1. **Open QGIS Desktop**
2. **Open Python Console** (`Ctrl+Alt+P`)
3. **Paste and run**:
   ```python
   exec(open('G:/PROJECTS/watershed-up/qgis_characterize_watersheds.py').read())
   ```
4. **Wait 2-5 minutes**
5. **Come back here when done!**

---

**Good luck! 🚀**
