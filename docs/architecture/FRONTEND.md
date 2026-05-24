# Frontend Architecture

## Overview

The frontend is a modern **React 18** single-page application (SPA) built with **TypeScript** and **Vite**. It provides an interactive dashboard for watershed analysis, predictions, and data visualization with real-time updates and responsive design.

**Tech Stack**:
- **Framework**: React 18.2+ with TypeScript
- **Build Tool**: Vite 5.0+
- **UI Library**: Material-UI (MUI) v5
- **Charts**: Recharts 2.10+
- **Maps**: Leaflet 1.9+ with React-Leaflet
- **HTTP Client**: Axios 1.6+
- **State Management**: React Context API + Hooks
- **Styling**: CSS Modules + MUI Theme

---

## Project Structure

```
app-frontend/
├── public/
│   └── vite.svg                # Favicon
├── src/
│   ├── App.tsx                 # Main application component
│   ├── App.css                 # Global styles
│   ├── main.tsx                # Application entry point
│   ├── vite-env.d.ts          # Vite type definitions
│   ├── components/
│   │   ├── Analytics/
│   │   │   ├── AnalyticsDashboard.tsx      # Main analytics view
│   │   │   ├── PriorityDistribution.tsx    # Priority pie chart
│   │   │   ├── FeatureImportance.tsx       # Feature importance bar chart
│   │   │   ├── ModelPerformance.tsx        # Model metrics display
│   │   │   └── SummaryCards.tsx            # Key metrics cards
│   │   ├── Watersheds/
│   │   │   ├── WatershedList.tsx           # Watershed table/grid
│   │   │   ├── WatershedDetail.tsx         # Detail panel
│   │   │   ├── WatershedMap.tsx            # Interactive map
│   │   │   └── WatershedFilters.tsx        # Filter controls
│   │   ├── Predictions/
│   │   │   ├── PredictionForm.tsx          # Prediction input form
│   │   │   ├── PredictionResult.tsx        # Prediction display
│   │   │   └── PredictionMap.tsx           # Map with prediction
│   │   ├── Layout/
│   │   │   ├── Header.tsx                  # App header/navbar
│   │   │   ├── Sidebar.tsx                 # Navigation sidebar
│   │   │   ├── Footer.tsx                  # App footer
│   │   │   └── LoadingSpinner.tsx          # Loading component
│   │   └── Common/
│   │       ├── ErrorBoundary.tsx           # Error handling
│   │       ├── InfoCard.tsx                # Reusable card
│   │       └── TabPanel.tsx                # Tab panel component
│   ├── services/
│   │   ├── api.ts              # Axios instance configuration
│   │   ├── watershedService.ts # Watershed API calls
│   │   ├── predictionService.ts # Prediction API calls
│   │   └── analyticsService.ts # Analytics API calls
│   ├── types/
│   │   ├── watershed.ts        # Watershed types
│   │   ├── prediction.ts       # Prediction types
│   │   └── analytics.ts        # Analytics types
│   ├── hooks/
│   │   ├── useWatersheds.ts    # Watershed data hook
│   │   ├── usePrediction.ts    # Prediction hook
│   │   └── useAnalytics.ts     # Analytics hook
│   ├── context/
│   │   ├── WatershedContext.tsx # Watershed state management
│   │   └── ThemeContext.tsx     # Theme configuration
│   ├── utils/
│   │   ├── formatters.ts       # Data formatting utilities
│   │   ├── validators.ts       # Form validation
│   │   └── constants.ts        # Application constants
│   └── assets/
│       ├── images/             # Image assets
│       └── styles/             # Global styles
├── index.html                  # HTML entry point
├── package.json                # Dependencies
├── tsconfig.json              # TypeScript config
├── vite.config.ts             # Vite configuration
└── README.md                  # Frontend documentation
```

---

## Core Components

### 1. Application Entry Point

#### `main.tsx`

Bootstrap the React application with providers and routing.

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

#### `App.tsx`

Main application component with routing and layout.

```typescript
import { useState } from 'react';
import { Container, Box, Tabs, Tab } from '@mui/material';
import Header from './components/Layout/Header';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';
import WatershedList from './components/Watersheds/WatershedList';
import PredictionForm from './components/Predictions/PredictionForm';
import { WatershedProvider } from './context/WatershedContext';

function App() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <WatershedProvider>
      <Header />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Analytics" />
            <Tab label="Watersheds" />
            <Tab label="Predictions" />
          </Tabs>
        </Box>
        
        {activeTab === 0 && <AnalyticsDashboard />}
        {activeTab === 1 && <WatershedList />}
        {activeTab === 2 && <PredictionForm />}
      </Container>
    </WatershedProvider>
  );
}

export default App;
```

---

### 2. Analytics Components

#### `AnalyticsDashboard.tsx`

Main analytics view with summary cards and charts.

**Features**:
- Summary statistics cards (total watersheds, high priority count, etc.)
- Priority distribution pie chart
- Feature importance bar chart
- Model performance metrics
- Responsive grid layout

**Key Sections**:
```typescript
<Grid container spacing={3}>
  {/* Summary Cards */}
  <Grid item xs={12}>
    <SummaryCards data={summaryData} />
  </Grid>
  
  {/* Charts Row */}
  <Grid item xs={12} md={6}>
    <PriorityDistribution data={priorityData} />
  </Grid>
  <Grid item xs={12} md={6}>
    <FeatureImportance data={featureData} />
  </Grid>
  
  {/* Model Performance */}
  <Grid item xs={12}>
    <ModelPerformance metrics={modelMetrics} />
  </Grid>
</Grid>
```

#### `PriorityDistribution.tsx`

Pie chart showing distribution of watershed priorities.

**Chart Configuration**:
- Recharts PieChart component
- Custom colors for priority levels
- Interactive tooltips
- Legend with percentages

#### `FeatureImportance.tsx`

Bar chart displaying feature importance from SHAP analysis.

**Features**:
- Horizontal bar chart
- Top 10 features
- Color gradient based on importance
- Interactive hover effects

#### `ModelPerformance.tsx`

Display model performance metrics (accuracy, precision, recall, F1).

**Layout**:
- Grid of metric cards
- Color-coded values
- Comparison to baseline

---

### 3. Watershed Components

#### `WatershedList.tsx`

Paginated table/grid of watersheds with filtering and sorting.

**Features**:
- Material-UI DataGrid
- Server-side pagination
- Column sorting
- Priority filtering
- Search functionality
- Export to CSV (future)

**State Management**:
```typescript
const [page, setPage] = useState(1);
const [pageSize, setPageSize] = useState(20);
const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
const { watersheds, loading } = useWatersheds(page, pageSize, priorityFilter);
```

#### `WatershedDetail.tsx`

Detailed information panel for selected watershed.

**Displayed Information**:
- Basic info (ID, area, perimeter)
- Priority classification and score
- Feature values (elevation, slope, LULC, rainfall)
- Geometry visualization
- Recommendations

**Tabs**:
1. **Overview**: Key metrics and priority
2. **Features**: All feature values
3. **Map**: Watershed boundary on map
4. **Analysis**: Detailed analysis and recommendations

#### `WatershedMap.tsx`

Interactive Leaflet map displaying watersheds.

**Features**:
- Base layer selection (OSM, satellite, terrain)
- Watershed boundaries (GeoJSON overlay)
- Color coding by priority
- Click to view details
- Zoom controls
- Search by coordinates

**Map Configuration**:
```typescript
<MapContainer center={[13.0, 80.0]} zoom={10}>
  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
  <GeoJSON 
    data={watershedData}
    style={(feature) => ({
      color: getPriorityColor(feature.properties.priority_class),
      weight: 2,
      fillOpacity: 0.5
    })}
    onEachFeature={(feature, layer) => {
      layer.on('click', () => setSelectedWatershed(feature));
    }}
  />
</MapContainer>
```

---

### 4. Prediction Components

#### `PredictionForm.tsx`

Form for submitting prediction requests.

**Form Fields**:
- Longitude input (with validation)
- Latitude input (with validation)
- Optional: Upload coordinates file
- Submit button

**Validation**:
```typescript
const validateCoordinates = (lon: number, lat: number) => {
  if (lon < -180 || lon > 180) return 'Invalid longitude';
  if (lat < -90 || lat > 90) return 'Invalid latitude';
  return null;
};
```

**Submission**:
```typescript
const handleSubmit = async () => {
  setLoading(true);
  try {
    const result = await predictionService.predictPoint(lon, lat);
    setPredictionResult(result);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

#### `PredictionResult.tsx`

Display prediction results with visualization.

**Sections**:
1. **Prediction**: High/Low groundwater potential
2. **Probability**: Confidence score (0-1)
3. **Feature Values**: All feature values at the point
4. **Map**: Location on map with prediction overlay
5. **Recommendations**: Based on prediction

**Visual Elements**:
- Color-coded result (green for high, red for low)
- Probability gauge/progress bar
- Feature value table
- Location marker on map

---

### 5. Layout Components

#### `Header.tsx`

Application header with navigation and branding.

**Elements**:
- App logo and title
- Navigation tabs (Analytics, Watersheds, Predictions)
- Theme toggle (light/dark mode)
- User menu (future: login/logout)

#### `Sidebar.tsx`

Navigation sidebar (alternative to header tabs).

**Features**:
- Collapsible drawer
- Navigation links
- Active route highlighting
- Quick actions

#### `LoadingSpinner.tsx`

Reusable loading indicator.

**Variants**:
- Full-page overlay
- Inline spinner
- Progress bar

---

## State Management

### Context API

#### `WatershedContext.tsx`

Global state for watershed data and selection.

```typescript
interface WatershedContextType {
  watersheds: Watershed[];
  selectedWatershed: Watershed | null;
  loading: boolean;
  error: string | null;
  setSelectedWatershed: (watershed: Watershed | null) => void;
  refreshWatersheds: () => Promise<void>;
}

export const WatershedProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [watersheds, setWatersheds] = useState<Watershed[]>([]);
  const [selectedWatershed, setSelectedWatershed] = useState<Watershed | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshWatersheds = async () => {
    setLoading(true);
    try {
      const data = await watershedService.getWatersheds();
      setWatersheds(data.watersheds);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <WatershedContext.Provider value={{
      watersheds,
      selectedWatershed,
      loading,
      error,
      setSelectedWatershed,
      refreshWatersheds
    }}>
      {children}
    </WatershedContext.Provider>
  );
};
```

### Custom Hooks

#### `useWatersheds.ts`

Hook for fetching and managing watershed data.

```typescript
export const useWatersheds = (page: number, pageSize: number, priority?: string) => {
  const [data, setData] = useState<WatershedListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWatersheds = async () => {
      setLoading(true);
      try {
        const response = await watershedService.getWatersheds(page, pageSize, priority);
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWatersheds();
  }, [page, pageSize, priority]);

  return { data, loading, error };
};
```

---

## API Services

### `api.ts` - Axios Configuration

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor (for auth tokens, etc.)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### `watershedService.ts`

```typescript
import apiClient from './api';
import { Watershed, WatershedListResponse } from '../types/watershed';

export const watershedService = {
  async getWatersheds(page = 1, pageSize = 20, priority?: string): Promise<WatershedListResponse> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (priority) params.append('priority', priority);
    
    const response = await apiClient.get(`/api/watersheds?${params}`);
    return response.data;
  },

  async getWatershedDetail(id: number): Promise<Watershed> {
    const response = await apiClient.get(`/api/watersheds/${id}`);
    return response.data;
  },

  async getWatershedGeometry(id: number): Promise<GeoJSON.Feature> {
    const response = await apiClient.get(`/api/watersheds/${id}/geometry`);
    return response.data;
  },
};
```

### `predictionService.ts`

```typescript
import apiClient from './api';
import { PredictionRequest, PredictionResponse } from '../types/prediction';

export const predictionService = {
  async predictPoint(lon: number, lat: number): Promise<PredictionResponse> {
    const response = await apiClient.post('/api/predictions/predict', { longitude: lon, latitude: lat });
    return response.data;
  },

  async getPredictionMap(): Promise<Blob> {
    const response = await apiClient.get('/api/predictions/map', { responseType: 'blob' });
    return response.data;
  },
};
```

---

## TypeScript Types

### `watershed.ts`

```typescript
export interface Watershed {
  watershed_id: number;
  area_km2: number;
  perimeter_km: number;
  priority_class: 'High' | 'Medium' | 'Low';
  priority_score: number;
  mean_elevation: number;
  mean_slope: number;
  drainage_density: number;
  lulc_forest_pct: number;
  lulc_agriculture_pct: number;
  mean_rainfall: number;
  geometry?: GeoJSON.Geometry;
}

export interface WatershedListResponse {
  total: number;
  page: number;
  page_size: number;
  watersheds: Watershed[];
}
```

### `prediction.ts`

```typescript
export interface PredictionRequest {
  longitude: number;
  latitude: number;
}

export interface PredictionResponse {
  longitude: number;
  latitude: number;
  probability: number;
  prediction: 'High' | 'Low';
  features: Record<string, number>;
}
```

---

## Styling

### Material-UI Theme

```typescript
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    success: { main: '#2e7d32' },
    warning: { main: '#ed6c02' },
    error: { main: '#d32f2f' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 500 },
    h2: { fontSize: '2rem', fontWeight: 500 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none' },
      },
    },
  },
});
```

### CSS Modules

Component-specific styles using CSS Modules:

```css
/* WatershedList.module.css */
.container {
  padding: 24px;
  background: white;
  border-radius: 8px;
}

.table {
  min-height: 400px;
}

.filterBar {
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
}
```

---

## Performance Optimization

### 1. Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const AnalyticsDashboard = lazy(() => import('./components/Analytics/AnalyticsDashboard'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AnalyticsDashboard />
    </Suspense>
  );
}
```

### 2. Memoization

```typescript
import { useMemo } from 'react';

const sortedWatersheds = useMemo(() => {
  return watersheds.sort((a, b) => b.priority_score - a.priority_score);
}, [watersheds]);
```

### 3. Virtual Scrolling

For large lists, use react-window or react-virtualized.

---

## Build & Deployment

### Development

```bash
npm run dev
# Runs on http://localhost:5173
```

### Production Build

```bash
npm run build
# Output: dist/
```

### Preview Production Build

```bash
npm run preview
```

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Testing

### Unit Tests (Vitest)

```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import WatershedList from './WatershedList';

describe('WatershedList', () => {
  it('renders watershed table', () => {
    render(<WatershedList />);
    expect(screen.getByText('Watersheds')).toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useWatersheds } from '../hooks/useWatersheds';

describe('useWatersheds', () => {
  it('fetches watersheds', async () => {
    const { result } = renderHook(() => useWatersheds(1, 20));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeDefined();
    });
  });
});
```

---

## Best Practices

### 1. Component Design

✅ **Do**:
- Keep components small and focused
- Use functional components with hooks
- Extract reusable logic to custom hooks
- Use TypeScript for type safety

❌ **Don't**:
- Create large monolithic components
- Use class components (unless necessary)
- Mix business logic with UI

### 2. State Management

✅ **Do**:
- Use Context for global state
- Keep local state when possible
- Use custom hooks for data fetching

❌ **Don't**:
- Overuse global state
- Prop drill through many levels

### 3. Performance

✅ **Do**:
- Use React.memo for expensive components
- Implement code splitting
- Optimize images and assets

❌ **Don't**:
- Re-render unnecessarily
- Load all data upfront

---

## Troubleshooting

### Common Issues

**1. CORS Errors**
```
Solution: Ensure backend CORS origins include http://localhost:5173
```

**2. Build Errors**
```
Solution: Clear node_modules and reinstall: rm -rf node_modules && npm install
```

**3. Type Errors**
```
Solution: Check TypeScript version and update @types packages
```

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
