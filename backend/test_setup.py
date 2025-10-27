"""
Quick test script to validate backend setup

Run this to check if everything is working:
    python test_setup.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🧪 Testing Backend Setup...\n")

# Test 1: Import config
print("1️⃣ Testing configuration...")
try:
    from backend.config import settings
    print(f"   ✅ Config loaded")
    print(f"   - Supabase URL: {settings.supabase_url}")
    print(f"   - API Port: {settings.api_port}")
except Exception as e:
    print(f"   ❌ Config error: {e}")
    sys.exit(1)

# Test 2: Import models
print("\n2️⃣ Testing database models...")
try:
    from backend.models import Session, Point, User, HeartRateData, Insight
    print("   ✅ All models imported successfully")
except Exception as e:
    print(f"   ❌ Model import error: {e}")
    sys.exit(1)

# Test 3: Test existing code imports
print("\n3️⃣ Testing existing code integration...")
try:
    from data.ingestion.data_ingestion import FitnessDataImporter
    from core.metrics_framework import MetricsFramework, RallyDetector
    print("   ✅ Existing code can be imported")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 4: Test services
print("\n4️⃣ Testing service layer...")
try:
    # Just import, don't instantiate (needs DB connection)
    from backend.services.data_ingestion_service import DataIngestionService
    from backend.services.insight_generator import InsightGenerator
    print("   ✅ Services can be imported")
except Exception as e:
    print(f"   ❌ Service error: {e}")
    sys.exit(1)

# Test 5: Database connection (optional, requires Supabase)
print("\n5️⃣ Testing database connection...")
try:
    from backend.models.database import engine
    # Try to connect
    with engine.connect() as conn:
        print("   ✅ Database connection successful!")
        print(f"   - Connected to: {settings.database_url.split('@')[1]}")  # Hide password
except Exception as e:
    print(f"   ⚠️  Database connection failed (this is OK if you haven't set up Supabase yet)")
    print(f"   - Error: {e}")
    print(f"   - Make sure SUPABASE_SERVICE_KEY and DATABASE_URL are set in .env")

print("\n" + "="*60)
print("✨ Setup test complete!")
print("="*60)
print("\nNext steps:")
print("1. If database connection failed, update .env with Supabase credentials")
print("2. Run: python app.py")
print("3. Visit: http://localhost:8000/docs")
print("\nReady to build! 🚀")
