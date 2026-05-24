# Frontend Quick Start Guide

## ✅ Setup Complete!

Your React + TypeScript frontend has been configured and is ready to use.

---

## 🚀 How to Run

### Option 1: Batch File (Easiest)
```bash
# From project root
run_frontend.bat
```

### Option 2: PowerShell Script
```powershell
# From project root
.\run_frontend.ps1
```

### Option 3: Manual (if Node.js is in PATH)
```bash
cd app-frontend
npm install
npm run dev
```

---

## 📦 What Was Added

### New Files
- `app-frontend/` - Complete React application
  - `src/App.tsx` - Main application component
  - `src/components/MapView.tsx` - MapLibre GL component
  - `src/pages/Home.tsx` - Home page
  - `src/styles/index.css` - Tailwind CSS styles
  - `vite.config.ts` - Vite configuration with API proxy
  - `package.json` - Dependencies
  
- `run_frontend.bat` - Windows batch launcher
- `run_frontend.ps1` - PowerShell launcher

### Updated Files
- `.gitignore` - Added node_modules/, dist/, build/

---

## 🔧 Configuration

### Vite Config (`app-frontend/vite.config.ts`)
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:8000',
    '/tiles': 'http://localhost:8000'
  }
}
```

**This means:**
- Frontend runs on: `http://localhost:5173`
- API calls to `/api/*` are proxied to backend on port 8000
- Map tiles from `/tiles/*` are proxied to backend

---

## 🎨 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.2.0 |
| Language | TypeScript | 5.3.3 |
| Build Tool | Vite | 5.0.0 |
| Styling | Tailwind CSS | 3.4.14 |
| Maps | MapLibre GL | 2.4.0 |
| HTTP | Axios | 1.4.0 |
| State | TanStack Query | 4.36.0 |

---

## 📁 Project Structure

```
app-frontend/
├── src/
│   ├── components/
│   │   └── MapView.tsx       # Map component
│   ├── pages/
│   │   └── Home.tsx          # Home page
│   ├── styles/
│   │   └── index.css         # Global styles
│   ├── App.tsx               # Root component
│   └── main.tsx              # Entry point
├── public/                   # Static assets
├── index.html                # HTML template
├── package.json              # Dependencies
├── vite.config.ts            # Vite config
├── tailwind.config.js        # Tailwind config
└── tsconfig.json             # TypeScript config
```

---

## 🔌 Connecting to Backend

### Step 1: Start Backend (Port 8000)
```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload
```

### Step 2: Start Frontend (Port 5173)
```bash
# Terminal 2
run_frontend.bat
```

### Step 3: Access
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🛠️ Development Commands

### Install Dependencies
```bash
cd app-frontend
npm install
```

### Start Dev Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
# Output in dist/ folder
```

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

---

## 🐛 Troubleshooting

### Problem: "node is not recognized"

**Solution:** Use the batch/PowerShell scripts - they automatically add Node.js to PATH:
```bash
run_frontend.bat
```

### Problem: Port 5173 already in use

**Solution 1:** Kill the process
```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Solution 2:** Change port in `vite.config.ts`
```typescript
server: { port: 3000 }
```

### Problem: CORS errors when calling backend

**Solution:** Ensure backend has CORS enabled:
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problem: Dependencies fail to install

**Solution:** Clear npm cache and retry
```bash
cd app-frontend
npm cache clean --force
rm -rf node_modules
npm install
```

---

## 📚 Next Steps

1. **Customize Components** - Edit files in `src/components/`
2. **Add Pages** - Create new pages in `src/pages/`
3. **Connect to Backend** - Use axios to call your API
4. **Style with Tailwind** - Add utility classes
5. **Add Map Layers** - Extend MapView component

---

## 📖 Documentation Links

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [MapLibre GL](https://maplibre.org/)

---

## ✅ Verification Checklist

- [ ] Node.js installed (v18+)
- [ ] npm working (`npm --version`)
- [ ] Frontend dependencies installed (`node_modules/` exists)
- [ ] Backend running on port 8000
- [ ] Frontend accessible at http://localhost:5173
- [ ] No CORS errors in browser console

---

**Need Help?** Check the full README: `app-frontend/README.md`

**Last Updated:** November 9, 2025
