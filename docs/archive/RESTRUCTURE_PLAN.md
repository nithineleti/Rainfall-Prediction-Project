# Project Restructuring Plan - Safe Migration

**Date:** October 29, 2025  
**Commit Before Restructure:** `9141434` - "feat: enhanced watershed features complete - BACKUP before restructure"  
**Rollback Command:** `git reset --hard 9141434`

---

## 🎯 Objective

Transform current flat structure into production-ready architecture with:
- Backend API (FastAPI)
- ML Pipeline (organized)
- UI (React/Streamlit)
- Docker Compose
- CI/CD
- Comprehensive docs

---

## 📋 File Preservation Checklist

### CRITICAL - DO NOT DELETE

**Enhanced Watershed Features (Recently Created):**
```
✅ src/enhance_watershed_features.py
✅ src/derive_drainage.py
✅ src/features_stack.py
✅ data/processed/stage3/twi_lucknow.tif
✅ data/processed/stage3/tpi_lucknow.tif
✅ data/processed/stage3/distance_to_stream_lucknow.tif
✅ data/processed/stage3/plan_curvature_lucknow.tif
✅ data/processed/stage3/profile_curvature_lucknow.tif
✅ data/processed/stage3/aspect_lucknow.tif
✅ docs/ENHANCED_WATERSHED_FEATURES.md
✅ docs/MODEL_TRAINING_RESULTS.md
```

**Core ML Scripts:**
```
✅ src/train_model.py
✅ src/predict_map.py
✅ src/shap_explain.py
✅ src/sample_wells.py
✅ src/clean_samples.py
```

**Preprocessing Scripts:**
```
✅ src/preprocess.py
✅ src/preprocess_stage3.py
✅ src/preprocess_lulc.py
✅ src/preprocess_rain.py
✅ src/mosaic_and_clip_dem.py
```

**AHP Engine:**
```
✅ src/ahp.py
✅ src/ahp_with_lulc.py
✅ src/ahp_with_rain.py
```

**Visualization:**
```
✅ src/visualize.py
✅ src/visualize_stage3.py
✅ visualize_enhanced_features.py
✅ visualize_prediction_results.py
```

**Streamlit App:**
```
✅ app/ (entire directory)
✅ launch_streamlit.bat
✅ launch_streamlit.ps1
```

**Data (ALL FILES):**
```
✅ data/raw/ (all files)
✅ data/processed/ (all files)
✅ models/rf_baseline.pkl
```

**Documentation:**
```
✅ docs/ (all markdown files)
✅ docs/thesis_progress_*.tex
✅ README.md
✅ ENHANCED_FEATURES_SUMMARY.md
```

**Configuration:**
```
✅ environment.yml
✅ requirements.txt
✅ configs/config.yml
```

---

## 🏗️ New Structure Mapping

### Where Files Will Move

**Current → New Location**

1. **Core ML Scripts** → `ml/src/`
   ```
   src/train_model.py              → ml/src/train.py
   src/predict_map.py              → ml/src/predict.py
   src/enhance_watershed_features.py → ml/src/features.py
   src/shap_explain.py             → ml/src/evaluate.py
   src/sample_wells.py             → ml/src/sampling.py
   ```

2. **Preprocessing** → `backend/app/services/`
   ```
   src/preprocess*.py              → backend/app/services/preprocess.py
   src/derive_drainage.py          → backend/app/services/hydrology.py
   src/features_stack.py           → backend/app/services/feature_engineering.py
   src/mosaic_and_clip_dem.py      → backend/app/services/raster_ops.py
   ```

3. **AHP Engine** → `backend/app/services/`
   ```
   src/ahp*.py                     → backend/app/services/ahp_engine.py
   ```

4. **API (NEW)** → `backend/app/api/v1/`
   ```
   NEW: backend/app/main.py
   NEW: backend/app/api/v1/data.py
   NEW: backend/app/api/v1/jobs.py
   NEW: backend/app/api/v1/ahp.py
   NEW: backend/app/api/v1/ml.py
   ```

5. **Streamlit App** → `ui/streamlit/`
   ```
   app/                            → ui/streamlit/app/
   launch_streamlit.*              → ui/streamlit/
   ```

6. **React UI (NEW)** → `ui/web/`
   ```
   NEW: ui/web/src/App.jsx
   NEW: ui/web/src/components/MapView.jsx
   ```

7. **Data** → KEEP IN PLACE
   ```
   data/                           → data/ (NO CHANGE)
   models/                         → models/ (NO CHANGE)
   ```

8. **Docs** → `docs/` (reorganized)
   ```
   docs/*.md                       → docs/
   docs/*.tex                      → docs/latex/
   NEW: docs/SRS_MASTER.md
   NEW: docs/API_SPEC.md
   NEW: docs/RUNBOOK.md
   ```

9. **Scripts** → `scripts/`
   ```
   run_pipeline.bat                → scripts/run_pipeline.bat
   run_shap.bat                    → scripts/run_shap.bat
   cleanup_project.ps1             → scripts/maintenance/
   ```

10. **Configuration** → Root + Backend
    ```
    environment.yml                 → ml/conda_env.yml
    requirements.txt                → backend/requirements.txt
    configs/                        → backend/app/configs/
    ```

---

## 📝 Step-by-Step Migration

### Phase 1: Create New Directory Structure (NO DELETIONS)
```bash
mkdir -p backend/app/{api/v1,core,db,workers,services,utils}
mkdir -p ml/src ml/notebooks
mkdir -p ui/web/src/components ui/streamlit
mkdir -p docs/latex docs/api
mkdir -p tests/backend tests/ml
mkdir -p .github/workflows
mkdir -p infra/terraform
mkdir -p scripts/maintenance
```

### Phase 2: Copy Core Files (COPY, NOT MOVE)
```bash
# ML files
cp src/train_model.py ml/src/train.py
cp src/predict_map.py ml/src/predict.py
cp src/enhance_watershed_features.py ml/src/features.py

# Backend services (consolidate)
# Create new files that import from src/ (bridge phase)
```

### Phase 3: Create New API Layer
```bash
# Create FastAPI app
# Create API endpoints that call existing src/ functions
```

### Phase 4: Create React UI
```bash
# Initialize React app in ui/web/
```

### Phase 5: Add Docker & CI
```bash
# Create docker-compose.yml
# Create Dockerfiles
# Create GitHub Actions
```

### Phase 6: Consolidate & Clean
```bash
# After verifying everything works:
# - Move files from src/ to new locations
# - Update imports
# - Remove duplicates
```

---

## ⚠️ Safety Checks Before Each Phase

1. **Test Current Functionality:**
   ```bash
   python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models
   .\run_pipeline.bat
   .\launch_streamlit.bat
   ```

2. **Git Commit After Each Phase:**
   ```bash
   git add -A
   git commit -m "refactor(phaseN): description"
   ```

3. **Rollback If Needed:**
   ```bash
   git log --oneline  # Find commit hash
   git reset --hard <commit-hash>
   ```

---

## 🔄 Import Path Updates

### Before
```python
from src.preprocess import load_dem
from src.train_model import train_xgb
```

### After
```python
from backend.app.services.preprocess import load_dem
from ml.src.train import train_xgb
```

**Strategy:** Use `setup.py` or `__init__.py` to maintain backward compatibility during transition.

---

## 🧪 Testing Strategy

### After Each Phase
1. Run existing scripts (should still work)
2. Test new API endpoints (if added)
3. Verify data files unchanged
4. Check model predictions match

### Final Validation
```bash
# Old way (should still work)
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models

# New way (should produce same results)
python ml/src/train.py --in data/processed/stage4/train_samples_clean.csv --out_dir models

# API way (new)
curl -X POST http://localhost:8000/v1/ml/train
```

---

## 📊 Progress Tracking

- [ ] Phase 1: Directory structure created
- [ ] Phase 2: Files copied to new locations
- [ ] Phase 3: FastAPI backend created
- [ ] Phase 4: React UI created
- [ ] Phase 5: Docker & CI added
- [ ] Phase 6: Old files removed, imports updated
- [ ] Final: All tests passing

---

## 🚨 Emergency Rollback

If anything breaks:
```bash
# Return to pre-restructure state
git reset --hard 9141434

# Or return to any phase
git log --oneline
git reset --hard <phase-commit-hash>
```

---

## ✅ Acceptance Criteria

Before declaring success:
1. ✅ All original scripts still work
2. ✅ New API endpoints functional
3. ✅ React UI loads map
4. ✅ Docker compose starts all services
5. ✅ ML model predictions unchanged
6. ✅ All data files preserved
7. ✅ Documentation updated
8. ✅ Tests passing

---

**Next Action:** Execute Phase 1 - Create directory structure
