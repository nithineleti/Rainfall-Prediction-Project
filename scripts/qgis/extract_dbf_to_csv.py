"""
Extract data from DBF file (shapefile attribute table) to CSV
DBF files can be read without geopandas
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set UTF-8 encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("Extracting data from DBF file...")

try:
    from dbfread import DBF
    import pandas as pd
    from path_config import VECTORS_DIR, TABLES_DIR
    
    dbf_file = str(VECTORS_DIR / "watersheds_characterized.dbf")
    csv_file = str(TABLES_DIR / "watersheds_characterized.csv")
    
    print(f"Reading: {dbf_file}")
    
    # Read DBF
    dbf = DBF(dbf_file, encoding='utf-8')
    
    # Convert to DataFrame
    df = pd.DataFrame(iter(dbf))
    
    print(f"  Loaded {len(df)} records")
    print(f"  Columns: {len(df.columns)}")
    print(f"\n  Column names: {list(df.columns)}")
    
    # Save to CSV
    df.to_csv(csv_file, index=False)
    print(f"\n✓ Saved: {csv_file}")
    
    # Show sample
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    print("\n✅ Conversion complete!")
    
except ImportError:
    print("❌ dbfread not installed")
    print("Installing dbfread...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "dbfread"], check=True)
    print("\n✓ Installed! Run this script again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
