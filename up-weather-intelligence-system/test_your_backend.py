"""
=============================================================
Backend Connection Test Script
Tailored for YOUR specific file structure:
  - models/classifier_xgb.pkl
  - models/regressor_lgbm.pkl
  - models/scaler.pkl
  - models/scaler_reg.pkl
  - data/weather_db.sqlite
=============================================================
Run this BEFORE starting the frontend to verify everything works.

Instructions:
1. Start your FastAPI server:
   uvicorn app:app --reload --port 8000

2. Run this test in your virtual environment:
   python test_your_backend.py

3. Check the output for any errors
=============================================================
"""

import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"

def test_connection():
    print("\n" + "=" * 70)
    print(" UP Rainfall Prediction — Backend Connection Test")
    print("   Tailored for YOUR project structure")
    print("=" * 70 + "\n")

    all_passed = True

    # ============================================================
    # Test 1: Server Reachability
    # ============================================================
    print("Test 1: Server Reachability")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Server responding (Status: {response.status_code})")
            print(f"     Models loaded: {data.get('models_loaded', 'unknown')}")
            print(f"     Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print(f"  ❌ Server returned status {response.status_code}")
            all_passed = False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Server not running at {BASE_URL}")
        print("  → Start: uvicorn app:app --reload --port 8000")
        all_passed = False
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        all_passed = False
    print()

    # ============================================================
    # Test 2: GET /api/v1/districts
    # ============================================================
    print("Test 2: GET /api/v1/districts (SQLite Query)")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/districts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  ✅ Districts endpoint working")
                print(f"     Returned {len(data)} districts")
                if len(data) > 0:
                    print(f"     Sample: {json.dumps(data[0], indent=2)}")
            else:
                print(f"  ⚠️  Unexpected response format")
                print(f"     Type: {type(data).__name__}")
        else:
            print(f"   Endpoint returned status {response.status_code}")
            print(f"     Response: {response.text[:200]}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ Request failed: {e}")
        all_passed = False
    print()

    # ============================================================
    # Test 3: POST /api/v1/predict (Single District)
    # ============================================================
    print("Test 3: POST /api/v1/predict (Your Models)")
    print("-" * 50)
    test_payload = {
        "district_id": "UP-50",
        "temperature_c": 32.5,
        "humidity_pct": 78.0,
        "wind_vector_x": -1.6,
        "wind_vector_y": 2.8,
        "lag_1_rain": 15.0,
        "lag_3_rain": 35.0,
        "lag_7_rain": 78.0
    }
    print(f"  Sending payload:")
    print(f"  {json.dumps(test_payload, indent=4)}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Prediction successful!")
            print(f"  Response:")
            print(f"  {json.dumps(data, indent=4)}")
            
            # Validate response
            required_fields = ["district_id", "classification_threat_pct", "will_rain", "predicted_rain_mm"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"  ⚠️  Missing fields: {missing}")
                all_passed = False
            else:
                print(f"  ✅ All required fields present")
                
                # Check prediction makes sense
                if 0 <= data["classification_threat_pct"] <= 100:
                    print(f"  ✅ Threat probability is valid (0-100%)")
                else:
                    print(f"  ⚠️  Threat probability out of range: {data['classification_threat_pct']}")
                    
                if data["predicted_rain_mm"] >= 0:
                    print(f"  ✅ Rainfall prediction is valid (≥ 0 mm)")
                else:
                    print(f"  ⚠️  Negative rainfall: {data['predicted_rain_mm']}")
                    
        else:
            print(f"  ❌ Prediction endpoint returned status {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            all_passed = False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to server")
        all_passed = False
    except Exception as e:
        print(f"  ❌ Request failed: {e}")
        all_passed = False
    print()

    # ============================================================
    # Test 4: CORS Headers (Critical for Frontend)
    # ============================================================
    print("Test 4: CORS Headers (Frontend Compatibility)")
    print("-" * 50)
    try:
        response = requests.options(
            f"{BASE_URL}/api/v1/predict",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        cors_headers = response.headers
        
        if "access-control-allow-origin" in cors_headers:
            origin = cors_headers.get("access-control-allow-origin")
            print(f"  ✅ CORS enabled")
            print(f"     Access-Control-Allow-Origin: {origin}")
            
            if origin == "*" or "localhost:5173" in origin:
                print(f"  ✅ Frontend (localhost:5173) is allowed")
            else:
                print(f"  ️  Frontend origin may not be allowed")
        else:
            print(f"  ❌ CORS headers missing!")
            print(f"  → Check app.py has CORSMiddleware configured")
            all_passed = False
    except Exception as e:
        print(f"  ⚠️  CORS test error: {e}")
    print()

    # ============================================================
    # Test 5: Multiple Districts (Bulk)
    # ============================================================
    print("Test 5: Bulk Prediction (Multiple Districts)")
    print("-" * 50)
    bulk_payload = [
        {
            "district_id": "UP-50",
            "temperature_c": 32.5,
            "humidity_pct": 78.0,
            "wind_vector_x": -1.6,
            "wind_vector_y": 2.8,
            "lag_1_rain": 15.0,
            "lag_3_rain": 35.0,
            "lag_7_rain": 78.0
        },
        {
            "district_id": "UP-01",
            "temperature_c": 34.2,
            "humidity_pct": 62.0,
            "wind_vector_x": 2.1,
            "wind_vector_y": -1.4,
            "lag_1_rain": 0.0,
            "lag_3_rain": 12.5,
            "lag_7_rain": 45.0
        },
        {
            "district_id": "UP-12",
            "temperature_c": 30.5,
            "humidity_pct": 84.0,
            "wind_vector_x": -2.5,
            "wind_vector_y": 4.8,
            "lag_1_rain": 54.0,
            "lag_3_rain": 110.0,
            "lag_7_rain": 210.0
        }
    ]
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/predict/bulk",
            json=bulk_payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Bulk prediction working")
            print(f"     Returned {len(data)} predictions:")
            for pred in data:
                print(f"     - {pred['district_id']}: threat={pred['threat_pct']}%, rain={pred['rain_mm']}mm")
        else:
            print(f"  ⚠️  Bulk endpoint returned status {response.status_code}")
            print(f"     (This endpoint is optional — single predictions still work)")
    except Exception as e:
        print(f"  ️  Bulk test error: {e}")
        print(f"     (This endpoint is optional)")
    print()

    # ============================================================
    # Summary
    # ============================================================
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED — Your backend is ready!")
        print()
        print("Next Steps:")
        print("1. Open a NEW terminal (keep this one running)")
        print("2. Navigate to the frontend dashboard folder")
        print("3. Run: npm install")
        print("4. Run: npm run dev")
        print("5. Open browser to: http://localhost:5173")
        print("6. You should see 'Backend ONLINE' green badge")
    else:
        print("❌ SOME TESTS FAILED — Fix issues before proceeding")
        print()
        print("Common Fixes:")
        print("1. Make sure uvicorn is running: uvicorn app:app --reload --port 8000")
        print("2. Check app.py has CORSMiddleware (see INTEGRATION_GUIDE.md)")
        print("3. Verify models exist in models/ directory")
        print("4. Check SQLite table names match (see Step 2 in guide)")
        print("5. Verify feature order matches training data (see Step 3)")
    print("=" * 70 + "\n")

    return all_passed

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
