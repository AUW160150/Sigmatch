# Sigmatch Backend - Quick Reference Guide

## 🚀 Starting the Server

```bash
cd sigmatch_backend
source sigma/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will be available at:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/docs`

---

## 📁 Project Structure

```
sigmatch_backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py             # Pydantic models for requests/responses
│   ├── routers/
│   │   ├── config.py              # GET/POST /api/config
│   │   ├── trials.py              # GET/POST /api/trials
│   │   ├── cohorts.py             # GET/POST /api/cohorts
│   │   ├── prompts.py             # GET/PUT /api/prompts
│   │   ├── pipeline.py            # POST /api/pipeline/run
│   │   ├── results.py             # GET /api/results
│   │   └── chat.py                # GET/POST /api/chat
│   ├── services/
│   │   ├── file_ops.py            # File operations with BASE_DIR
│   │   ├── config_manager.py      # Config management & path generation
│   │   └── synthetic_data.py      # Dummy data generation
│   └── data/
│       └── Sigmatch/              # All data files (BASE_DIR)
│           ├── config_files/
│           │   ├── overall_config_settings/
│           │   │   └── active_data_config.json
│           │   ├── trial_files/
│           │   ├── pipeline_json_files/
│           │   └── prompt_settings/
│           ├── results_dir/
│           │   ├── matching/
│           │   ├── llm_summarization/
│           │   └── evaluation/
│           ├── documents/
│           │   ├── pdfs/
│           │   └── ocr/
│           └── snapshots/
```

---

## 🔧 Common API Operations

### 1. Get Current Configuration

```bash
curl http://localhost:8000/api/config | jq
```

### 2. Update Configuration (Change Cohort)

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "cohortName": "my_cohort",
    "patients_file_path": "config_files/pipeline_json_files/my_cohort.json"
  }' | jq
```

**Result:** All paths auto-generate based on cohortName:
- `matching_result_dir` → `results_dir/matching/my_cohort`
- `extracted_features_path` → `results_dir/llm_summarization/my_cohort/patient_feature_summaries_my_cohort.csv`
- etc.

### 3. List All Trials

```bash
curl http://localhost:8000/api/trials | jq '.trials'
```

### 4. List All Cohorts

```bash
curl http://localhost:8000/api/cohorts | jq '.cohorts'
```

### 5. Run Pipeline (Get Command)

```bash
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "config_files/overall_config_settings/active_data_config.json",
    "run_ocr": false,
    "do_llm_summarization": true,
    "do_patient_matching": true,
    "do_evaluation": false
  }' | jq -r '.command'
```

**Command will also print to server console:**
```
================================================================================
PIPELINE COMMAND TO RUN:
python orchestrate_pipeline.py --data_config_json config_files/overall_config_settings/active_data_config.json --run_ocr False --do_llm_summarization True --do_patient_matching True --do_evaluation False
================================================================================
```

### 6. Get Results Summary

```bash
curl http://localhost:8000/api/results/summary | jq
```

### 7. Download Results CSV

```bash
curl http://localhost:8000/api/results/download -o matching_results.csv
```

### 8. Create Configuration Snapshot

```bash
curl -X POST http://localhost:8000/api/config/snapshot | jq
```

### 9. Assemble Cohort (Filter Patients)

```bash
curl -X POST http://localhost:8000/api/cohorts/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": ["colorectal cancer", "stage 4", "metastatic"],
    "max_patients": 100,
    "cohort_source": "dummy_cohort1.json"
  }' | jq
```

---

## 📝 Adding New Data

### Add a New Trial

**Option 1: Upload JSON File**
```bash
curl -X POST http://localhost:8000/api/trials/upload \
  -F "file=@my_trial.json" | jq
```

**Option 2: Create from Data**
```bash
curl -X POST http://localhost:8000/api/trials \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Clinical Trial",
    "full_text": "Trial description here..."
  }' | jq
```

**Option 3: Manually Add File**
1. Create `my_trial.json`:
```json
{
  "_id": "my_trial_001",
  "title": "My Trial Title",
  "full_text": "Full trial description and eligibility criteria..."
}
```
2. Drop it into: `app/data/Sigmatch/config_files/trial_files/`
3. Refresh frontend → trial appears immediately

### Add a New Cohort

**Option 1: Generate Synthetic Data**
```bash
curl -X POST http://localhost:8000/api/cohorts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_cohort",
    "patient_count": 50
  }' | jq
```

**Option 2: Manually Add File**
1. Create `my_cohort.json`:
```json
[
  {
    "patient_id": "P001",
    "full_text": "Patient clinical history and information..."
  },
  {
    "patient_id": "P002",
    "full_text": "Patient clinical history and information..."
  }
]
```
2. Drop it into: `app/data/Sigmatch/config_files/pipeline_json_files/`
3. Refresh frontend → cohort appears immediately

### Add Results for a Cohort

1. Create `matching_results.csv` with these columns:
   - `patient_id`
   - `final_decision` (MATCH or NO_MATCH)
   - `overall_score` (1-5)
   - `primary_reasons`
   - `concerns`
   - `decision_reasoning`

2. Place it in: `app/data/Sigmatch/results_dir/matching/{cohort_name}/matching_results.csv`

3. Refresh Results page → data appears immediately

---

## 🔍 Debugging Tips

### Check Server Logs

Look for these in terminal:
- Startup: `Sigmatch backend initialized successfully!`
- Pipeline commands: Lines with `================`
- Validation errors: Lines starting with `❌ VALIDATION ERROR`
- Debug output: Lines starting with `DEBUG:`

### Common Issues

**Issue:** 422 Validation Error on POST /api/config  
**Solution:** Check request body matches DataConfig schema in `app/models/schemas.py`

**Issue:** 404 Not Found for trial/cohort  
**Solution:** Verify file exists in correct directory with `.json` extension

**Issue:** No results showing  
**Solution:** 
1. Check `active_data_config.json` for correct `matching_result_dir`
2. Verify `matching_results.csv` exists in that directory
3. Check CSV has correct column names

**Issue:** CORS errors in frontend  
**Solution:** Use Cloudflare Tunnel or ngrok to expose local backend with HTTPS

---

## 🧪 Testing Endpoints

**Interactive API Docs:**  
Visit `http://localhost:8000/docs` for Swagger UI with:
- All endpoints documented
- Try-it-out functionality
- Request/response schemas
- Example values

**Health Check:**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

---

## 📊 Understanding the Data Flow

1. **User Selects Cohort** → Frontend calls `POST /api/config`
2. **Backend Auto-Generates Paths** → Based on cohortName
3. **Backend Creates Directories** → If they don't exist
4. **User Clicks "Run Pipeline"** → Frontend calls `POST /api/pipeline/run`
5. **Backend Returns Command** → User copies and runs command
6. **Pipeline Writes Results** → To `results_dir/matching/{cohort_name}/matching_results.csv`
7. **User Views Results** → Frontend calls `GET /api/results/summary`
8. **Backend Reads Results** → From path in active config

**Key Point:** Everything is based on cohortName, making it fully dynamic!

---

## 🔐 Security Notes (Development)

- CORS is set to `allow_origins=["*"]` for development
- No authentication required
- All file operations restricted to `BASE_DIR`
- Malformed files are skipped gracefully

**For Production:**
- Update CORS to specific origins
- Add authentication/authorization
- Add rate limiting
- Add file size limits

---

## 📦 Dependencies

```txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
aiofiles==23.2.1
python-dotenv==1.0.0
```

**To install:**
```bash
pip install -r requirements.txt
```

---

## 🆘 Getting Help

1. **API Documentation:** http://localhost:8000/docs
2. **Audit Report:** See `BACKEND_AUDIT_REPORT.md` for comprehensive system overview
3. **Assemble Cohort Feature:** See `ASSEMBLE_COHORT_FEATURE.md` for details on filtering patients
4. **Main README:** See `README.md` for project overview

---

## 🎯 Next Steps After Setup

1. ✅ Start the server
2. ✅ Open http://localhost:8000/docs to explore API
3. ✅ Test endpoints with curl or Swagger UI
4. ✅ Add your own trials and cohorts
5. ✅ Configure cohort in frontend
6. ✅ Run pipeline and view results

**Everything is ready to go!** 🚀

