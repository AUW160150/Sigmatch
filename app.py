"""
Sigmatch Streamlit App - Clinical Trial Matching Interface
Replicates the Lovable React frontend functionality

FILE STRUCTURE (Noah's SageMaker):
/sigmatch/                              ← Parent directory (BASE_DIR)
├── config_files/
├── documents/
├── results_dir/
├── orchestrate_pipeline.py             ← Pipeline script
└── streamlit_frontend/                 ← This app folder
    └── app.py                          ← YOU ARE HERE
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import shutil
import subprocess
import sys
import os

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Streamlit app is in: /sigmatch/streamlit_frontend/app.py
# Data files are in:   /sigmatch/
# So we go ONE LEVEL UP from the app's directory

BASE_DIR = Path(__file__).resolve().parent.parent  # Goes up to /sigmatch/

# Config files
CONFIG_DIR = BASE_DIR / "config_files"
OVERALL_CONFIG = CONFIG_DIR / "overall_config_settings" / "active_data_config.json"
PROMPT_SETTINGS = CONFIG_DIR / "prompt_settings" / "sigmatch_standard_prompt_content.json"
TRIAL_FILES_DIR = CONFIG_DIR / "trial_files"
COHORT_FILES_DIR = CONFIG_DIR / "pipeline_json_files"

# Documents
DOCUMENTS_DIR = BASE_DIR / "documents"
OCR_DIR = DOCUMENTS_DIR / "ocr"
PDF_DIR = DOCUMENTS_DIR / "pdfs"

# Results
RESULTS_DIR = BASE_DIR / "results_dir"
MATCHING_DIR = RESULTS_DIR / "matching"
LLM_SUMMARIZATION_DIR = RESULTS_DIR / "llm_summarization"
EVALUATION_DIR = RESULTS_DIR / "evaluation"

# Pipeline script (at root level, same as BASE_DIR)
PIPELINE_SCRIPT = BASE_DIR / "orchestrate_pipeline.py"

# Snapshots
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

# =============================================================================
# STREAMLIT CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Sigmatch",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #3b82f6;
        --primary-hover: #2563eb;
        --success: #22c55e;
        --destructive: #ef4444;
        --muted: #f1f5f9;
        --border: #e2e8f0;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    
    /* Secondary button */
    .secondary-btn button {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }
    .secondary-btn button:hover {
        background-color: #e2e8f0 !important;
    }
    
    /* Success box */
    .success-box {
        padding: 1rem;
        background-color: #dcfce7;
        border-radius: 0.5rem;
        border: 1px solid #86efac;
        margin: 0.5rem 0;
    }
    
    /* Error box */
    .error-box {
        padding: 1rem;
        background-color: #fee2e2;
        border-radius: 0.5rem;
        border: 1px solid #fca5a5;
        margin: 0.5rem 0;
    }
    
    /* Info box */
    .info-box {
        padding: 1rem;
        background-color: #dbeafe;
        border-radius: 0.5rem;
        border: 1px solid #93c5fd;
        margin: 0.5rem 0;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
    
    /* Patient ID badge */
    .patient-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        background-color: #dbeafe;
        color: #1d4ed8;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
        border: 1px solid #93c5fd;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #3b82f6;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .assistant-message {
        background-color: #f1f5f9;
        color: #1e293b;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    /* Stat card */
    .stat-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 0.75rem;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Code block */
    .code-block {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.875rem;
        overflow-x: auto;
    }
    
    /* Header styling */
    .main-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Results display */
    .results-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        min-height: 200px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_paths_info() -> Dict[str, str]:
    """Return all important paths for display."""
    return {
        "base_dir": str(BASE_DIR.resolve()),
        "pipeline_script": str(PIPELINE_SCRIPT.resolve()),
        "config_dir": str(CONFIG_DIR.resolve()),
        "trials_dir": str(TRIAL_FILES_DIR.resolve()),
        "cohorts_dir": str(COHORT_FILES_DIR.resolve()),
        "results_dir": str(RESULTS_DIR.resolve()),
        "active_config": str(OVERALL_CONFIG.resolve()),
    }

def load_json(relative_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file from path relative to BASE_DIR."""
    try:
        full_path = BASE_DIR / relative_path
        if not full_path.exists():
            return None
        with open(full_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {relative_path}: {e}")
        return None

def save_json(relative_path: str, data: Dict[str, Any]) -> bool:
    """Save JSON file to path relative to BASE_DIR."""
    try:
        full_path = BASE_DIR / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False

def get_trials() -> List[Dict[str, str]]:
    """Get all trial files from trial_files directory."""
    if not TRIAL_FILES_DIR.exists():
        return []
    
    trials = []
    for f in TRIAL_FILES_DIR.glob("*.json"):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
            trials.append({
                "filename": f.name,
                "title": data.get("title", f.stem),
                "_id": data.get("_id", f.stem)
            })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            trials.append({
                "filename": f.name,
                "title": f.stem,
                "_id": f.stem
            })
    return trials

def get_cohorts() -> List[Dict[str, Any]]:
    """Get all cohort files from pipeline_json_files directory."""
    if not COHORT_FILES_DIR.exists():
        return []
    
    cohorts = []
    for f in COHORT_FILES_DIR.glob("*.json"):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
            cohorts.append({
                "filename": f.name,
                "name": f.stem,
                "patient_count": len(data) if isinstance(data, list) else 0
            })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            cohorts.append({
                "filename": f.name,
                "name": f.stem,
                "patient_count": 0
            })
    return cohorts

def get_active_config() -> Dict[str, Any]:
    """Load the active configuration."""
    if OVERALL_CONFIG.exists():
        try:
            with open(OVERALL_CONFIG, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

def save_active_config(config: Dict[str, Any]) -> bool:
    """Save configuration with versioning and auto-generated paths."""
    cohort_name = config.get("cohortName", "default")
    
    # Auto-generate paths based on cohortName
    config["pdf_data_dir"] = f"documents/pdfs/{cohort_name}"
    config["ocr_data_dir"] = f"documents/ocr/{cohort_name}"
    config["llm_summarization_result_dir"] = f"results_dir/llm_summarization/{cohort_name}"
    config["matching_result_dir"] = f"results_dir/matching/{cohort_name}"
    config["extracted_features_path"] = f"results_dir/llm_summarization/{cohort_name}/patient_feature_summaries_{cohort_name}.csv"
    config["evaluation_results_path"] = f"results_dir/evaluation/matching_results_summary_{cohort_name}.xlsx"
    
    # Create directories if needed
    (BASE_DIR / config["matching_result_dir"]).mkdir(parents=True, exist_ok=True)
    (BASE_DIR / config["llm_summarization_result_dir"]).mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"data_config_{cohort_name}__{timestamp}.json"
    save_json(f"config_files/overall_config_settings/{backup_filename}", config)
    
    # Save as active config
    return save_json("config_files/overall_config_settings/active_data_config.json", config)

def assemble_cohort(criteria_list: List[str], cohort_source: str, max_patients: int) -> Dict[str, Any]:
    """Assemble a cohort based on search criteria."""
    try:
        cohort_path = COHORT_FILES_DIR / cohort_source
        if not cohort_path.exists():
            return {"matched_count": 0, "patient_ids_list": []}
        
        with open(cohort_path, 'r') as f:
            cohort = json.load(f)
        
        if not isinstance(cohort, list):
            return {"matched_count": 0, "patient_ids_list": []}
        
        stop_words = {'i', 'want', 'patients', 'who', 'are', 'is', 'the', 'a', 'in', 'with', 
                      'have', 'has', 'had', 'and', 'or', 'of', 'to', 'for', 'on', 'at'}
        
        matched = []
        for patient in cohort[:max_patients]:
            text = patient.get('full_text', '').lower()
            all_match = True
            
            for criterion in criteria_list:
                if not criterion.strip():
                    continue
                keywords = [w for w in criterion.lower().split() 
                           if w not in stop_words and len(w) > 2]
                if keywords and not any(kw in text for kw in keywords):
                    all_match = False
                    break
            
            if all_match:
                matched.append(patient.get('patient_id', 'Unknown'))
        
        return {
            "matched_count": len(matched),
            "patient_ids_list": matched
        }
    except Exception as e:
        st.error(f"Error assembling cohort: {e}")
        return {"matched_count": 0, "patient_ids_list": []}

def generate_pipeline_command(run_ocr: bool, do_llm_summarization: bool, 
                              do_patient_matching: bool, do_evaluation: bool) -> str:
    """Generate the pipeline command string for display/debugging."""
    config_path = "config_files/overall_config_settings/active_data_config.json"
    return (f"python orchestrate_pipeline.py "
            f"--data_config_json {config_path} "
            f"--run_ocr {run_ocr} "
            f"--do_llm_summarization {do_llm_summarization} "
            f"--do_patient_matching {do_patient_matching} "
            f"--do_evaluation {do_evaluation}")

def run_pipeline(run_ocr: bool, do_llm_summarization: bool, 
                 do_patient_matching: bool, do_evaluation: bool) -> Dict[str, Any]:
    """Run Noah's pipeline directly and return results."""
    
    # Check if pipeline script exists
    if not PIPELINE_SCRIPT.exists():
        return {
            "error": f"Pipeline script not found at:\n{PIPELINE_SCRIPT}\n\n"
                     f"orchestrate_pipeline.py should be in the sigmatch root folder:\n{BASE_DIR}",
            "hint": "Make sure orchestrate_pipeline.py is in the correct location",
            "success": False
        }
    
    config_path = "config_files/overall_config_settings/active_data_config.json"
    
    # Build command
    cmd = [
        sys.executable,  # Use current Python interpreter
        str(PIPELINE_SCRIPT),
        "--data_config_json", config_path,
        "--run_ocr", str(run_ocr),
        "--do_llm_summarization", str(do_llm_summarization),
        "--do_patient_matching", str(do_patient_matching),
        "--do_evaluation", str(do_evaluation)
    ]
    
    try:
        # Set up environment - inherit current environment
        env = os.environ.copy()
        
        # Run pipeline with timeout from BASE_DIR
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),  # Run from sigmatch root
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour timeout
            env=env
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(cmd)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Pipeline timed out after 1 hour. The process may still be running.",
            "success": False
        }
    except FileNotFoundError as e:
        return {
            "error": f"Python interpreter not found: {e}",
            "success": False
        }
    except PermissionError as e:
        return {
            "error": f"Permission denied: {e}. Make sure orchestrate_pipeline.py is executable.",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Unexpected error running pipeline: {str(e)}",
            "success": False
        }

def save_snapshot() -> str:
    """Save a snapshot of all config files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = SNAPSHOTS_DIR / f"snapshot_{timestamp}"
    
    try:
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy config files
        if CONFIG_DIR.exists():
            shutil.copytree(CONFIG_DIR, snapshot_dir / "config_files")
        
        return str(snapshot_dir)
    except Exception as e:
        raise Exception(f"Failed to save snapshot: {e}")

def get_prompts() -> Dict[str, Any]:
    """Load prompt settings."""
    if PROMPT_SETTINGS.exists():
        try:
            with open(PROMPT_SETTINGS, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading prompts: {e}")
    return {}

def save_prompts(prompts: Dict[str, Any]) -> bool:
    """Save prompt settings with versioning."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup current
    save_json(f"config_files/prompt_settings/sigmatch_standard_prompt_content_{timestamp}.json", prompts)
    
    # Save as current
    return save_json("config_files/prompt_settings/sigmatch_standard_prompt_content.json", prompts)

def get_results_summary() -> Dict[str, Any]:
    """Get summary of matching results."""
    config = get_active_config()
    cohort_name = config.get("cohortName", "unknown")
    matching_result_dir = config.get("matching_result_dir", "")
    
    # Build results path
    if matching_result_dir:
        results_csv = BASE_DIR / matching_result_dir / "matching_results.csv"
    else:
        results_csv = MATCHING_DIR / cohort_name / "matching_results.csv"
    
    if not results_csv.exists():
        return {
            "has_results": False,
            "cohort_name": cohort_name,
            "total_patients": 0,
            "matched_count": 0,
            "not_matched_count": 0,
            "match_percentage": 0,
            "score_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        }
    
    try:
        df = pd.read_csv(results_csv)
        
        total = len(df)
        matched = len(df[df['final_decision'] == 'MATCH'])
        not_matched = total - matched
        match_pct = round(matched / total * 100, 1) if total > 0 else 0
        
        # Score distribution
        score_dist = df['overall_score'].value_counts().to_dict()
        score_distribution = {str(i): score_dist.get(i, 0) for i in range(1, 6)}
        
        return {
            "has_results": True,
            "cohort_name": cohort_name,
            "total_patients": total,
            "matched_count": matched,
            "not_matched_count": not_matched,
            "match_percentage": match_pct,
            "score_distribution": score_distribution,
            "dataframe": df
        }
    except Exception as e:
        return {"has_results": False, "error": str(e)}

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'criteria_list' not in st.session_state:
    st.session_state.criteria_list = ['']

if 'assemble_results' not in st.session_state:
    st.session_state.assemble_results = None

if 'config' not in st.session_state:
    st.session_state.config = get_active_config()

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'prompts' not in st.session_state:
    st.session_state.prompts = get_prompts()

if 'pipeline_result' not in st.session_state:
    st.session_state.pipeline_result = None

# =============================================================================
# PAGE FUNCTIONS
# =============================================================================

def page_setup_paths():
    """Setup & Paths page - Verify file structure."""
    st.markdown('<p class="main-header">📁 Setup & File Paths</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Verify your file structure and paths</p>', unsafe_allow_html=True)
    
    paths = get_paths_info()
    
    # Check what exists
    pipeline_exists = PIPELINE_SCRIPT.exists()
    config_exists = OVERALL_CONFIG.exists()
    trials_exist = len(list(TRIAL_FILES_DIR.glob("*.json"))) > 0 if TRIAL_FILES_DIR.exists() else False
    cohorts_exist = len(list(COHORT_FILES_DIR.glob("*.json"))) > 0 if COHORT_FILES_DIR.exists() else False
    
    st.subheader("Status Check")
    col1, col2 = st.columns(2)
    
    with col1:
        if pipeline_exists:
            st.success("✅ orchestrate_pipeline.py found")
        else:
            st.error("❌ orchestrate_pipeline.py NOT found")
        
        if config_exists:
            st.success("✅ Config file found")
        else:
            st.warning("⚠️ Config file missing (will be created)")
    
    with col2:
        if trials_exist:
            trial_count = len(list(TRIAL_FILES_DIR.glob("*.json")))
            st.success(f"✅ Trial files found ({trial_count} files)")
        else:
            st.warning("⚠️ No trial files")
        
        if cohorts_exist:
            cohort_count = len(list(COHORT_FILES_DIR.glob("*.json")))
            st.success(f"✅ Cohort files found ({cohort_count} files)")
        else:
            st.warning("⚠️ No cohort files")
    
    st.divider()
    
    st.subheader("Expected File Structure")
    st.code(f"""
{paths['base_dir']}/
├── orchestrate_pipeline.py      ← Pipeline script {'✅' if pipeline_exists else '❌'}
├── config_files/
│   ├── overall_config_settings/
│   │   └── active_data_config.json {'✅' if config_exists else '⚠️'}
│   ├── prompt_settings/
│   │   └── sigmatch_standard_prompt_content.json
│   ├── trial_files/
│   │   └── *.json               ← Trial files {'✅' if trials_exist else '⚠️'}
│   └── pipeline_json_files/
│       └── *.json               ← Patient cohorts {'✅' if cohorts_exist else '⚠️'}
├── documents/
│   ├── ocr/
│   └── pdfs/
├── results_dir/
│   └── matching/
│       └── {{cohort_name}}/
│           └── matching_results.csv
│
└── streamlit_frontend/
    └── app.py                   ← This app (YOU ARE HERE)
    """)
    
    st.divider()
    
    st.subheader("Resolved Paths")
    for name, path in paths.items():
        exists = Path(path).exists()
        icon = "✅" if exists else "❌"
        st.text(f"{icon} {name}: {path}")
    
    st.divider()
    
    if st.button("🔄 Refresh Status"):
        st.rerun()


def page_configure():
    """Configure Pipeline page - Main configuration interface."""
    st.markdown('<p class="main-header">Configure Pipeline</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Set up your clinical trial matching parameters</p>', unsafe_allow_html=True)
    
    # Load current config
    config = st.session_state.config
    trials = get_trials()
    cohorts = get_cohorts()
    
    # =========================================================================
    # ASSEMBLE COHORT SECTION (Full Width)
    # =========================================================================
    st.markdown("### 👥 Assemble Cohort")
    st.markdown("Define criteria to identify matching patients from a cohort source")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Patient Criteria**")
        
        # Dynamic criteria inputs
        for i, criterion in enumerate(st.session_state.criteria_list):
            cols = st.columns([6, 1])
            with cols[0]:
                st.session_state.criteria_list[i] = st.text_input(
                    f"Criterion {i+1}",
                    value=criterion,
                    placeholder="e.g., patients who received gemcitabine",
                    key=f"criterion_{i}",
                    label_visibility="collapsed"
                )
            with cols[1]:
                if len(st.session_state.criteria_list) > 1:
                    if st.button("✕", key=f"remove_{i}"):
                        st.session_state.criteria_list.pop(i)
                        st.rerun()
        
        if st.button("➕ Add Criterion"):
            st.session_state.criteria_list.append('')
            st.rerun()
        
        st.markdown("---")
        
        # Cohort source and max patients
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            cohort_options = [c['filename'] for c in cohorts]
            selected_cohort_source = st.selectbox(
                "Cohort Source",
                options=cohort_options if cohort_options else ["No cohorts available"],
                key="cohort_source"
            )
        
        with subcol2:
            max_patients = st.selectbox(
                "Max Patients",
                options=[25, 50, 100, 250, 500],
                index=1,
                key="max_patients"
            )
        
        if st.button("🔍 Identify Patients", type="primary"):
            valid_criteria = [c for c in st.session_state.criteria_list if c.strip()]
            if not valid_criteria:
                st.warning("Please add at least one criterion.")
            elif not selected_cohort_source or selected_cohort_source == "No cohorts available":
                st.warning("Please select a cohort source.")
            else:
                with st.spinner("Searching patients..."):
                    results = assemble_cohort(valid_criteria, selected_cohort_source, max_patients)
                    st.session_state.assemble_results = results
    
    with col2:
        st.markdown("**Results**")
        results_container = st.container()
        with results_container:
            if st.session_state.assemble_results:
                results = st.session_state.assemble_results
                if results['matched_count'] > 0:
                    st.success(f"Found **{results['matched_count']}** patients:")
                    
                    # Display patient IDs as badges
                    badges_html = ""
                    for pid in results['patient_ids_list']:
                        badges_html += f'<span class="patient-badge">{pid}</span>'
                    st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">{badges_html}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.warning("No patients found matching all criteria.")
            else:
                st.markdown('<div class="results-container">'
                           '<p style="color: #64748b; text-align: center; padding-top: 80px;">'
                           'Enter criteria and click "Identify Patients" to find matching patients.</p>'
                           '</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # =========================================================================
    # TRIAL AND COHORT SELECTION (2 columns)
    # =========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Trial Selection")
        st.markdown("Choose or upload a clinical trial")
        
        if not trials:
            st.warning("No trial files found. Add trial JSON files to config_files/trial_files/")
            selected_trial = None
        else:
            # Trial dropdown
            trial_options = {t['filename']: t['title'] for t in trials}
            current_trial = config.get('trial_file_config_path', '').split('/')[-1] if config.get('trial_file_config_path') else None
            
            selected_trial = st.selectbox(
                "Select Trial",
                options=list(trial_options.keys()),
                format_func=lambda x: trial_options.get(x, x),
                index=list(trial_options.keys()).index(current_trial) if current_trial in trial_options else 0,
                key="selected_trial"
            )
        
        # File upload
        uploaded_file = st.file_uploader("Upload Trial JSON", type=['json'], key="trial_upload")
        if uploaded_file:
            try:
                trial_data = json.load(uploaded_file)
                filename = uploaded_file.name
                save_json(f"config_files/trial_files/{filename}", trial_data)
                st.success(f"Trial '{filename}' uploaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error uploading file: {e}")
        
        # Create from free text
        with st.expander("📝 Create from free text"):
            new_trial_title = st.text_input("Trial Title", key="new_trial_title")
            new_trial_description = st.text_area("Trial Description (Full Text)", 
                                                  height=150, key="new_trial_desc")
            
            if st.button("💾 Save Trial"):
                if new_trial_title and new_trial_description:
                    trial_id = new_trial_title.lower().replace(' ', '_').replace('-', '_')
                    filename = f"{trial_id}.json"
                    trial_data = {
                        "_id": trial_id,
                        "title": new_trial_title,
                        "full_text": new_trial_description
                    }
                    if save_json(f"config_files/trial_files/{filename}", trial_data):
                        st.success("Trial created successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill in both title and description.")
    
    with col2:
        st.markdown("### 📊 Cohort Selection")
        st.markdown("Select patient cohort for matching")
        
        # Get cohort names from directory
        cohort_names = [c['name'] for c in cohorts]
        
        if not cohort_names:
            st.warning("No cohort files found. Add cohort JSON files to config_files/pipeline_json_files/")
            cohort_type = 'custom'
        else:
            # Radio selection for cohorts
            cohort_type = st.radio(
                "Choose cohort",
                options=cohort_names + ['custom'],
                key="cohort_type"
            )
        
        custom_path = ""
        if cohort_type == 'custom':
            custom_path = st.text_input(
                "Custom Path",
                placeholder="config_files/pipeline_json_files/...",
                key="custom_cohort_path"
            )
        
        # Cohort name input
        cohort_name = st.text_input(
            "Cohort Name",
            value=config.get('cohortName', ''),
            key="cohort_name"
        )
    
    st.divider()
    
    # =========================================================================
    # PIPELINE STEPS AND ACTIONS (2 columns)
    # =========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Pipeline Steps")
        st.markdown("Select which steps to run")
        
        run_ocr = st.checkbox("OCR", value=False, key="run_ocr")
        do_llm_summarization = st.checkbox("LLM Summarization", value=True, key="do_llm_sum")
        do_patient_matching = st.checkbox("Patient Matching", value=True, key="do_matching")
        do_evaluation = st.checkbox("Evaluation", value=False, key="do_eval")
    
    with col2:
        st.markdown("### 🚀 Actions")
        st.markdown("Run pipeline or save configuration")
        
        # Run Pipeline Section
        run_pipeline_btn = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)
        
        if run_pipeline_btn:
            # First save the current config
            updated_config = {
                **config,
                "cohortName": cohort_name,
                "trial_file_config_path": f"config_files/trial_files/{selected_trial}" if selected_trial else "",
                "patients_file_path": f"config_files/pipeline_json_files/{cohort_type}.json" if cohort_type != 'custom' else custom_path,
            }
            
            save_active_config(updated_config)
            st.session_state.config = updated_config
            
            # Show progress
            with st.spinner("🔄 Running pipeline... This may take several minutes."):
                result = run_pipeline(
                    run_ocr=run_ocr,
                    do_llm_summarization=do_llm_summarization,
                    do_patient_matching=do_patient_matching,
                    do_evaluation=do_evaluation
                )
                st.session_state.pipeline_result = result
            
            # Display results
            if result.get("error"):
                st.error(f"❌ Pipeline failed: {result['error']}")
                if result.get("hint"):
                    st.info(f"💡 Hint: {result['hint']}")
            elif result.get("success"):
                st.success("✅ Pipeline completed successfully!")
                st.balloons()
                st.info("📊 View your results in the 'Results Summary' page")
            else:
                st.error("❌ Pipeline failed. Check the output below for details.")
        
        # Show pipeline results if available
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            
            if result.get("stdout"):
                with st.expander("📄 View Pipeline Output", expanded=not result.get("success", False)):
                    st.code(result.get("stdout", ""), language="text")
            
            if result.get("stderr"):
                with st.expander("⚠️ View Warnings/Errors"):
                    st.code(result.get("stderr", ""), language="text")
        
        st.markdown("---")
        
        # Secondary actions
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📸 Save Snapshot", use_container_width=True):
                try:
                    snapshot_path = save_snapshot()
                    st.success(f"Snapshot saved!")
                except Exception as e:
                    st.error(str(e))
        
        with col_b:
            if st.button("💾 Save Config", use_container_width=True):
                # Update config with current selections
                updated_config = {
                    **config,
                    "cohortName": cohort_name,
                    "trial_file_config_path": f"config_files/trial_files/{selected_trial}" if selected_trial else "",
                    "patients_file_path": f"config_files/pipeline_json_files/{cohort_type}.json" if cohort_type != 'custom' else custom_path,
                }
                
                if save_active_config(updated_config):
                    st.session_state.config = updated_config
                    st.success("Configuration saved!")
        
        # Debug command expander
        with st.expander("🔧 View Pipeline Command (for debugging)"):
            cmd_str = generate_pipeline_command(
                run_ocr, do_llm_summarization, do_patient_matching, do_evaluation
            )
            st.code(cmd_str, language="bash")
            st.caption("Copy this command to run the pipeline manually in a terminal.")


def page_adjust_prompts():
    """Adjust Prompts page - Configure AI agent prompts."""
    st.markdown('<p class="main-header">Adjust Prompts</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure AI agent system and main prompts</p>', unsafe_allow_html=True)
    
    # Save All button at top
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("💾 Save All Prompts", type="primary"):
            if save_prompts(st.session_state.prompts):
                st.success("All prompts saved successfully!")
    
    # Agent labels
    agent_labels = {
        "final_decision_agent": "Final Decision Agent",
        "eligibility_checker_agent": "Eligibility Checker Agent",
        "trial_analyzer_agent": "Trial Analyzer Agent",
        "patient_analyzer_agent": "Patient Analyzer Agent",
        "patient_record_summarize": "Patient Record Summarizer",
        "extract_features": "Feature Extractor"
    }
    
    prompts = st.session_state.prompts
    
    st.markdown("### 🤖 Agent Prompts")
    st.markdown("Edit system and main prompts for each AI agent")
    
    # Create tabs for each agent
    if prompts:
        tabs = st.tabs([agent_labels.get(name, name) for name in prompts.keys()])
        
        for i, (agent_name, prompt_data) in enumerate(prompts.items()):
            with tabs[i]:
                # Skip toggle
                skip_val = prompt_data.get('skip', False)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{agent_labels.get(agent_name, agent_name)}**")
                with col2:
                    new_skip = st.checkbox("Skip", value=skip_val, key=f"skip_{agent_name}")
                    if new_skip != skip_val:
                        st.session_state.prompts[agent_name]['skip'] = new_skip
                
                if skip_val:
                    st.info("This agent is currently skipped in the pipeline.")
                
                # System prompt
                st.markdown("**System Prompt**")
                system_prompt = st.text_area(
                    "System Prompt",
                    value=prompt_data.get('system_prompt', ''),
                    height=150,
                    key=f"sys_{agent_name}",
                    label_visibility="collapsed"
                )
                
                # Main prompt
                st.markdown("**Main Prompt**")
                main_prompt = st.text_area(
                    "Main Prompt",
                    value=prompt_data.get('main_prompt', ''),
                    height=200,
                    key=f"main_{agent_name}",
                    label_visibility="collapsed"
                )
                
                # Save individual agent
                if st.button(f"💾 Save {agent_labels.get(agent_name, agent_name)}", key=f"save_{agent_name}"):
                    st.session_state.prompts[agent_name]['system_prompt'] = system_prompt
                    st.session_state.prompts[agent_name]['main_prompt'] = main_prompt
                    if save_prompts(st.session_state.prompts):
                        st.success(f"{agent_labels.get(agent_name, agent_name)} saved!")
    else:
        st.warning("No prompts found. Check your prompt settings file at config_files/prompt_settings/")


def page_evaluation_criteria():
    """Evaluation Criteria page - Chat interface for criteria configuration."""
    st.markdown('<p class="main-header">Evaluation Criteria</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure criteria through conversation</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Chat")
        st.markdown("Discuss and refine evaluation criteria")
        
        # Chat container
        chat_container = st.container(height=400)
        
        with chat_container:
            if not st.session_state.chat_messages:
                st.markdown("""
                <div style="text-align: center; padding: 100px 20px; color: #64748b;">
                    <p style="font-size: 2rem;">💬</p>
                    <p>No messages yet. Start the conversation!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_messages:
                    if msg['role'] == 'user':
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin: 0.5rem 0;">
                            <div class="user-message">{msg['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin: 0.5rem 0;">
                            <div class="assistant-message">{msg['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Input area
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input("Type your message...", key="chat_input", 
                                       label_visibility="collapsed", 
                                       placeholder="Type your message...")
        with col_btn:
            send_clicked = st.button("➤", key="send_btn")
        
        if send_clicked and user_input:
            # Add user message
            st.session_state.chat_messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Generate response (simple echo for now)
            response = f'I received your message: "{user_input}". How can I help you refine the evaluation criteria?'
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': response
            })
            
            st.rerun()
    
    with col2:
        st.markdown("### 📋 Final Evaluation Criteria")
        st.markdown("Enter the final criteria for patient matching evaluation")
        
        criteria_text = st.text_area(
            "Evaluation Criteria",
            height=350,
            placeholder="Enter your evaluation criteria here...",
            key="final_criteria",
            label_visibility="collapsed"
        )
        
        if st.button("💾 Save Criteria", type="primary", use_container_width=True):
            if criteria_text:
                # Save to a criteria file
                criteria_data = {
                    "criteria": criteria_text,
                    "updated_at": datetime.now().isoformat(),
                    "chat_history": st.session_state.chat_messages
                }
                if save_json("config_files/other_config_files/evaluation_criteria.json", criteria_data):
                    st.success("Evaluation criteria saved successfully!")
            else:
                st.warning("Please enter evaluation criteria.")


def page_review_results():
    """Review Results page - Manual review placeholder."""
    st.markdown('<p class="main-header">Manual Review Results</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Review and approve/reject patient matches</p>', unsafe_allow_html=True)
    
    st.markdown("### 📋 Patient Matches")
    
    # Info box
    st.markdown("""
    <div style="border: 2px dashed #e2e8f0; border-radius: 0.5rem; padding: 2rem; text-align: center; margin: 1rem 0;">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🕐</p>
        <h3 style="margin-bottom: 0.5rem;">Feature In Development</h3>
        <p style="color: #64748b;">
            The manual review functionality is currently being developed. 
            Below is a preview of how it will look.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dummy data for preview
    dummy_patients = [
        {"id": "PT-001", "decision": "Matched", "score": 4.2, "status": "pending"},
        {"id": "PT-002", "decision": "Not Matched", "score": 2.1, "status": "pending"},
        {"id": "PT-003", "decision": "Matched", "score": 4.8, "status": "approved"},
        {"id": "PT-004", "decision": "Matched", "score": 3.5, "status": "rejected"},
    ]
    
    # Display table with custom formatting
    st.markdown("---")
    
    # Header row
    cols = st.columns([1, 1.5, 1, 1, 2])
    cols[0].markdown("**Patient ID**")
    cols[1].markdown("**Decision**")
    cols[2].markdown("**Score**")
    cols[3].markdown("**Status**")
    cols[4].markdown("**Actions**")
    
    st.markdown("---")
    
    # Data rows
    for patient in dummy_patients:
        cols = st.columns([1, 1.5, 1, 1, 2])
        
        cols[0].write(patient['id'])
        
        # Decision badge
        if patient['decision'] == 'Matched':
            cols[1].markdown(f'<span style="background-color: #22c55e; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["decision"]}</span>', unsafe_allow_html=True)
        else:
            cols[1].markdown(f'<span style="background-color: #64748b; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["decision"]}</span>', unsafe_allow_html=True)
        
        cols[2].write(f"{patient['score']:.1f}")
        
        # Status badge
        status_colors = {
            'pending': '#f59e0b',
            'approved': '#22c55e',
            'rejected': '#ef4444'
        }
        cols[3].markdown(f'<span style="border: 1px solid {status_colors[patient["status"]]}; color: {status_colors[patient["status"]]}; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["status"]}</span>', unsafe_allow_html=True)
        
        # Action buttons (disabled)
        with cols[4]:
            btn_cols = st.columns(2)
            btn_cols[0].button("✓ Approve", key=f"approve_{patient['id']}", disabled=True)
            btn_cols[1].button("✕ Reject", key=f"reject_{patient['id']}", disabled=True)


def page_results_summary():
    """Results Summary page - Display matching results and statistics."""
    st.markdown('<p class="main-header">Results Summary</p>', unsafe_allow_html=True)
    
    # Refresh button at the top
    col_header1, col_header2 = st.columns([4, 1])
    with col_header2:
        if st.button("🔄 Refresh Results"):
            st.rerun()
    
    summary = get_results_summary()
    
    if not summary.get('has_results'):
        st.markdown('<p class="sub-header">View matching results and statistics</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; border: 1px solid #e2e8f0; border-radius: 0.75rem; margin: 2rem 0;">
            <p style="font-size: 4rem; margin-bottom: 1rem;">⚠️</p>
            <h3 style="margin-bottom: 0.5rem;">No Results Available</h3>
            <p style="color: #64748b; max-width: 400px; margin: 0 auto 1.5rem;">
                Run the pipeline to generate matching results. Results will appear here once processing is complete.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_no_results1, col_no_results2 = st.columns(2)
        with col_no_results1:
            st.button("📥 Download Results (CSV)", disabled=True)
        with col_no_results2:
            if st.button("🔄 Refresh", key="refresh_no_results"):
                st.rerun()
        return
    
    st.markdown(f'<p class="sub-header">Cohort: <strong>{summary["cohort_name"]}</strong></p>', unsafe_allow_html=True)
    
    # Download button
    col1, col2 = st.columns([4, 1])
    with col2:
        csv_data = summary['dataframe'].to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"matching_results_{summary['cohort_name']}.csv",
            mime="text/csv"
        )
    
    # Stats cards
    st.markdown("---")
    cols = st.columns(4)
    
    metrics = [
        ("Total Patients", summary['total_patients'], "👥", "#3b82f6"),
        ("Matched", summary['matched_count'], "✓", "#22c55e"),
        ("Not Matched", summary['not_matched_count'], "✕", "#ef4444"),
        ("Match Rate", f"{summary['match_percentage']:.1f}%", "📊", "#3b82f6")
    ]
    
    for i, (label, value, icon, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <p style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">{label}</p>
                <p style="color: {color}; font-size: 2rem; font-weight: 700; margin: 0;">{value}</p>
                <span style="float: right; margin-top: -2.5rem; font-size: 1.5rem;">{icon}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Score distribution chart
    st.markdown("### 📊 Score Distribution")
    st.markdown("Distribution of matching scores across all patients")
    
    score_dist = summary['score_distribution']
    
    # Prepare chart data
    chart_data = []
    colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']  # 1-5 scores
    
    for score in range(1, 6):
        count = score_dist.get(str(score), 0)
        chart_data.append({
            'Score': f'Score {score}',
            'Count': count,
            'color': colors[score - 1]
        })
    
    df_chart = pd.DataFrame(chart_data)
    
    fig = px.bar(
        df_chart,
        x='Score',
        y='Count',
        color='Score',
        color_discrete_sequence=colors,
        title=''
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            title='Count'
        ),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    st.markdown("---")
    st.markdown("### 📋 Detailed Results")
    
    df = summary['dataframe']
    
    # Check which columns exist
    display_cols = ['patient_id', 'final_decision', 'overall_score']
    if 'primary_reasons' in df.columns:
        display_cols.append('primary_reasons')
    
    # Style the dataframe
    def color_decision(val):
        if val == 'MATCH':
            return 'background-color: #dcfce7; color: #166534;'
        else:
            return 'background-color: #fee2e2; color: #991b1b;'
    
    styled_df = df[display_cols].style.applymap(
        color_decision, subset=['final_decision']
    )
    
    st.dataframe(styled_df, use_container_width=True, height=400)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main application entry point."""
    
    # Sidebar navigation
    st.sidebar.title("🔬 Sigmatch")
    st.sidebar.markdown("---")
    
    pages = {
        "Setup / Paths": page_setup_paths,
        "Configure": page_configure,
        "Adjust Prompts": page_adjust_prompts,
        "Evaluation Criteria": page_evaluation_criteria,
        "Review Results": page_review_results,
        "Results Summary": page_results_summary
    }
    
    page_icons = {
        "Setup / Paths": "📁",
        "Configure": "⚙️",
        "Adjust Prompts": "🤖",
        "Evaluation Criteria": "📋",
        "Review Results": "✓",
        "Results Summary": "📊"
    }
    
    selection = st.sidebar.radio(
        "Navigation",
        options=list(pages.keys()),
        format_func=lambda x: f"{page_icons[x]} {x}",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Show current config info
    config = st.session_state.config
    if config:
        st.sidebar.markdown("### Current Config")
        st.sidebar.markdown(f"**Cohort:** {config.get('cohortName', 'Not set')}")
        trial_path = config.get('trial_file_config_path', '')
        trial_name = trial_path.split('/')[-1].replace('.json', '') if trial_path else 'Not set'
        st.sidebar.markdown(f"**Trial:** {trial_name}")
    
    # Show BASE_DIR in sidebar
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📂 Base: {BASE_DIR}")
    
    # Render selected page
    pages[selection]()


if __name__ == "__main__":
    main()
