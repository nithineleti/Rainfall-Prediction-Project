import sys
import os
from pathlib import Path

# Ensure src/ is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT)) # Also include root for config_utils if it was there

from src.config_utils import load_config
import src.preprocess as preprocess
import src.train_classifier as train_classifier
import src.train_regressor as train_regressor
import src.evaluate as evaluate
import src.visualize as visualize

def main():
    print("\n" + "="*60)
    print("      DUAL-STAGE RAINFALL PREDICTION PIPELINE")
    print("="*60 + "\n")
    
    # 1. Load configuration
    print("Step 1: Loading configuration...")
    cfg = load_config("configs/config.yaml")
    
    # 2. Preprocess
    print("\nStep 2: Preprocessing and feature engineering...")
    preprocess.run_preprocessing("configs/config.yaml")
    
    # 3. Train Classifier
    print("\nStep 3: Training Stage 1 - Classifier (Rain/No Rain)...")
    train_classifier.run_training("configs/config.yaml")
    
    # 4. Train Regressor
    print("\nStep 4: Training Stage 2 - Regressor (Rainfall Amount)...")
    train_regressor.run_training("configs/config.yaml")
    
    # 5. Evaluate
    print("\nStep 5: Running full test evaluation...")
    evaluate.evaluate_all("configs/config.yaml")
    
    # 6. Visualize
    print("\nStep 6: Generating plots and visualizations...")
    visualize.run_all_eda_plots("configs/config.yaml")
    
    print("\n" + "="*60)
    print("  Pipeline execution complete! Check 'outputs/' for results.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
