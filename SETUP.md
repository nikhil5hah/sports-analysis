# Sports Analytics - Quick Setup Guide

Complete platform for racket sports analytics (Squash, Tennis, Badminton, Table Tennis, Padel)

---

## 🚀 Backend Setup (5 minutes)

### 1. Supabase Credentials

✅ **Already done!** Your credentials are in `backend/.env`

**If you need to update**:
1. Go to Supabase Dashboard → Project Settings → API
2. Copy the **service_role** key (not anon key)
3. Update `SUPABASE_SERVICE_KEY` in `backend/.env`

Also get your database password from Supabase:
- Project Settings → Database → Connection String
- Update `DATABASE_URL` in `backend/.env`

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Test the Server

```bash
python app.py
```

**Expected output:**
```
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test it:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

---

## 🏗️ What's Built

### Backend (FastAPI)
- ✅ Database models (Session, Point, HR data, etc.)
- ✅ Data ingestion service (reuses your FIT parser)
- ✅ Insight generator (reuses your metrics framework)
- ⏳ API routes (next step)

### Multi-Sport Support
- ✅ Database ready for any racket sport
- ✅ Session model has `sport` field
- ✅ Scoring system field (american/english/traditional/etc.)

### Features Ready
- ✅ Manual score tracking (button presses)
- ✅ HR monitoring integration
- ✅ Sensor data collection (for future ML)
- ✅ HR + Score correlation insights
- ✅ Let tracking (for accurate rally counts)

---

## 📊 Database Tables

Your Supabase database will have these tables (auto-created):

```
users                   # User accounts
├── sessions            # Match/training sessions
│   ├── points          # Individual points scored
│   ├── heart_rate_data # Time-series HR (1Hz)
│   ├── sensor_data_batches # Accel/gyro (10Hz, compressed)
│   └── insights        # Generated analytics
```

---

## 🔍 Verify Supabase Connection

### Option 1: Supabase Dashboard
1. Go to your project: https://nvclilppofulqvotedvu.supabase.co
2. Click "Table Editor" (left sidebar)
3. After running the backend once, you should see tables created

### Option 2: Check in Code
```bash
# From backend/ directory
python
>>> from models.database import engine
>>> from models import Base
>>> Base.metadata.create_all(engine)
>>> # If no errors, database is connected!
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "Could not connect to database"
Check your `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.nvclilppofulqvotedvu.supabase.co:5432/postgres
```

Get YOUR_PASSWORD from:
- Supabase → Settings → Database → Connection String

### "SUPABASE_SERVICE_KEY not found"
1. Supabase → Settings → API → Service Role Key (secret)
2. Copy and paste into `backend/.env`

---

## 📝 Next Steps

### ✅ Now: Test Backend
```bash
cd backend
python app.py
# Visit: http://localhost:8000/docs (Swagger UI)
```

### ⏭️ Next: Build API Routes
I'll create:
- `POST /api/sessions` - Start new session
- `POST /api/sessions/{id}/points` - Record points
- `GET /api/sessions/{id}/insights` - Get analytics

### 🎯 Then: Test with Real Data
- Upload a FIT file
- Get insights back
- Validate the whole flow

---

## 🔐 Security Notes

**⚠️ Never commit `.env` file!**

It's already in `.gitignore`, but double-check:
```bash
git status
# Should NOT show backend/.env
```

**Your credentials are safe** ✅

---

## 🎾 Multi-Sport Ready

Currently configured for **Squash**, but ready to add:
- Tennis
- Badminton
- Table Tennis
- Padel

See `docs/multi_sport_support.md` for architecture details.

---

## 📞 Help

If you get stuck:
1. Check the error message carefully
2. Verify `.env` file has all values filled
3. Make sure Supabase project is running (green status in dashboard)
4. Check database connection string is correct

---

**You're all set!** 🚀

Backend is ready to receive data from the Wear OS app (which we'll build next).
