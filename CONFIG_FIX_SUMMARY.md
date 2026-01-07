# Config Handling Fix - Summary

## Problem Solved

Fixed issues where:
- Config had empty `cohortName: ""`
- Paths were incomplete: `"results_dir/matching/"` (missing cohort folder)
- Results page couldn't find `matching_results.csv`

## Changes Made

### 1. Enhanced `auto_generate_paths()` in `config_manager.py`

**Location:** `app/services/config_manager.py` (Lines 61-98)

**New Logic:**
1. Checks if `cohortName` is empty or missing
2. If empty, extracts cohort name from `patients_file_path`
   - Example: `"config_files/pipeline_json_files/dummy_cohort2.json"` → `"dummy_cohort2"`
3. If still empty, falls back to `"dummy_cohort1"`
4. Always sets `cohortName` in config
5. Auto-generates ALL paths based on extracted/provided `cohortName`

**Code:**
```python
def auto_generate_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    cohort_name = config.get("cohortName", "").strip()
    
    # If cohortName is empty, try to extract from patients_file_path
    if not cohort_name:
        patients_path = config.get("patients_file_path", "")
        if patients_path:
            filename = patients_path.split("/")[-1]  # "dummy_cohort1.json"
            cohort_name = filename.replace(".json", "")  # "dummy_cohort1"
            print(f"INFO: Extracted cohort name '{cohort_name}' from patients_file_path")
    
    # Default fallback
    if not cohort_name:
        cohort_name = "dummy_cohort1"
        print(f"WARN: No cohortName found, using default: {cohort_name}")
    
    # Set the cohortName in config
    config["cohortName"] = cohort_name
    
    # ALWAYS generate paths based on cohortName
    config["matching_result_dir"] = f"results_dir/matching/{cohort_name}"
    # ... all other paths
```

### 2. Added Startup Validation in `main.py`

**Location:** `app/main.py` (Lines 20-60)

**New Checks:**
1. On startup, reads `active_data_config.json`
2. Checks if `cohortName` is empty
3. If empty, extracts from `patients_file_path` or uses default
4. Verifies paths are complete (contain cohort name)
5. Regenerates paths if incomplete
6. Saves fixed config

**Startup Log Output:**
```
WARN: Config has empty cohortName, fixing...
INFO: Fixed cohortName to 'dummy_cohort1' with complete paths
WARN: Incomplete paths detected, regenerating...
INFO: Paths regenerated for cohort 'dummy_cohort1'
```

### 3. Added Debug Logging in `results.py`

**Location:** `app/routers/results.py` (Lines 57-71)

**New Debug Output:**
```python
print(f"DEBUG: Looking for results file at: {results_file}")
print(f"DEBUG: Cohort name: {cohort_name}")
print(f"DEBUG: Full path: {file_ops.get_full_path(results_file)}")
print(f"DEBUG: File exists: {file_ops.file_exists(results_file)}")
```

**Console Output:**
```
DEBUG: Looking for results file at: results_dir/matching/dummy_cohort1/matching_results.csv
DEBUG: Cohort name: dummy_cohort1
DEBUG: Full path: /Users/.../matching/dummy_cohort1/matching_results.csv
DEBUG: File exists: True
```

## Test Results

### ✅ Test 1: Config with Valid cohortName
```bash
GET /api/config
```
**Result:**
```json
{
  "cohortName": "dummy_cohort1",
  "matching_result_dir": "results_dir/matching/dummy_cohort1"
}
```
✅ **PASS** - Path is complete with cohort name

### ✅ Test 2: Results Endpoint
```bash
GET /api/results/summary
```
**Result:**
```json
{
  "has_results": true,
  "cohort_name": "dummy_cohort1",
  "total_patients": 25,
  "matched_count": 17
}
```
✅ **PASS** - Results file found and parsed

### ✅ Test 3: Empty cohortName with patients_file_path
```bash
POST /api/config
{
  "cohortName": "",
  "patients_file_path": "config_files/pipeline_json_files/dummy_cohort2.json"
}
```
**Result:**
```json
{
  "cohortName": "dummy_cohort2",
  "matching_result_dir": "results_dir/matching/dummy_cohort2"
}
```
**Log:** `INFO: Extracted cohort name 'dummy_cohort2' from patients_file_path`

✅ **PASS** - Cohort name extracted automatically

### ✅ Test 4: Startup Fix
**Server started with corrupted config (empty cohortName)**

**Startup Logs:**
```
WARN: Config has empty cohortName, fixing...
INFO: Fixed cohortName to 'dummy_cohort1' with complete paths
```
✅ **PASS** - Auto-fixed on startup

## How It Works

### User Flow 1: Frontend Sends cohortName
```
Frontend: POST /api/config
{
  "cohortName": "my_cohort",
  "patients_file_path": "config_files/pipeline_json_files/my_cohort.json"
}

Backend: ✅ Uses provided cohortName
Result: matching_result_dir = "results_dir/matching/my_cohort"
```

### User Flow 2: Frontend Sends Only patients_file_path
```
Frontend: POST /api/config
{
  "patients_file_path": "config_files/pipeline_json_files/my_cohort.json"
}

Backend: 
  1. Sees cohortName is empty/missing
  2. Extracts "my_cohort" from patients_file_path
  3. Logs: "INFO: Extracted cohort name 'my_cohort' from patients_file_path"

Result: 
  cohortName = "my_cohort"
  matching_result_dir = "results_dir/matching/my_cohort"
```

### User Flow 3: Backend Starts with Corrupted Config
```
active_data_config.json:
{
  "cohortName": "",
  "matching_result_dir": "results_dir/matching/"  ← INCOMPLETE!
}

Backend Startup:
  1. Detects empty cohortName
  2. Tries to extract from patients_file_path
  3. If no path, uses default "dummy_cohort1"
  4. Regenerates all paths
  5. Saves fixed config
  
Result: Config is auto-repaired
```

## Benefits

### 1. Robust Error Handling
- Never crashes on empty cohortName
- Always has a valid fallback
- Auto-repairs on startup

### 2. Smart Defaults
- Extracts cohort name from file path if needed
- Falls back to "dummy_cohort1" for initial setup
- Works out-of-the-box

### 3. Better Debugging
- Console logs show exactly what's happening
- Easy to troubleshoot path issues
- Clear INFO/WARN messages

### 4. Maintains Backward Compatibility
- Still accepts explicit cohortName (preferred)
- Adds fallback extraction as safety net
- No breaking changes to API

## Console Output Examples

### Successful Path Generation
```
DEBUG: Received config: {'cohortName': 'my_cohort', 'patients_file_path': '...'}
INFO:     127.0.0.1:62452 - "POST /api/config HTTP/1.1" 200 OK
```

### Automatic Extraction
```
DEBUG: Received config: {'cohortName': '', 'patients_file_path': 'config_files/pipeline_json_files/dummy_cohort2.json'}
INFO: Extracted cohort name 'dummy_cohort2' from patients_file_path
INFO:     127.0.0.1:62463 - "POST /api/config HTTP/1.1" 200 OK
```

### Startup Fix
```
WARN: Config has empty cohortName, fixing...
INFO: Fixed cohortName to 'dummy_cohort1' with complete paths
WARN: Incomplete paths detected, regenerating...
INFO: Paths regenerated for cohort 'dummy_cohort1'
Sigmatch backend initialized successfully!
```

### Results Found
```
DEBUG: Looking for results file at: results_dir/matching/dummy_cohort1/matching_results.csv
DEBUG: Cohort name: dummy_cohort1
DEBUG: Full path: /Users/rodela/.../matching/dummy_cohort1/matching_results.csv
DEBUG: File exists: True
INFO:     127.0.0.1:62441 - "GET /api/results/summary HTTP/1.1" 200 OK
```

## Files Modified

1. ✅ `app/services/config_manager.py` - Enhanced `auto_generate_paths()`
2. ✅ `app/main.py` - Added startup validation and repair
3. ✅ `app/routers/results.py` - Added debug logging

## Verification Checklist

- [✅] Config never has empty `cohortName`
- [✅] All paths include cohort folder name
- [✅] Results endpoint finds CSV files
- [✅] Extraction from `patients_file_path` works
- [✅] Startup auto-repairs corrupted configs
- [✅] Debug logs help troubleshooting
- [✅] Backward compatible with existing code

## Status

🟢 **ALL ISSUES RESOLVED**

The backend now:
- Intelligently extracts cohortName when missing
- Auto-repairs configs on startup
- Always generates complete paths
- Provides clear debug output
- Works reliably with ANY cohort

---

**Fixed:** December 27, 2024  
**Tested:** All scenarios passing  
**Ready for:** Production use

