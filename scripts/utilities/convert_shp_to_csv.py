# -*- coding: utf-8 -*-
"""
Convert QGIS Shapefile Output to CSV
Since QGIS CSV export might be empty, read the shapefile and create CSV manually
"""
import sys
import os

# Set UTF-8 encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("Converting shapefile to CSV...")

try:
    import geopandas as gpd
    import pandas as pd
    
    shp_file = "data/processed/stage4/watersheds_characterized.shp"
    csv_file = "data/processed/stage4/watersheds_characterized.csv"
    
    # Read shapefile
    print(f"Reading: {shp_file}")
    gdf = gpd.read_file(shp_file)
    
    print(f"  Loaded {len(gdf)} features")
    print(f"  Columns: {len(gdf.columns)}")
    
    # Drop geometry for CSV
    df = gdf.drop(columns=['geometry'])
    
    # Save to CSV
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved: {csv_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    
    # Show first few rows
    print("\nFirst 3 rows:")
    print(df.head(3))
    
except ImportError:
    print("❌ geopandas not available, using fiona instead...")
    
    try:
        import fiona
        import pandas as pd
        
        shp_file = "data/processed/stage4/watersheds_characterized.shp"
        csv_file = "data/processed/stage4/watersheds_characterized.csv"
        
        # Read with fiona
        print(f"Reading: {shp_file}")
        
        data = []
        with fiona.open(shp_file) as src:
            print(f"  Loaded {len(src)} features")
            print(f"  Properties: {list(src.schema['properties'].keys())}")
            
            for feature in src:
                props = feature['properties']
                # Add centroid coordinates
                geom = feature['geometry']
                if geom['type'] == 'Polygon':
                    coords = geom['coordinates'][0]
                    # Simple centroid approximation
                    xs = [c[0] for c in coords]
                    ys = [c[1] for c in coords]
                    props['centroid_x'] = sum(xs) / len(xs)
                    props['centroid_y'] = sum(ys) / len(ys)
                
                data.append(props)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(csv_file, index=False)
        print(f"✓ Saved: {csv_file}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        
        # Show first few rows
        print("\nFirst 3 rows:")
        print(df.head(3))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTrying GDAL/OGR...")
        
        # Last resort: use ogr2ogr command
        import subprocess
        
        shp_file = "data/processed/stage4/watersheds_characterized.shp"
        csv_file = "data/processed/stage4/watersheds_characterized.csv"
        
        cmd = f'ogr2ogr -f CSV "{csv_file}" "{shp_file}" -lco GEOMETRY=AS_XY'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Saved: {csv_file}")
        else:
            print(f"❌ Failed: {result.stderr}")
