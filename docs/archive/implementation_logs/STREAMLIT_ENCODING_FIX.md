# Streamlit Connection Error - SOLVED

**Date:** October 28, 2025  
**Issue:** Streamlit crashes immediately after starting with no visible error  
**Status:** ✅ RESOLVED

---

## Problem

When running `streamlit run app/main.py`, the server would:
1. Start successfully and show "You can now view your Streamlit app at http://localhost:8501"
2. Immediately crash with exit code 1
3. Show no error message to help debug

**Error in logs:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 1870
```

---

## Root Cause

**Windows Default Encoding Issue**

Windows PowerShell and Command Prompt use CP1252 (Windows-1252) encoding by default, which **cannot handle Unicode emoji characters** used in the Streamlit app:

```python
# These emojis cause UnicodeDecodeError on Windows:
st.markdown('💧 Groundwater Potential Zone Explorer')
page = st.sidebar.radio("Select:", [
    "🏠 Home",
    "🗺️ Interactive Map",
    "📊 Data Layers",
    # ... etc
])
```

The emoji characters (💧, 🏠, 🗺️, 📊, 🤖, 📈, 🔍, 📥) are multi-byte UTF-8 characters that Windows CP1252 cannot decode.

---

## Solution

Set Python I/O encoding to **UTF-8** before launching Streamlit.

### PowerShell
```powershell
$env:PYTHONIOENCODING = "utf-8"
streamlit run app\main.py
```

### Command Prompt / Batch
```cmd
set PYTHONIOENCODING=utf-8
streamlit run app\main.py
```

### Permanent Fix
Use the provided launch scripts that automatically set the encoding:

**PowerShell:**
```powershell
.\launch_streamlit.ps1
```

**Batch:**
```cmd
launch_streamlit.bat
```

---

## Files Created

1. **launch_streamlit.ps1** - PowerShell launcher with UTF-8 encoding
2. **launch_streamlit.bat** - Batch launcher with UTF-8 encoding
3. **STREAMLIT_LAUNCH.md** - Complete launch guide and troubleshooting
4. **Updated run_pipeline_skip_stage3.ps1** - Pipeline script now includes UTF-8 fix

---

## Verification

**Before fix:**
```
streamlit run app/main.py
# Output: Server starts then crashes immediately (exit code 1)
```

**After fix:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
streamlit run app/main.py
# Output: ✅ Server runs successfully at http://localhost:8501
```

---

## Technical Details

### Why This Happens on Windows

1. **Windows Console Codepage**: Windows terminals use CP1252 by default
2. **Python Default Encoding**: Python 3.x uses UTF-8 for source code but respects system encoding for I/O
3. **Streamlit UI**: Uses Unicode emoji characters throughout the interface
4. **Decoding Attempt**: When Streamlit tries to read/display the app, Windows attempts to decode UTF-8 emojis as CP1252, causing `UnicodeDecodeError`

### The Byte That Failed

```
Position: 1870
Byte: 0x8f
Character: Part of multi-byte UTF-8 emoji sequence 💧
Error: CP1252 has no mapping for 0x8f
```

In UTF-8, emoji characters use multiple bytes (usually 3-4 bytes). The emoji 💧 (water droplet) is encoded as:
```
UTF-8: 0xF0 0x9F 0x92 0xA7
```

Windows CP1252 encounters `0x8f` (which is undefined in CP1252) and crashes.

### Why It Works After Setting PYTHONIOENCODING

Setting `PYTHONIOENCODING=utf-8` tells Python to:
- Use UTF-8 for all standard I/O streams (stdin, stdout, stderr)
- Decode all text files as UTF-8 (including the Streamlit app code)
- Properly handle multi-byte Unicode characters

---

## Alternative Solutions (Not Recommended)

### 1. Remove Emojis
Replace all emojis with plain text:
```python
# Before
st.markdown('💧 Groundwater Potential Zone Explorer')

# After  
st.markdown('Groundwater Potential Zone Explorer')
```

**Downside:** Less visually appealing interface.

### 2. Change System Locale
Change Windows system locale to UTF-8:
```
Settings → Time & Language → Language → Administrative Language Settings
→ Change system locale → Beta: Use Unicode UTF-8
```

**Downside:** Requires system restart; may break other applications.

### 3. Use WSL
Run Streamlit in Windows Subsystem for Linux where UTF-8 is default:
```bash
wsl
conda activate watershed-up
streamlit run app/main.py
```

**Downside:** Requires WSL setup; extra complexity.

---

## Best Practice for Windows Streamlit Apps

**Always include encoding setup in launch scripts:**

```powershell
# PowerShell
$env:PYTHONIOENCODING = "utf-8"

# Batch
set PYTHONIOENCODING=utf-8
```

Or add to the beginning of your Python script:
```python
import sys
import io

# Force UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

## References

- [Python Encoding on Windows](https://docs.python.org/3/library/sys.html#sys.stdin)
- [Streamlit Unicode Issues](https://discuss.streamlit.io/search?q=unicode)
- [Windows Code Pages](https://docs.microsoft.com/en-us/windows/win32/intl/code-pages)

---

## Summary

✅ **Fixed by setting `PYTHONIOENCODING=utf-8`**  
✅ **Launch scripts created for easy startup**  
✅ **Streamlit now runs successfully on Windows**  
✅ **All emoji characters display correctly**

The platform is fully operational!
