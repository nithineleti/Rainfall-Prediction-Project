# Running the Frontend

This guide explains how to set up, run, and develop the React TypeScript frontend application.

---

## Prerequisites

- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)
- **Git**: For version control
- **Backend**: Backend server must be running (see [Running Backend](./RUNNING_BACKEND.md))

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PAVANKUMARELETI/watershed-up.git
cd watershed-up
```

### 2. Navigate to Frontend Directory

```bash
cd app-frontend
```

### 3. Install Dependencies

```bash
npm install
```

**This installs**:
- React 18.2+
- TypeScript 5.0+
- Vite 5.0+
- Material-UI (MUI) v5
- Recharts 2.10+
- Leaflet + React-Leaflet
- Axios 1.6+

### 4. Verify Installation

```bash
npm list react react-dom typescript vite
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `app-frontend/` directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Application Settings
VITE_APP_TITLE=Watershed Prioritization
VITE_APP_VERSION=2.0.0

# Map Configuration
VITE_MAP_CENTER_LAT=13.0
VITE_MAP_CENTER_LON=80.0
VITE_MAP_DEFAULT_ZOOM=10
```

### API Base URL

The frontend connects to the backend via the URL specified in `.env`:

```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## Running the Development Server

### Start Dev Server

```bash
npm run dev
```

**Output**:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h to show help
```

### Access the Application

Open your browser and visit: **http://localhost:5173**

### Hot Module Replacement (HMR)

Vite provides instant hot reload:
- Edit any `.tsx` or `.ts` file
- Changes appear immediately in the browser
- No manual refresh needed

---

## Building for Production

### Create Production Build

```bash
npm run build
```

**Output directory**: `dist/`

**Build includes**:
- Minified JavaScript bundles
- Optimized CSS
- Tree-shaken dependencies
- Source maps (optional)

### Preview Production Build

```bash
npm run preview
```

This serves the production build locally for testing.

---

## Development Workflow

### Project Structure

```
app-frontend/
├── public/              # Static assets
│   └── vite.svg
├── src/
│   ├── App.tsx          # Main app component
│   ├── App.css          # Global styles
│   ├── main.tsx         # Entry point
│   ├── components/      # React components
│   │   ├── Analytics/
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   ├── PriorityDistribution.tsx
│   │   │   ├── FeatureImportance.tsx
│   │   │   └── ModelPerformance.tsx
│   │   ├── Watersheds/
│   │   │   ├── WatershedList.tsx
│   │   │   ├── WatershedDetail.tsx
│   │   │   └── WatershedMap.tsx
│   │   ├── Predictions/
│   │   │   ├── PredictionForm.tsx
│   │   │   └── PredictionResult.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       └── LoadingSpinner.tsx
│   ├── services/        # API services
│   │   ├── api.ts
│   │   ├── watershedService.ts
│   │   ├── predictionService.ts
│   │   └── analyticsService.ts
│   ├── types/           # TypeScript types
│   │   ├── watershed.ts
│   │   ├── prediction.ts
│   │   └── analytics.ts
│   ├── hooks/           # Custom React hooks
│   │   ├── useWatersheds.ts
│   │   └── usePrediction.ts
│   ├── context/         # React Context
│   │   └── WatershedContext.tsx
│   └── utils/           # Utility functions
│       ├── formatters.ts
│       └── validators.ts
├── index.html           # HTML template
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite configuration
└── README.md
```

### Adding a New Component

**1. Create component file**:

```bash
mkdir -p src/components/NewFeature
touch src/components/NewFeature/NewFeature.tsx
```

**2. Write component**:

```typescript
// src/components/NewFeature/NewFeature.tsx
import React from 'react';
import { Box, Typography } from '@mui/material';

interface NewFeatureProps {
  title: string;
}

const NewFeature: React.FC<NewFeatureProps> = ({ title }) => {
  return (
    <Box>
      <Typography variant="h4">{title}</Typography>
    </Box>
  );
};

export default NewFeature;
```

**3. Use in App**:

```typescript
import NewFeature from './components/NewFeature/NewFeature';

function App() {
  return (
    <div>
      <NewFeature title="My New Feature" />
    </div>
  );
}
```

### Creating a Custom Hook

```typescript
// src/hooks/useWatersheds.ts
import { useState, useEffect } from 'react';
import { watershedService } from '../services/watershedService';
import { Watershed } from '../types/watershed';

export const useWatersheds = (page: number, pageSize: number) => {
  const [data, setData] = useState<Watershed[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await watershedService.getWatersheds(page, pageSize);
        setData(response.watersheds);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [page, pageSize]);

  return { data, loading, error };
};
```

### Adding API Service

```typescript
// src/services/newService.ts
import apiClient from './api';

export const newService = {
  async getData(): Promise<any> {
    const response = await apiClient.get('/api/new-endpoint');
    return response.data;
  },

  async postData(data: any): Promise<any> {
    const response = await apiClient.post('/api/new-endpoint', data);
    return response.data;
  },
};
```

---

## Styling

### Material-UI Theme

Customize theme in `src/main.tsx`:

```typescript
import { createTheme, ThemeProvider } from '@mui/material/styles';

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
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Disable uppercase
        },
      },
    },
  },
});

<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>
```

### CSS Modules

Create component-specific styles:

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
```

Use in component:

```typescript
import styles from './WatershedList.module.css';

<div className={styles.container}>
  <table className={styles.table}>...</table>
</div>
```

### Global Styles

Edit `src/App.css`:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f5f5;
}
```

---

## TypeScript

### Type Definitions

Define types in `src/types/`:

```typescript
// src/types/watershed.ts
export interface Watershed {
  watershed_id: number;
  area_km2: number;
  priority_class: 'High' | 'Medium' | 'Low';
  priority_score: number;
}

export interface WatershedListResponse {
  total: number;
  page: number;
  watersheds: Watershed[];
}
```

### Type Checking

```bash
# Check types
npm run type-check

# Or with tsc directly
npx tsc --noEmit
```

### Strict Mode

Enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

---

## Testing

### Run Tests

```bash
npm run test
```

### Test with Coverage

```bash
npm run test:coverage
```

### Unit Test Example

```typescript
// src/components/WatershedList.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import WatershedList from './WatershedList';

describe('WatershedList', () => {
  it('renders watershed table', () => {
    render(<WatershedList />);
    expect(screen.getByText('Watersheds')).toBeInTheDocument();
  });

  it('displays loading spinner', () => {
    render(<WatershedList loading={true} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
```

### Integration Test Example

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

## Debugging

### Browser DevTools

**React DevTools Extension**:
- Install React DevTools for Chrome/Firefox
- Inspect component hierarchy
- View props and state
- Profile performance

**Redux DevTools** (if using Redux):
- Time-travel debugging
- Action history
- State inspection

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/app-frontend/src"
    }
  ]
}
```

### Console Logging

```typescript
// Use console.log during development
console.log('Watershed data:', watersheds);

// Remove before production or use conditional logging
if (import.meta.env.DEV) {
  console.log('Debug info');
}
```

---

## Performance Optimization

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const AnalyticsDashboard = lazy(() => import('./components/Analytics/AnalyticsDashboard'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AnalyticsDashboard />
    </Suspense>
  );
}
```

### Memoization

```typescript
import { useMemo, useCallback } from 'react';

const sortedData = useMemo(() => {
  return data.sort((a, b) => b.score - a.score);
}, [data]);

const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);
```

### React.memo

```typescript
import React from 'react';

const ExpensiveComponent = React.memo(({ data }) => {
  // Component only re-renders if data changes
  return <div>{data}</div>;
});
```

---

## Common Issues

### 1. CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Ensure backend CORS is configured:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Match frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Module Not Found

**Error**: `Cannot find module './Component'`

**Solution**:
```bash
# Check file exists
ls src/components/Component.tsx

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### 3. TypeScript Errors

**Error**: `Property 'x' does not exist on type 'Y'`

**Solution**: Add proper type definitions:
```typescript
interface MyType {
  x: string;  // Add missing property
}
```

### 4. Build Errors

**Error**: `Build failed`

**Solution**:
```bash
# Clear cache
rm -rf node_modules/.vite

# Rebuild
npm run build
```

### 5. API Connection Failed

**Error**: `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution**:
- Check backend is running: `curl http://localhost:8000/api/health`
- Verify API URL in `.env`
- Check firewall/antivirus settings

---

## Code Quality

### Linting

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

### Formatting

```bash
# Format with Prettier
npm run format

# Check formatting
npm run format:check
```

### Pre-commit Hooks

Install Husky for git hooks:

```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "npm run lint && npm run type-check"
```

---

## Deployment

### Build Production Assets

```bash
npm run build
```

### Serve with Nginx

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/watershed-app/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Deployment

**Dockerfile**:
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

**Build and run**:
```bash
docker build -t watershed-frontend .
docker run -p 80:80 watershed-frontend
```

---

## Environment-Specific Builds

### Development

```bash
npm run dev
```

Uses `.env.development`:
```env
VITE_API_URL=http://localhost:8000
```

### Production

```bash
npm run build
```

Uses `.env.production`:
```env
VITE_API_URL=https://api.example.com
```

---

## Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Material-UI Documentation](https://mui.com/)
- [Project Architecture](../architecture/FRONTEND.md)

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
