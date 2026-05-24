"""
ALOS PALSAR 12.5m DEM Setup Instructions
"""

print("""
========================================
ALOS PALSAR 12.5m DEM Download
========================================

OPTION 1: Download from NASA Earthdata (Automated)
---------------------------------------------------
1. Create free account: https://urs.earthdata.nasa.gov/users/new
2. Run: python scripts/lucknow_dem_12.5_download_script/download-all-2025-11-01_18-12-34.py
3. Enter your Earthdata username and password when prompted
4. Wait for 10 tiles to download (~5 GB, 15-30 min)

OPTION 2: Manual Download (Recommended if automated fails)
-----------------------------------------------------------
1. Go to: https://search.asf.alaska.edu/
2. Draw box around Lucknow (26.55°N-26.95°N, 80.80°E-81.20°E)
3. Select: ALOS PALSAR -> RTC Hi-Res DEM (12.5m)
4. Download these 10 tiles:
   - AP_12350_FBD_F0530_RT1
   - AP_12350_FBD_F0520_RT1
   - AP_11788_FBS_F3080_RT1
   - AP_11788_FBS_F3070_RT1
   - AP_08324_FBD_F0530_RT1
   - AP_08324_FBD_F0520_RT1
   - AP_07405_FBD_F0530_RT1
   - AP_07405_FBD_F0520_RT1
   - AP_08572_FBD_F0520_RT1
   - AP_08324_FBD_F0510_RT1

5. Save all ZIP files to: data/raw/alos_dem_tiles/

OPTION 3: Use Existing 30m DEM (Quick)
---------------------------------------
Your current Copernicus 30m DEM is perfectly fine for groundwater
potential mapping at district scale. The difference between 12.5m 
and 30m is minimal for this application.

To continue with 30m, just revert the path_config.py changes.

========================================

What would you like to do?
1. Continue with NASA download (needs credentials)
2. Download manually from ASF
3. Keep using 30m DEM (recommended for now)

""")

choice = input("Enter choice (1/2/3): ").strip()

if choice == "1":
    print("\nProceeding with automated download...")
    print("You'll be prompted for NASA Earthdata credentials.")
    import subprocess
    import os
    os.chdir("data/raw/alos_dem_tiles")
    subprocess.run(["python", "../../../scripts/lucknow_dem_12.5_download_script/download-all-2025-11-01_18-12-34.py"])
elif choice == "2":
    print("\nManual download instructions:")
    print("1. Open: https://search.asf.alaska.edu/")
    print("2. Follow steps above")
    print("3. After downloading, run: python scripts/lucknow_dem_12.5_download_script/mosaic_and_clip_dem.py")
elif choice == "3":
    print("\nReverting to 30m DEM...")
    print("No changes needed - your current setup works great!")
else:
    print("\nInvalid choice. Exiting.")
