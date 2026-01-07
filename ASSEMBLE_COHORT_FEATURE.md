# Assemble Cohort Feature Documentation

## Overview
The "Assemble Cohort" feature allows users to filter patients from an existing cohort based on multiple text-based criteria. The system performs keyword extraction and searches patient records to find matches.

## Endpoint

**POST** `/api/cohorts/assemble`

## Request Body

```json
{
  "criteria": ["patients who received gemcitabine", "patients who are male"],
  "max_patients": 100,
  "cohort_source": "dummy_cohort1.json"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `criteria` | `List[str]` | Yes | - | List of natural language criteria to filter patients. All criteria must match (AND logic). |
| `max_patients` | `int` | No | `100` | Maximum number of patients to search from the source cohort. |
| `cohort_source` | `str` | No | `"dummy_cohort1.json"` | The filename of the source cohort in `config_files/pipeline_json_files/`. |

## Response

```json
{
  "status": "success",
  "criteria_used": [
    "colorectal cancer",
    "male"
  ],
  "total_searched": 20,
  "matched_count": 18,
  "matched_patients": [
    {
      "patient_id": "P001",
      "match_reasons": [
        "Matches 'colorectal cancer' (found: colorectal)",
        "Matches 'male' (found: male)"
      ]
    }
  ],
  "patient_ids_list": ["P001", "P002", "P003"]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | Status of the operation (`"success"` or error message). |
| `criteria_used` | `List[str]` | The original criteria used for filtering. |
| `total_searched` | `int` | Total number of patients searched. |
| `matched_count` | `int` | Number of patients that matched all criteria. |
| `matched_patients` | `List[MatchedPatient]` | Detailed list of matched patients with reasons. |
| `patient_ids_list` | `List[str]` | Simple list of matched patient IDs for convenience. |

## How It Works

### 1. Keyword Extraction
The system extracts meaningful keywords from each criterion by:
- Converting to lowercase
- Removing common "stop words" (I, want, patients, who, are, the, a, and, etc.)
- Filtering out words with less than 3 characters

**Example:**
- Input: `"patients who received gemcitabine"`
- Keywords extracted: `["gemcitabine"]`

### 2. Patient Matching
For each patient in the source cohort:
- The system searches the patient's `full_text` field (clinical notes)
- **ALL criteria must match** (AND logic)
- For each criterion, **at least one keyword** must appear in the text

### 3. Match Reasons
The response includes detailed match reasons showing:
- Which criterion was matched
- Which specific keywords were found

## Example Use Cases

### Use Case 1: Find Male Colorectal Cancer Patients

```bash
curl -X POST http://localhost:8000/api/cohorts/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": ["colorectal cancer", "male"],
    "max_patients": 50,
    "cohort_source": "dummy_cohort1.json"
  }'
```

### Use Case 2: Find Stage III Patients Who Had Surgery

```bash
curl -X POST http://localhost:8000/api/cohorts/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": ["stage III", "surgery"],
    "max_patients": 100,
    "cohort_source": "dummy_cohort1.json"
  }'
```

### Use Case 3: Multiple Specific Criteria

```bash
curl -X POST http://localhost:8000/api/cohorts/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": [
      "metastatic disease",
      "receiving chemotherapy",
      "ECOG performance status 1"
    ],
    "max_patients": 200,
    "cohort_source": "dummy_cohort2.json"
  }'
```

## Frontend Integration

For the Lovable frontend, you can integrate this feature as follows:

### 1. UI Components Needed
- **Criteria Input**: Multiple text inputs or a textarea where users can add criteria (one per line or use a dynamic list with "Add Criterion" button)
- **Max Patients Dropdown**: Selector with options like 50, 100, 200, 500
- **Cohort Source Dropdown**: Pre-populated with available cohorts from `/api/cohorts`
- **Identify Patients Button**: Triggers the API call
- **Results Display**: Show matched patient IDs and match reasons

### 2. Example React/JavaScript Code

```javascript
const API_BASE = 'http://localhost:8000';

async function assembleCohort(criteria, maxPatients = 100, cohortSource = 'dummy_cohort1.json') {
  const response = await fetch(`${API_BASE}/api/cohorts/assemble`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      criteria,
      max_patients: maxPatients,
      cohort_source: cohortSource,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
const result = await assembleCohort(
  ['colorectal cancer', 'male', 'stage III'],
  100,
  'dummy_cohort1.json'
);

console.log(`Found ${result.matched_count} patients out of ${result.total_searched} searched`);
console.log('Patient IDs:', result.patient_ids_list);
```

### 3. UI Flow
1. User enters criteria (e.g., "I want patients who received gemcitabine", "I want patients who are male")
2. User selects max patients to search (default: 100)
3. User selects source cohort (dropdown)
4. User clicks "Identify Patients" button
5. Loading spinner appears
6. Results display:
   - Summary: "Found 12 patients out of 100 searched"
   - Patient IDs list: "P001, P003, P005, ..."
   - Detailed match reasons (expandable)

## Technical Implementation Details

### Files Modified
1. **`app/models/schemas.py`**: Added new Pydantic models
   - `CohortAssembleRequest`
   - `MatchedPatient`
   - `CohortAssembleResponse`

2. **`app/routers/cohorts.py`**: Added new endpoint and helper function
   - `extract_keywords()`: Helper function to extract meaningful keywords
   - `POST /api/cohorts/assemble`: Main endpoint implementation

### Algorithm Details
- **Matching Logic**: AND across criteria, OR within keywords of a single criterion
- **Case Sensitivity**: Case-insensitive search
- **Stop Words**: Common words are filtered out to improve matching accuracy
- **Performance**: Searches are limited by `max_patients` to prevent timeouts

## Testing

The feature has been tested with:
1. ✅ Empty criteria (returns 0 matches)
2. ✅ Multiple criteria with male colorectal cancer patients
3. ✅ Specific criteria with stage and surgery keywords
4. ✅ Server auto-reload on code changes
5. ✅ Proper JSON response format

## Future Enhancements (Optional)

- Add OR logic option alongside AND logic
- Support for advanced operators (NOT, exact phrase matching)
- Save assembled cohorts as new cohort files
- Integration with LLM for more intelligent criteria parsing
- Real-time search as user types
- Export matched patients to CSV

