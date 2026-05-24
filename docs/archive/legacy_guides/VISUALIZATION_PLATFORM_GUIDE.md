# GRPZ Visualization Platform - Quick Start Guide

## Overview

This guide will help you set up and run the interactive GRPZ (Groundwater Potential Zone) visualization platform for the Lucknow watershed project.

## Prerequisites

- Python 3.10 or higher
- Git (optional, for version control)
- At least 4GB of RAM
- Modern web browser (Chrome, Firefox, Edge)

## Step-by-Step Setup

### Option 1: Using Conda (Recommended)

```bash
# 1. Create conda environment from the existing environment.yml
conda env create -f environment.yml

# 2. Activate the environment
conda activate watershed-up

# 3. Install Streamlit and additional web app dependencies
pip install streamlit streamlit-folium seaborn

# 4. Verify installation
python -c "import streamlit; import folium; print('Setup successful!')"
```

### Option 2: Using pip

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import streamlit; import folium; print('Setup successful!')"
```

## Data Preparation

Before running the visualization platform, ensure you have processed the data:

### 1. Basic Preprocessing

```bash
# Preprocess DEM and derived features
python src/preprocess.py

# Preprocess LULC data
python src/preprocess_lulc.py

# Preprocess rainfall data
python src/preprocess_rain.py

# Preprocess Stage 3 features (geology, NDVI, etc.)
python src/preprocess_stage3.py
```

### 2. Feature Engineering

```bash
# Derive drainage features (flow accumulation, stream network)
python src/derive_drainage.py

# Create feature stack
python src/features_stack.py

# Visualize and summarize features
python src/visualize_stage3.py
```

### 3. Model Training

```bash
# Generate training samples from wells
python src/sample_wells.py --stack data/processed/stage3/features_stack.tif --wells data/raw/wells_cgwb.csv --out data/processed/stage4/train_samples.csv

# Clean training samples
python src/clean_samples.py

# Train the Random Forest model
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models --cv_k 5

# Generate SHAP explanations (optional)
python src/shap_explain.py
```

### 4. Generate Predictions

```bash
# Predict using ML model
python src/predict_map.py

# Run AHP analysis (optional)
python src/ahp.py

# Compare ML vs AHP (optional)
python src/compare_with_ahp.py
```

## Running the Visualization Platform

### Method 1: Direct Launch

```bash
streamlit run app/main.py
```

### Method 2: Using Launch Script

```bash
cd app
python launch_app.py
```

### Method 3: From Project Root

```bash
python -m streamlit run app/main.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## Platform Features

### 1. Home Page (🏠)
- Project overview and methodology
- Data availability checker
- GRPZ classification legend
- Quick start guide

### 2. Interactive Map (🗺️)
- View ML and AHP predictions
- Toggle data layers
- Show well locations
- Adjust layer opacity
- Multiple basemap options
- Real-time statistics

### 3. Data Layers (📊)
- Explore individual features (DEM, slope, LULC, etc.)
- View statistical summaries
- Compare multiple layers
- Correlation analysis
- Export feature data

### 4. Model Insights (🤖)
- Feature importance ranking
- Cross-validation results
- Confusion matrix
- SHAP explanations
- ML vs AHP comparison

### 5. Statistical Analysis (📈)
- Training data statistics
- Class distribution
- Feature distributions by class
- Correlation heatmaps
- Spatial sample distribution

### 6. Well Validation (🔍)
- Validate predictions against well data
- Well performance by predicted class
- Statistical validation metrics
- Export validated data

### 7. Export & Download (📥)
- Download prediction maps (GeoTIFF)
- Export shapefiles
- Training/validation data (CSV)
- Trained model files
- Complete data packages (ZIP)

## Common Usage Scenarios

### Scenario 1: Explore Predictions

1. Navigate to **Interactive Map**
2. Select "ML Prediction (Class)" or "AHP Result (Class)"
3. Toggle "Show Well Locations" to see validation points
4. Click on map areas to see details
5. Use opacity slider to overlay with basemap

### Scenario 2: Understand Model Performance

1. Go to **Model Insights**
2. Review feature importance to see key predictors
3. Check cross-validation results for accuracy
4. Examine confusion matrix
5. View SHAP analysis for interpretability

### Scenario 3: Validate Results

1. Visit **Well Validation**
2. Select prediction source (ML or AHP)
3. View cross-tabulation of predictions vs well performance
4. Analyze percentage charts
5. Export validated data for further analysis

### Scenario 4: Export Data for GIS

1. Go to **Export & Download**
2. Download prediction maps (GeoTIFF)
3. Download shapefiles for vector analysis
4. Open in QGIS or ArcGIS
5. Perform custom spatial analysis

## Troubleshooting

### Issue: "Data file not found"

**Solution:**
- Ensure you've run the complete data processing pipeline
- Check that file paths in scripts match your directory structure
- Verify data files exist in the expected locations

### Issue: Map not loading

**Solution:**
- Large rasters may take time to render
- Try selecting a different layer
- Check browser console for errors
- Ensure adequate system memory

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or reinstall specific packages
pip install --upgrade streamlit streamlit-folium
```

### Issue: Port already in use

**Solution:**
```bash
# Specify a different port
streamlit run app/main.py --server.port 8502
```

## Performance Tips

1. **For Large Datasets:**
   - Sample data when creating histograms
   - Use correlation matrix from pre-computed CSV
   - Close unused browser tabs

2. **For Faster Loading:**
   - Reduce raster resolution if needed
   - Use efficient file formats
   - Enable browser caching

3. **For Better Visualization:**
   - Adjust opacity for better layer visibility
   - Use appropriate color schemes
   - Export high-resolution figures separately

## Customization

### Change Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = false
enableCORS = false
```

### Modify Layout

Edit `app/main.py` to:
- Change page titles
- Add new navigation items
- Customize sidebar content
- Modify color schemes

### Add Custom Pages

1. Create new file in `app/pages/your_page.py`
2. Implement `show()` function
3. Add import and condition in `app/main.py`

## Deployment Options

### Local Network Access

```bash
streamlit run app/main.py --server.address 0.0.0.0
```

Access from other devices: `http://YOUR_IP:8501`

### Cloud Deployment

**Streamlit Cloud (Free):**
1. Push code to GitHub
2. Sign up at streamlit.io
3. Connect repository
4. Deploy automatically

**Docker:**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app/main.py"]
```

## Data Management

### Expected File Structure

```
watershed-up/
├── app/                    # Streamlit application
├── data/
│   ├── processed/         # Processed GeoTIFFs and CSVs
│   └── raw/              # Original data
├── models/               # Trained models
├── src/                  # Processing scripts
├── requirements.txt      # Python dependencies
└── environment.yml       # Conda environment
```

### Backup Important Files

```bash
# Backup predictions
cp -r data/processed/stage4/ backups/predictions_$(date +%Y%m%d)/

# Backup model
cp models/rf_baseline.pkl backups/model_$(date +%Y%m%d).pkl
```

## Best Practices

1. **Data Version Control:**
   - Track changes to processing scripts
   - Document data sources and versions
   - Maintain changelog for updates

2. **Model Management:**
   - Save model training parameters
   - Document feature engineering steps
   - Keep validation metrics

3. **User Experience:**
   - Add clear instructions
   - Provide tooltips and help text
   - Include data quality indicators

4. **Performance:**
   - Cache expensive computations
   - Optimize raster operations
   - Use efficient data formats

## Support and Resources

- **Documentation:** `docs/` folder
- **Examples:** `notebooks/` folder
- **Scripts:** `src/` folder with inline comments

## Next Steps

1. ✅ Set up environment
2. ✅ Process data
3. ✅ Train model
4. ✅ Launch platform
5. 🎯 Explore and validate results
6. 📊 Export data for stakeholders
7. 📝 Generate reports
8. 🔄 Iterate and improve

---

**Questions or Issues?**
- Review the README files in `app/` and project root
- Check the Software Requirements Specification (SRS) in `docs/`
- Examine example scripts for implementation details

**Happy Exploring! 💧🗺️**
