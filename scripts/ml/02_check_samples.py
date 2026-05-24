import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from path_config import TRAIN_SAMPLES_CSV

df = pd.read_csv(str(TRAIN_SAMPLES_CSV))
print(f"Total samples: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nLabel distribution:")
print(df['label'].value_counts())
print(f"\nFirst few rows:")
print(df.head())
