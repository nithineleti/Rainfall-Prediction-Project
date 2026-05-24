# Quick Start Guide - Enhanced Features

## 🚀 Using the New Configuration System

### 1. View All Configuration Parameters
```bash
# See all available parameters
cat config.yml

# Test configuration loading
python config_loader.py
```

### 2. Access Configuration in Your Scripts
```python
from config_loader import config

# Get specific parameters
latitude = config.preprocessing.dem.latitude_center  # 26.8
cv_folds = config.machine_learning.training.cv_folds  # 5
weights = config.watershed.prioritization.weights

# Use in your code
print(f"Processing at latitude: {latitude}°")
print(f"Using {cv_folds}-fold cross-validation")
```

### 3. Change Parameters (No Code Editing!)
```yaml
# Edit config.yml
watershed:
  prioritization:
    weights:
      stress: 0.35        # Changed from 0.30
      potential: 0.25     # Changed from 0.25
      population: 0.20
      feasibility: 0.15
      cost: 0.05          # Changed from 0.10
```

Then just re-run your scripts - they'll automatically use new values!

---

## 🧪 Running Unit Tests

### Quick Test
```bash
# Run all tests
python -m pytest tests/test_core_functions.py -v

# Expected output:
# ============ 12 passed in 4.25s ============
```

### Test Specific Functions
```bash
# Test only configuration
pytest tests/test_core_functions.py::TestConfiguration -v

# Test only geospatial functions
pytest tests/test_core_functions.py::TestGeospatialFunctions -v

# Test with detailed output
pytest tests/test_core_functions.py -v --tb=long
```

### Before Making Changes
```bash
# Always run tests first!
pytest tests/test_core_functions.py

# If all pass, safe to proceed
# If any fail, fix before continuing
```

---

## 📊 Adding Progress Bars

### Example: Long Loop
```python
from tqdm import tqdm

# Before (no progress indicator)
for i in range(1000):
    process_item(i)

# After (with progress bar)
for i in tqdm(range(1000), desc="Processing items"):
    process_item(i)

# Output: Processing items: 45%|████▌     | 450/1000 [00:30<00:37, 14.7it/s]
```

### Example: File Processing
```python
from tqdm import tqdm
import os

file_size = os.path.getsize('large_file.tif')

with tqdm(total=file_size, unit='B', unit_scale=True, desc='Reading') as pbar:
    with open('large_file.tif', 'rb') as f:
        while chunk := f.read(8192):
            # Process chunk
            pbar.update(len(chunk))
```

### Where to Add Progress Bars
Recommended scripts:
1. `scripts/preprocessing/03_calculate_drainage.py` - flow accumulation
2. `scripts/watershed/delineate_watersheds.py` - watershed tracing
3. `scripts/ml/prepare_samples.py` - sample generation
4. `scripts/ml/train_model.py` - CV iterations

---

## 📝 Using Type Hints (Optional)

### Example: Function with Type Hints
```python
from typing import Tuple, Optional
import numpy as np

def normalize_raster(
    arr: np.ndarray,
    reverse: bool = False,
    nodata_value: Optional[float] = -9999
) -> np.ndarray:
    """
    Normalize array to 0-1 range.
    
    Parameters
    ----------
    arr : np.ndarray
        Input array
    reverse : bool, default=False
        If True, reverse the scale (1-0)
    nodata_value : float, optional
        Value to exclude from normalization
    
    Returns
    -------
    np.ndarray
        Normalized array (0-1 range)
    """
    # Implementation
    mask = arr != nodata_value
    min_val = arr[mask].min()
    max_val = arr[mask].max()
    
    normalized = (arr - min_val) / (max_val - min_val)
    
    if reverse:
        normalized = 1 - normalized
    
    return normalized
```

### Benefits
- IDE autocomplete knows what types to expect
- Catches type errors early
- Better documentation
- Easier to understand code

---

## 🎯 Common Workflows

### Workflow 1: Adjust Watershed Prioritization
```bash
# 1. Edit weights in config.yml
nano config.yml  # or any text editor

# 2. Test configuration loads
python config_loader.py

# 3. Re-run prioritization
python scripts/watershed/prioritize_watersheds.py

# 4. Check results
ls -lh data/vectors/watersheds_prioritized.*
```

### Workflow 2: Validate Changes
```bash
# 1. Make your code changes
# ... edit scripts ...

# 2. Run tests
pytest tests/test_core_functions.py -v

# 3. If tests pass, run full pipeline
python run_complete_pipeline.py

# 4. Verify outputs
ls -lh outputs/reports/
```

### Workflow 3: Experiment with ML Parameters
```yaml
# Edit config.yml
machine_learning:
  training:
    n_estimators: 300      # Try more trees
    cv_folds: 10           # Try more folds
```

```bash
# Re-run training
python scripts/ml/train_model.py --in data/tables/train_samples.csv

# Compare results
cat data/processed/stage4/cv_results.csv
```

---

## 📚 Key Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `config.yml` | All parameters | Adjust any threshold/weight |
| `config_loader.py` | Configuration API | Access params in scripts |
| `tests/test_core_functions.py` | Unit tests | Validate changes |
| `IMPROVEMENTS_IMPLEMENTED.md` | Full documentation | Understand improvements |
| `requirements.txt` | Dependencies | Install packages |

---

## 💡 Tips & Best Practices

### 1. Configuration Changes
✅ **DO:** Edit `config.yml` to change parameters  
❌ **DON'T:** Hardcode values in scripts

### 2. Testing
✅ **DO:** Run tests before and after changes  
❌ **DON'T:** Skip tests when making modifications

### 3. Version Control
✅ **DO:** Commit `config.yml` with meaningful messages  
❌ **DON'T:** Commit temporary test values

### 4. Documentation
✅ **DO:** Add comments explaining parameter choices  
❌ **DON'T:** Use "magic numbers" without explanation

---

## 🆘 Troubleshooting

### Config Not Loading
```bash
# Check if config.yml exists
ls config.yml

# Test loading
python config_loader.py

# Check for YAML syntax errors
python -c "import yaml; yaml.safe_load(open('config.yml'))"
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/test_core_functions.py -v --tb=long

# Run specific failing test
pytest tests/test_core_functions.py::TestName::test_name -v

# Check Python environment
python --version
pip list | grep -E "pytest|numpy|pandas"
```

### Import Errors
```bash
# Ensure packages installed
pip install -r requirements.txt

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"

# Verify project structure
ls -la  # Should see config.yml, path_config.py, etc.
```

---

## 🎉 Success Checklist

After implementing recommendations, verify:

- ✅ Configuration loads: `python config_loader.py`
- ✅ Tests pass: `pytest tests/test_core_functions.py`
- ✅ Dependencies installed: `pip install -r requirements.txt`
- ✅ Scripts still run: Test one preprocessing script
- ✅ Documentation readable: Review `IMPROVEMENTS_IMPLEMENTED.md`

If all ✅, you're ready to use the enhanced system!

---

## 📞 Need Help?

1. Check `IMPROVEMENTS_IMPLEMENTED.md` for detailed explanations
2. Review `config.yml` comments for parameter descriptions
3. Look at `tests/test_core_functions.py` for usage examples
4. Run `python config_loader.py` to see current configuration

**Happy watershed analysis! 🌊**
