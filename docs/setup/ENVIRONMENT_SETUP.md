# How to Activate Both Python and Node.js Environment

## Problem
When you activate the Python virtual environment (`.venv`), Node.js/npm are not available because they're not in the venv's PATH.

## Solution: Use the Combined Activation Script

### Method 1: PowerShell Script (Recommended)
```powershell
# From project root
.\activate_all.ps1
```

This script will:
1. ✅ Activate Python virtual environment
2. ✅ Add Node.js to PATH
3. ✅ Show installed versions

### Method 2: Manual (Two Commands)
```powershell
# Step 1: Activate Python venv
.\.venv\Scripts\Activate.ps1

# Step 2: Add Node.js to PATH
$env:Path = "C:\Program Files\nodejs;" + $env:Path
```

### Method 3: One-Line Command
```powershell
.\.venv\Scripts\Activate.ps1; $env:Path = "C:\Program Files\nodejs;" + $env:Path
```

---

## Verification

After activation, verify both are available:

```powershell
# Check Python
python --version
# Should show: Python 3.11.x

# Check Node.js
node --version
# Should show: v24.11.0

# Check npm
npm --version
# Should show: 11.6.1
```

---

## Common Workflows

### Start Backend (Python)
```powershell
# Activate environment
.\activate_all.ps1

# Run backend
cd backend
uvicorn app.main:app --reload
```

### Start Frontend (Node.js)
```powershell
# Activate environment
.\activate_all.ps1

# Run frontend
cd app-frontend
npm run dev
```

### Run Full Stack
```powershell
# Terminal 1: Backend
.\activate_all.ps1
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
.\activate_all.ps1
cd app-frontend
npm run dev
```

---

## Why This Happens

The Python virtual environment (`.venv`) only contains:
- Python interpreter
- Python packages (pip, numpy, pandas, etc.)
- **NOT Node.js or npm** (they're system-wide installations)

When you activate `.venv`, it modifies PATH to prioritize the venv's Python, but it doesn't include system Node.js. You need to manually add Node.js to PATH after activating the venv.

---

## Permanent Solution (Optional)

If you always need both, you can modify the venv activation script:

```powershell
# Edit .venv\Scripts\Activate.ps1
# Add this line at the end:
$env:Path = "C:\Program Files\nodejs;" + $env:Path
```

But it's cleaner to use the `activate_all.ps1` script instead.

---

## Quick Reference

| Task | Command |
|------|---------|
| Activate both | `.\activate_all.ps1` |
| Run backend | `cd backend; uvicorn app.main:app --reload` |
| Run frontend | `cd app-frontend; npm run dev` |
| Install Python package | `pip install <package>` |
| Install Node package | `cd app-frontend; npm install <package>` |
| Deactivate | `deactivate` |

---

**Created:** November 9, 2025
