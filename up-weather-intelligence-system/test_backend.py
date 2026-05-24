"""
=============================================================
Backend Connection Test Script
Run this BEFORE connecting the frontend to verify your
FastAPI server is properly configured.
=============================================================
Instructions:
1. Start your FastAPI server: uvicorn app:app --reload --port 8000
2. Run this script: python test_backend.py
3. Check output for any errors
=============================================================
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_connection():
    print("=" * 60)
    print("🧪 FastAPI Backend Connection Test")
    print("=" * 60)
    print()

    # Test 1: Check if server is running
    print("Test 1: Server Reachability...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"  ✅ Server responding (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Server not running at {BASE_URL}")
        print("  → Start your server: uvicorn app:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"  ⚠️  Server error: {e}")

    # Test 2: Check GET /api/v1/districts endpoint
    print("\nTest 2: GET /api/v1/districts endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/districts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  ✅ Endpoint working (returned {len(data)} districts)")
            else:
                print(f"  ⚠️  Endpoint returned non-list data")
        else:
            print(f"  ❌ Endpoint returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Request failed: {e}")

    # Test 3: Check POST /api/v1/predict endpoint
    print("\nTest 3: POST /api/v1/predict endpoint...")
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
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Prediction endpoint working!")
            print(f"  Response:")
            print(json.dumps(data, indent=4))
            
            # Validate response structure
            required_fields = ["district_id", "classification_threat_pct", "will_rain", "predicted_rain_mm"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"  ⚠️  Missing fields in response: {missing}")
            else:
                print(f"  ✅ All required fields present")
        else:
            print(f"  ❌ Endpoint returned status {response.status_code}")
            print(f"  Response: {response.text[:300]}")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to server")
    except Exception as e:
        print(f"  ❌ Request failed: {e}")

    # Test 4: Check CORS headers
    print("\nTest 4: CORS Headers (Critical for Frontend)...")
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
            print(f"  ✅ CORS enabled")
            print(f"  Access-Control-Allow-Origin: {cors_headers.get('access-control-allow-origin')}")
        else:
            print(f"  ❌ CORS headers missing!")
            print(f"  → Add CORSMiddleware to your app.py (see SETUP_INSTRUCTIONS.md)")
    except Exception as e:
        print(f"  ⚠️  CORS test failed: {e}")

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. If all tests passed ✅ → Run 'npm run dev' to start frontend")
    print("2. If any tests failed ❌ → Fix issues in app.py before proceeding")
    print("3. Open browser to http://localhost:5173")
    print()

    return True

if __name__ == "__main__":
    try:
        test_connection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
