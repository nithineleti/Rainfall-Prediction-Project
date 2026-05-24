# Visualization Platform Guide

This guide explains how to use the interactive visualization platform to explore watershed data, view predictions, and analyze groundwater potential.

---

## Overview

The Watershed Prioritization Platform provides:
- **Analytics Dashboard**: Summary statistics and charts
- **Watershed Explorer**: Interactive table and map
- **Prediction Tool**: Real-time groundwater potential predictions
- **Interactive Maps**: Spatial visualization with Leaflet

---

## Accessing the Platform

### Start the Application

**1. Start Backend Server**:
```bash
cd backend
python run.py
```

**2. Start Frontend Server**:
```bash
cd app-frontend
npm run dev
```

**3. Open Browser**:
Navigate to: **http://localhost:5173**

---

## Platform Features

### 1. Analytics Dashboard

**Purpose**: Overview of watershed statistics and model performance

#### Summary Cards

**Location**: Top of Analytics tab

**Displays**:
- **Total Watersheds**: Count of all watersheds
- **High Priority**: Number of high-priority watersheds
- **Total Area**: Combined area in km²
- **Mean GW Potential**: Average groundwater potential score

**Example**:
```
┌─────────────────────┐  ┌─────────────────────┐
│ Total Watersheds    │  │ High Priority       │
│      520            │  │      145 (28%)      │
└─────────────────────┘  └─────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐
│ Total Area          │  │ Mean GW Potential   │
│   12,345.67 km²     │  │      0.62 (62%)     │
└─────────────────────┘  └─────────────────────┘
```

#### Priority Distribution Chart

**Type**: Pie Chart

**Shows**: Distribution of watersheds by priority class

**Interpretation**:
- **Green segment**: High priority watersheds
- **Orange segment**: Medium priority watersheds
- **Red segment**: Low priority watersheds

**Hover**: View count and percentage for each class

**Use Cases**:
- Quick overview of priority distribution
- Identify proportion needing immediate attention
- Compare relative priorities

#### Feature Importance Chart

**Type**: Horizontal Bar Chart

**Shows**: Top 10 most important features (SHAP values)

**Features Displayed**:
1. Topographic Wetness Index (TWI)
2. Flow Accumulation
3. Drainage Density
4. Annual Rainfall
5. Elevation
6. LULC - Agriculture %
7. Slope
8. Distance to Streams
9. LULC - Forest %
10. Geology - Lithology

**Interpretation**:
- Longer bars = More important features
- Top features drive model predictions
- Understand what influences groundwater potential

**Use Cases**:
- Understand model behavior
- Identify key factors for groundwater
- Guide field investigations

#### Model Performance Metrics

**Displays**:
- **Accuracy**: 79.6%
- **Precision**: 82.0%
- **Recall**: 76.0%
- **F1-Score**: 79.0%
- **ROC-AUC**: 85.0%

**Color Coding**:
- Green: Good performance (>75%)
- Orange: Moderate (60-75%)
- Red: Needs improvement (<60%)

**Interpretation**:
- **Accuracy**: Overall correctness
- **Precision**: Of predicted high potential, how many are truly high
- **Recall**: Of actual high potential, how many we detected
- **F1-Score**: Balance between precision and recall
- **ROC-AUC**: Model's ability to distinguish classes

---

### 2. Watershed Explorer

**Purpose**: Browse and analyze individual watersheds

#### Watershed Table

**Location**: Watersheds tab

**Columns**:
- **ID**: Watershed identifier
- **Area (km²)**: Watershed area
- **Priority Class**: High/Medium/Low
- **Priority Score**: Numerical score (0-1)
- **Mean Elevation**: Average elevation (m)
- **Mean Slope**: Average slope (degrees)
- **Drainage Density**: km/km²
- **Forest %**: Forest cover percentage
- **Agriculture %**: Agricultural land percentage
- **Rainfall**: Mean annual rainfall (mm)
- **GW Potential**: Mean groundwater potential

**Features**:

**Pagination**:
- Default: 20 watersheds per page
- Options: 10, 20, 50, 100 per page
- Navigate with Previous/Next buttons

**Sorting**:
- Click column headers to sort
- Click again to reverse order
- Default: Sorted by priority score (descending)

**Filtering**:
- **Priority Filter**: Show only High/Medium/Low
- **Area Filter**: Minimum and maximum area
- **Search**: Search by watershed ID

**Example Usage**:
```
1. Click "Priority" dropdown → Select "High"
2. Set Min Area: 50 km²
3. Sort by "Area (km²)" (descending)
→ Shows large, high-priority watersheds
```

#### Watershed Detail Panel

**Trigger**: Click any row in the table

**Tabs**:

**1. Overview Tab**:
- Basic Info: ID, area, perimeter, priority
- Morphometry: Shape metrics
- Priority: Score, rank, percentile

**2. Features Tab**:
- Terrain: Elevation, slope, aspect, relief
- Drainage: Density, frequency, bifurcation ratio
- Land Cover: Forest, agriculture, built-up, water percentages
- Climate: Rainfall statistics
- Groundwater: Prediction statistics

**3. Map Tab**:
- Watershed boundary displayed on map
- Surrounding context
- Stream network
- Zoom to watershed extent

**4. Recommendations Tab**:
- Priority-based recommendations
- Suggested interventions
- Management strategies

**Example Recommendations**:
```
High Priority Watershed:
✓ Immediate development recommended
✓ Suitable for groundwater recharge structures
✓ High success probability for borewells
✓ Consider rainwater harvesting

Medium Priority Watershed:
→ Moderate development potential
→ Detailed site investigation recommended
→ Consider pilot projects
→ Monitor existing wells

Low Priority Watershed:
✗ Not recommended for immediate development
✗ Focus on conservation measures
✗ Consider surface water alternatives
```

---

### 3. Interactive Map

**Purpose**: Spatial visualization of watersheds

**Features**:

**Base Layers**:
- OpenStreetMap (default)
- Satellite imagery
- Terrain view

**Overlays**:
- Watershed boundaries (colored by priority)
- Stream network
- Well locations
- Prediction raster

**Color Scheme**:
- **Green**: High priority watersheds
- **Orange**: Medium priority watersheds
- **Red**: Low priority watersheds

**Interactions**:

**Click Watershed**:
- Opens detail panel
- Highlights boundary
- Shows popup with key info

**Hover**:
- Shows watershed ID and priority
- Tooltip follows cursor

**Zoom Controls**:
- Zoom in/out buttons
- Mouse wheel zoom
- Double-click zoom
- Pinch zoom (touch devices)

**Search**:
- Search by coordinates
- Jump to location
- Add custom markers

**Legend**:
- Priority class colors
- Feature symbols
- Scale bar

---

### 4. Prediction Tool

**Purpose**: Get real-time groundwater potential predictions for any location

**Location**: Predictions tab

**Usage**:

**1. Enter Coordinates**:
```
Longitude: 80.1234 (decimal degrees, -180 to 180)
Latitude:  13.4567 (decimal degrees, -90 to 90)
```

**2. Click "Predict"**

**3. View Results**:

**Prediction Card**:
```
┌──────────────────────────────────────┐
│  Groundwater Potential Prediction    │
├──────────────────────────────────────┤
│  Location: 80.1234°E, 13.4567°N     │
│  Prediction: HIGH                    │
│  Probability: 78%                    │
│  Confidence: High                    │
└──────────────────────────────────────┘
```

**Feature Values**:
- Elevation: 234.5 m
- Slope: 12.3°
- TWI: 8.9
- Flow Accumulation: 1,234.5
- Drainage Density: 2.45 km/km²
- Forest Cover: 45.2%
- Agriculture: 32.1%
- Rainfall: 1,200.5 mm
- ... (all 17 features)

**Map View**:
- Location marked on map
- Surrounding watershed context
- Prediction overlay

**Recommendation**:
```
✓ High probability of groundwater potential
✓ Suitable for borewell development
✓ Expected yield: >500 L/day
✓ Recommended depth: 50-100m
```

**Batch Predictions** (Future):
- Upload CSV with coordinates
- Get predictions for multiple points
- Download results

---

## Common Workflows

### Workflow 1: Identify High-Priority Watersheds

**Goal**: Find watersheds for immediate development

**Steps**:
1. Go to **Watersheds** tab
2. Select **Priority: High** in filter
3. Sort by **Priority Score** (descending)
4. Review top watersheds in table
5. Click watershed to view details
6. Check **Recommendations** tab
7. Export list for field team

**Outcome**: List of high-priority watersheds with details

---

### Workflow 2: Analyze Specific Location

**Goal**: Assess groundwater potential for a proposed borewell site

**Steps**:
1. Go to **Predictions** tab
2. Enter site coordinates
3. Click **Predict**
4. Review prediction result
5. Check feature values
6. View location on map
7. Read recommendation
8. Download report

**Outcome**: Prediction and recommendation for the site

---

### Workflow 3: Compare Watersheds

**Goal**: Compare multiple watersheds for selection

**Steps**:
1. Go to **Watersheds** tab
2. Select watersheds of interest (click rows)
3. View details for each
4. Compare metrics:
   - Priority scores
   - Areas
   - Feature values
   - GW potential
5. Check map locations
6. Select best candidate

**Outcome**: Informed selection of watershed

---

### Workflow 4: Understand Model Predictions

**Goal**: Learn what drives model decisions

**Steps**:
1. Go to **Analytics** tab
2. View **Feature Importance** chart
3. Note top features
4. Go to **Predictions** tab
5. Make a prediction
6. Check feature values for those top features
7. Understand their contribution

**Outcome**: Better understanding of model behavior

---

## Tips & Best Practices

### For Analysts

1. **Use filters effectively**: Narrow down watersheds before detailed analysis
2. **Sort by priority score**: Focus on highest/lowest first
3. **Check multiple features**: Don't rely on single metric
4. **Validate with map**: Visual inspection complements data
5. **Export data**: Download for offline analysis

### For Field Teams

1. **Use prediction tool**: Pre-screen sites before visits
2. **Check recommendations**: Follow priority-based guidance
3. **View in map context**: Understand terrain and access
4. **Note feature values**: Share with technical team
5. **Verify predictions**: Report back actual yields

### For Decision Makers

1. **Review analytics**: Get overview before details
2. **Focus on high priority**: Allocate resources wisely
3. **Compare areas**: Choose best ROI watersheds
4. **Check model performance**: Trust well-performing models
5. **Request updates**: Retrain model with new data

---

## Data Export

### Export Watershed Data

**From Table**:
1. Apply filters as needed
2. Click **Export** button
3. Choose format: CSV, Excel, GeoJSON
4. Download file

**From Map**:
1. Select watersheds on map
2. Right-click → **Export Selection**
3. Choose format
4. Download file

### Export Predictions

**Single Prediction**:
1. Make prediction
2. Click **Download Report**
3. Choose format: PDF, JSON
4. Save file

**Batch Predictions** (Future):
1. Upload coordinates CSV
2. Run batch prediction
3. Download results CSV

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab 1` | Analytics tab |
| `Tab 2` | Watersheds tab |
| `Tab 3` | Predictions tab |
| `Ctrl + F` | Focus search box |
| `Esc` | Close detail panel |
| `←/→` | Navigate table pages |
| `↑/↓` | Navigate table rows |
| `Enter` | Open selected row |
| `+/-` | Zoom map in/out |

---

## Mobile Usage

The platform is responsive and works on mobile devices:

**Tablet**:
- Full functionality
- Touch-friendly controls
- Swipe to navigate

**Phone**:
- Vertical layout
- Stacked panels
- Optimized charts
- Touch zoom on maps

**Limitations**:
- Smaller charts
- Limited table columns
- Reduced map detail

**Best on**: Desktop or tablet (10"+ screen)

---

## Troubleshooting

### Charts Not Loading

**Issue**: Charts show as blank or loading spinner

**Solutions**:
- Refresh page (F5)
- Check backend is running
- Clear browser cache
- Check browser console for errors

### Map Not Displaying

**Issue**: Map area is blank

**Solutions**:
- Check internet connection (base maps require internet)
- Allow location access if prompted
- Try different base layer
- Check browser WebGL support

### Slow Performance

**Issue**: App feels sluggish

**Solutions**:
- Reduce page size (show 10 instead of 100 watersheds)
- Close unused browser tabs
- Clear browser cache
- Use Chrome or Firefox (best performance)
- Disable browser extensions

### Prediction Failed

**Issue**: "Prediction failed" error

**Solutions**:
- Check coordinates are valid (-180 to 180, -90 to 90)
- Ensure backend is running
- Check location is within study area
- Try again (temporary network issue)

---

## Additional Resources

- [Frontend Architecture](../architecture/FRONTEND.md)
- [API Documentation](../api/ENDPOINTS.md)
- [Running Frontend Guide](./RUNNING_FRONTEND.md)
- [Running Backend Guide](./RUNNING_BACKEND.md)

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
