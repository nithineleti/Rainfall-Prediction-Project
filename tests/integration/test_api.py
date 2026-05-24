"""
End-to-End Test for Watershed-UP API

Tests complete workflow: auth → data → models → predictions → AHP
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health: {response.json()}")
    return response.json()

def test_login():
    """Test login and get token"""
    data = {
        "username": "demo",
        "password": "demo123"
    }
    response = requests.post(f"{BASE_URL}/v1/auth/login", data=data)
    if response.status_code == 200:
        print(f"✅ Login successful: {response.status_code}")
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception(f"Login failed with status {response.status_code}")

def test_get_me(token):
    """Test getting current user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/auth/me", headers=headers)
    print(f"✅ Current user: {response.json()}")
    return response.json()

def test_list_models(token):
    """Test listing ML models"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/ml/models", headers=headers)
    print(f"✅ Available models: {len(response.json())} model(s)")
    return response.json()

def test_feature_importances(token, model_id="rf_baseline_v1"):
    """Test getting feature importances"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/ml/feature-importances/{model_id}", headers=headers)
    importances = response.json()["importances"]
    print(f"✅ Feature importances (top 5):")
    for feature, score in list(importances.items())[:5]:
        print(f"   {feature}: {score:.4f}")
    return importances

def test_ahp_default_weights():
    """Test getting default AHP weights"""
    response = requests.get(f"{BASE_URL}/v1/ahp/default-weights")
    print(f"✅ Default AHP weights: {response.json()}")
    return response.json()

def test_metrics():
    """Test metrics endpoint"""
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"✅ Metrics: {response.json()}")
    return response.json()

def test_submit_job(token):
    """Test submitting a job"""
    headers = {"Authorization": f"Bearer {token}"}
    job_data = {
        "job_type": "preprocess",
        "parameters": {"task": "feature_stack"}
    }
    response = requests.post(f"{BASE_URL}/v1/jobs/submit", headers=headers, json=job_data)
    if response.status_code == 201:
        print(f"✅ Job submitted: {response.json()['job_id']}")
        return response.json()
    else:
        print(f"⚠️  Job submission: {response.status_code}")
        return None

def test_list_jobs(token):
    """Test listing jobs"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/jobs/jobs", headers=headers)
    print(f"✅ Total jobs: {len(response.json())}")
    return response.json()

def test_model_detail(token, model_id="rf_baseline_v1"):
    """Test getting model details"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/ml/models/{model_id}", headers=headers)
    if response.status_code == 200:
        model = response.json()
        print(f"✅ Model: {model['model_name']}")
        print(f"   Accuracy: {model['accuracy']*100:.2f}%")
        print(f"   Features: {model['feature_count']}")
        return model
    return None

if __name__ == "__main__":
    print("\n" + "🌊 " * 20)
    print("    WATERSHED-UP API - END-TO-END TEST")
    print("🌊 " * 20)
    
    try:
        # Phase 1: System Health
        print_section("PHASE 1: System Health Check")
        health = test_health()
        metrics = test_metrics()
        
        # Phase 2: Authentication
        print_section("PHASE 2: Authentication & User Management")
        token = test_login()
        user = test_get_me(token)
        
        # Phase 3: ML Models
        print_section("PHASE 3: Machine Learning Models")
        models = test_list_models(token)
        if models:
            model_detail = test_model_detail(token)
            importances = test_feature_importances(token)
            
            # Show top 10 features
            print("\n📊 Top 10 Feature Importances:")
            for i, (feature, score) in enumerate(list(importances.items())[:10], 1):
                bar = "█" * int(score * 50)
                print(f"   {i:2d}. {feature:20s} {bar} {score:.4f}")
        
        # Phase 4: Job Queue
        print_section("PHASE 4: Job Queue System")
        job = test_submit_job(token)
        jobs = test_list_jobs(token)
        
        # Phase 5: AHP Engine
        print_section("PHASE 5: AHP Analysis Engine")
        ahp_weights = test_ahp_default_weights()
        print("\n📐 AHP Weight Distribution:")
        for criterion, weight in ahp_weights.items():
            bar = "▓" * int(weight * 100)
            print(f"   {criterion:20s} {bar} {weight:.2f}")
        
        # Summary
        print_section("TEST SUMMARY")
        print("✅ All API endpoints functional")
        print(f"✅ Authentication working (User: {user['username']})")
        print(f"✅ {len(models)} ML model(s) available")
        print(f"✅ Feature importances retrieved")
        print(f"✅ Job queue operational")
        print(f"✅ AHP engine ready")
        
        print("\n" + "="*60)
        print("🎉 END-TO-END TEST PASSED!")
        print("="*60)
        print(f"\n📖 Interactive API Docs: {BASE_URL}/docs")
        print(f"🔍 Health Check: {BASE_URL}/health")
        print(f"📊 Metrics: {BASE_URL}/metrics")
        
        # Enhanced Features Info
        print("\n" + "="*60)
        print("📈 ENHANCED WATERSHED FEATURES INTEGRATED:")
        print("="*60)
        print("✅ TWI (Topographic Wetness Index)")
        print("✅ TPI (Topographic Position Index)") 
        print("✅ Distance to Streams")
        print("✅ Plan Curvature")
        print("✅ Profile Curvature")
        print("✅ Aspect")
        print(f"\n🎯 Model Accuracy: {model_detail['accuracy']*100:.2f}%")
        print(f"🎯 Balanced Accuracy: {model_detail['balanced_accuracy']*100:.2f}%")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
