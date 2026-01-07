"""
Sigmatch Streamlit App - Clinical Trial Matching Interface
Powered by Natera

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

# Pipeline script
PIPELINE_SCRIPT = BASE_DIR / "orchestrate_pipeline.py"

# Snapshots
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

# =============================================================================
# NATERA BRAND COLORS
# =============================================================================

NATERA_GREEN = "#8CC63F"
NATERA_BLUE = "#00AEEF"
NATERA_DARK_GREEN = "#6BA32E"
NATERA_DARK_BLUE = "#0091C9"
NATERA_LIGHT_GREEN = "#C5E1A5"
NATERA_LIGHT_BLUE = "#B3E5FC"

# Natera Logo (base64 encoded SVG for reliability)
NATERA_LOGO_URL = "https://www.natera.com/wp-content/uploads/2023/06/natera-logo.svg"

# =============================================================================
# STREAMLIT CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Sigmatch | Natera",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS STYLING - NATERA THEME
# =============================================================================

st.markdown(f"""
<style>
    /* Natera theme colors */
    :root {{
        --natera-green: {NATERA_GREEN};
        --natera-blue: {NATERA_BLUE};
        --natera-dark-green: {NATERA_DARK_GREEN};
        --natera-dark-blue: {NATERA_DARK_BLUE};
        --natera-light-green: {NATERA_LIGHT_GREEN};
        --natera-light-blue: {NATERA_LIGHT_BLUE};
    }}
    
    /* Primary button - Natera Green */
    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, {NATERA_GREEN} 0%, {NATERA_DARK_GREEN} 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(140, 198, 63, 0.3);
    }}
    .stButton>button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {NATERA_DARK_GREEN} 0%, {NATERA_GREEN} 100%);
        box-shadow: 0 4px 8px rgba(140, 198, 63, 0.4);
        transform: translateY(-1px);
    }}
    
    /* Secondary button - Natera Blue */
    .stButton>button {{
        background: linear-gradient(135deg, {NATERA_BLUE} 0%, {NATERA_DARK_BLUE} 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, {NATERA_DARK_BLUE} 0%, {NATERA_BLUE} 100%);
        transform: translateY(-1px);
    }}
    
    /* Success messages - Green theme */
    .stSuccess {{
        background-color: {NATERA_LIGHT_GREEN} !important;
        border-left: 4px solid {NATERA_GREEN} !important;
    }}
    
    /* Info messages - Blue theme */
    .stInfo {{
        background-color: {NATERA_LIGHT_BLUE} !important;
        border-left: 4px solid {NATERA_BLUE} !important;
    }}
    
    /* Patient ID badge - Natera Blue */
    .patient-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        background-color: {NATERA_LIGHT_BLUE};
        color: {NATERA_DARK_BLUE};
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
        border: 1px solid {NATERA_BLUE};
    }}
    
    /* Chat messages */
    .user-message {{
        background: linear-gradient(135deg, {NATERA_BLUE} 0%, {NATERA_DARK_BLUE} 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }}
    
    .assistant-message {{
        background: linear-gradient(135deg, {NATERA_LIGHT_GREEN} 0%, #E8F5E9 100%);
        color: #1B5E20;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }}
    
    /* Stat cards - Natera gradient */
    .stat-card {{
        background: linear-gradient(135deg, #ffffff 0%, {NATERA_LIGHT_BLUE} 100%);
        border-radius: 0.75rem;
        padding: 1.25rem;
        border: 1px solid {NATERA_BLUE}33;
        box-shadow: 0 2px 8px rgba(0, 174, 239, 0.1);
    }}
    
    /* Header styling with Natera colors */
    .main-header {{
        font-size: 1.75rem;
        font-weight: 600;
        background: linear-gradient(90deg, {NATERA_GREEN} 0%, {NATERA_BLUE} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}
    
    .sub-header {{
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    /* Results container */
    .results-container {{
        background: linear-gradient(135deg, #f8fafc 0%, {NATERA_LIGHT_BLUE}40 100%);
        border: 1px solid {NATERA_BLUE}33;
        border-radius: 0.5rem;
        padding: 1rem;
        min-height: 200px;
    }}
    
    /* Activity log styling */
    .activity-log {{
        background-color: #1a1a2e;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.75rem;
        max-height: 250px;
        overflow-y: auto;
        border: 1px solid {NATERA_BLUE}66;
    }}
    
    .log-entry {{
        padding: 0.25rem 0;
        border-bottom: 1px solid #333;
        color: #e0e0e0;
    }}
    
    .log-time {{
        color: {NATERA_GREEN};
        font-weight: 500;
    }}
    
    .log-action {{
        color: {NATERA_BLUE};
    }}
    
    .log-path {{
        color: #888;
        font-size: 0.7rem;
    }}
    
    /* Natera logo container */
    .natera-logo {{
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }}
    
    .natera-logo img {{
        max-width: 150px;
        height: auto;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Sidebar with Natera accent */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #ffffff 0%, {NATERA_LIGHT_BLUE}30 100%);
        border-right: 2px solid {NATERA_BLUE}33;
    }}
    
    /* Radio button styling */
    .stRadio > div {{
        gap: 0.25rem;
    }}
    
    /* Metric styling */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {NATERA_DARK_BLUE};
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {NATERA_LIGHT_BLUE}50;
        border-radius: 0.5rem 0.5rem 0 0;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {NATERA_BLUE} !important;
        color: white !important;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {NATERA_LIGHT_BLUE}30;
        border-radius: 0.5rem;
    }}
    
    /* Toast notification styling */
    .toast-notification {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, {NATERA_GREEN} 0%, {NATERA_DARK_GREEN} 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    }}
    
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ACTIVITY LOG & ACTION TRACKING FUNCTIONS
# =============================================================================

def init_session_state():
    """Initialize all session state variables."""
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    if 'operations_log' not in st.session_state:
        st.session_state.operations_log = []
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    if 'show_action_modal' not in st.session_state:
        st.session_state.show_action_modal = False

def log_operation(operation_type: str, description: str, file_path: str = "", 
                  code_executed: str = "", result: str = "success"):
    """Log a detailed operation for the Operations Console."""
    init_session_state()
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    entry = {
        "time": timestamp,
        "type": operation_type,  # READ, WRITE, DELETE, EXECUTE, LOAD, SAVE
        "description": description,
        "file_path": file_path,
        "code_executed": code_executed,
        "result": result,
        "full_timestamp": datetime.now().isoformat()
    }
    
    st.session_state.operations_log.insert(0, entry)
    # Keep last 100 operations
    st.session_state.operations_log = st.session_state.operations_log[:100]
    
    return entry

def set_last_action(action_name: str, description: str, details: Dict[str, Any]):
    """Set the last action for modal display."""
    init_session_state()
    st.session_state.last_action = {
        "name": action_name,
        "description": description,
        "details": details,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.show_action_modal = True

def log_activity(action: str, details: str = "", path: str = ""):
    """Add an entry to the activity log (legacy support)."""
    init_session_state()
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = {
        "time": timestamp,
        "action": action,
        "details": details,
        "path": path
    }
    st.session_state.activity_log.insert(0, entry)
    st.session_state.activity_log = st.session_state.activity_log[:50]

def show_toast(message: str, icon: str = "✓"):
    """Show a toast notification."""
    st.toast(f"{icon} {message}")

def render_action_modal():
    """Render a modal showing the last action's details."""
    init_session_state()
    
    if st.session_state.show_action_modal and st.session_state.last_action:
        action = st.session_state.last_action
        
        # Create a prominent action feedback box using native components
        col1, col2, col3 = st.columns([1, 10, 1])
        with col2:
            st.info(f"🔔 **{action['name']}** [{action['timestamp']}]\n\n{action['description']}")
            
            # Show details in an expander
            with st.expander("📋 View Backend Details (What happened?)", expanded=True):
                details = action['details']
                
                if details.get('files_affected'):
                    st.markdown("**📁 Files Affected:**")
                    for f in details['files_affected']:
                        # Show short path
                        short_f = "/".join(f.split("/")[-3:]) if "/" in f else f
                        st.code(short_f, language="text")
                
                if details.get('code_executed'):
                    st.markdown("**💻 Code/Command Executed:**")
                    st.code(details['code_executed'], language="python")
                
                if details.get('data_loaded'):
                    st.markdown("**📥 Data Loaded:**")
                    st.json(details['data_loaded'])
                
                if details.get('data_saved'):
                    st.markdown("**💾 Data Saved:**")
                    st.json(details['data_saved'])
                
                if details.get('result'):
                    st.success(f"**Result:** {details['result']}")
            
            # Button to dismiss
            if st.button("✕ Dismiss Notification", key="dismiss_modal", use_container_width=True):
                st.session_state.show_action_modal = False
                st.rerun()
        
        st.markdown("---")

def render_operations_console():
    """Render the scrollable Operations Console in the sidebar."""
    init_session_state()
    
    st.sidebar.markdown("### 🖥️ Operations Console")
    st.sidebar.caption("Real-time file operations log")
    
    type_icons = {
        "READ": "📖",
        "WRITE": "✍️",
        "SAVE": "💾",
        "LOAD": "📥",
        "DELETE": "🗑️",
        "EXECUTE": "▶️",
        "CREATE": "📁",
        "ERROR": "❌",
        "SELECT": "👆",
    }
    
    # Create scrollable container using expander with text
    if not st.session_state.operations_log:
        st.sidebar.text("$ Waiting for operations...")
        st.sidebar.text("$ Actions will appear here")
    else:
        # Show operations in a scrollable text area style
        with st.sidebar.container(height=200):
            for entry in st.session_state.operations_log[:20]:
                icon = type_icons.get(entry['type'], "📝")
                time_str = entry['time']
                op_type = entry['type']
                desc = entry['description'][:35] + "..." if len(entry['description']) > 35 else entry['description']
                file_path = entry.get('file_path', '')
                
                # Format the entry
                st.text(f"[{time_str}] {icon} {op_type}")
                st.caption(f"   {desc}")
                if file_path:
                    short_path = file_path.split('/')[-1] if '/' in file_path else file_path
                    st.caption(f"   → {short_path}")
                st.markdown("---")
    
    # Clear console button
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear", key="clear_console", use_container_width=True):
            st.session_state.operations_log = []
            st.rerun()
    with col2:
        if st.button("📋 Export", key="copy_console", use_container_width=True):
            # Show copyable text version in expander
            with st.sidebar.expander("📋 Copy Log", expanded=True):
                log_text = "\n".join([
                    f"[{e['time']}] {e['type']}: {e['description']} → {e.get('file_path', '').split('/')[-1] if e.get('file_path') else ''}"
                    for e in st.session_state.operations_log[:30]
                ])
                st.code(log_text, language="text")

def render_activity_log():
    """Render the activity summary in the sidebar."""
    init_session_state()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Session Summary")
    
    # Count operations by type
    if st.session_state.operations_log:
        reads = sum(1 for e in st.session_state.operations_log if e['type'] in ['READ', 'LOAD'])
        writes = sum(1 for e in st.session_state.operations_log if e['type'] in ['WRITE', 'SAVE', 'CREATE'])
        executes = sum(1 for e in st.session_state.operations_log if e['type'] == 'EXECUTE')
        
        col1, col2, col3 = st.sidebar.columns(3)
        col1.metric("📥 Loads", reads)
        col2.metric("💾 Saves", writes)
        col3.metric("▶️ Runs", executes)
    else:
        st.sidebar.caption("No operations recorded yet.")

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

def load_json(relative_path: str, log_op: bool = False) -> Optional[Dict[str, Any]]:
    """Load JSON file from path relative to BASE_DIR."""
    try:
        full_path = BASE_DIR / relative_path
        if not full_path.exists():
            return None
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        if log_op:
            log_operation("READ", f"Loaded JSON: {relative_path.split('/')[-1]}", str(full_path),
                         code_executed=f"json.load('{relative_path}')")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_operation("ERROR", f"Failed to load: {e}", relative_path, result="error")
        return None

def save_json(relative_path: str, data: Dict[str, Any], log_action: bool = True) -> bool:
    """Save JSON file to path relative to BASE_DIR."""
    try:
        full_path = BASE_DIR / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        if log_action:
            log_operation("SAVE", f"Saved JSON: {relative_path.split('/')[-1]}", str(full_path),
                         code_executed=f"json.dump(data, '{relative_path}')")
            log_activity("FILE SAVED", f"Saved JSON data", relative_path)
            show_toast(f"Saved: {relative_path.split('/')[-1]}")
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        log_operation("ERROR", f"Failed to save: {e}", relative_path, result="error")
        log_activity("ERROR", f"Failed to save: {e}", relative_path)
        return False

def get_trials(log_op: bool = False) -> List[Dict[str, str]]:
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

def get_cohorts(log_op: bool = False) -> List[Dict[str, Any]]:
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
    matching_dir = BASE_DIR / config["matching_result_dir"]
    llm_dir = BASE_DIR / config["llm_summarization_result_dir"]
    matching_dir.mkdir(parents=True, exist_ok=True)
    llm_dir.mkdir(parents=True, exist_ok=True)
    
    log_operation("CREATE", f"Created directory: {config['matching_result_dir']}", str(matching_dir))
    log_operation("CREATE", f"Created directory: {config['llm_summarization_result_dir']}", str(llm_dir))
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"data_config_{cohort_name}__{timestamp}.json"
    backup_path = f"config_files/overall_config_settings/{backup_filename}"
    
    log_operation("SAVE", f"Saving config backup: {backup_filename}", str(BASE_DIR / backup_path),
                 code_executed=f"json.dump(config, '{backup_path}')")
    save_json(backup_path, config, log_action=False)
    
    # Save as active config
    active_path = "config_files/overall_config_settings/active_data_config.json"
    log_operation("SAVE", f"Saving active config", str(BASE_DIR / active_path),
                 code_executed=f"json.dump(config, '{active_path}')")
    
    # Log the activity
    log_activity("CONFIG SAVED", f"Cohort: {cohort_name}", backup_path)
    show_toast(f"Config saved for cohort: {cohort_name}", "💾")
    
    # Set action modal
    set_last_action(
        "💾 Configuration Saved",
        f"Saved configuration for cohort: {cohort_name}",
        {
            "files_affected": [
                str(BASE_DIR / backup_path),
                str(BASE_DIR / active_path),
                str(matching_dir),
                str(llm_dir)
            ],
            "code_executed": f"""
# Auto-generated paths for cohort: {cohort_name}
config["pdf_data_dir"] = "{config['pdf_data_dir']}"
config["ocr_data_dir"] = "{config['ocr_data_dir']}"
config["matching_result_dir"] = "{config['matching_result_dir']}"
config["llm_summarization_result_dir"] = "{config['llm_summarization_result_dir']}"

# Created directories
os.makedirs("{matching_dir}", exist_ok=True)
os.makedirs("{llm_dir}", exist_ok=True)

# Saved files
json.dump(config, "{backup_path}")
json.dump(config, "{active_path}")
""",
            "data_saved": {
                "cohortName": cohort_name,
                "trial_file_config_path": config.get("trial_file_config_path"),
                "patients_file_path": config.get("patients_file_path")
            },
            "result": f"Backup: {backup_filename}"
        }
    )
    
    return save_json(active_path, config, log_action=False)

def assemble_cohort(criteria_list: List[str], cohort_source: str, max_patients: int) -> Dict[str, Any]:
    """Assemble a cohort based on search criteria."""
    try:
        cohort_path = COHORT_FILES_DIR / cohort_source
        
        log_operation("READ", f"Loading cohort: {cohort_source}", str(cohort_path),
                     code_executed=f"open('{cohort_path}', 'r')")
        
        if not cohort_path.exists():
            log_operation("ERROR", f"Cohort file not found", str(cohort_path), result="not_found")
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
        
        log_operation("EXECUTE", f"Keyword search: {len(matched)} matches", str(cohort_path),
                     code_executed=f"search_criteria={criteria_list}, max={max_patients}")
        
        log_activity("COHORT ASSEMBLED", f"Found {len(matched)} patients from {cohort_source}")
        show_toast(f"Found {len(matched)} matching patients", "🔍")
        
        # Set action modal
        set_last_action(
            "🔍 Patient Search",
            f"Searched {len(cohort)} patients, found {len(matched)} matches",
            {
                "files_affected": [str(cohort_path)],
                "code_executed": f"""
# Load cohort data
with open('{cohort_path}', 'r') as f:
    cohort = json.load(f)

# Search criteria: {criteria_list}
# Max patients: {max_patients}
# Total in cohort: {len(cohort)}
# Matched: {len(matched)}
""",
                "data_loaded": {"patient_count": len(cohort), "criteria": criteria_list},
                "result": f"Found {len(matched)} patients: {matched}"
            }
        )
        
        return {
            "matched_count": len(matched),
            "patient_ids_list": matched
        }
    except Exception as e:
        st.error(f"Error assembling cohort: {e}")
        log_operation("ERROR", f"Cohort assembly failed: {e}", result="error")
        log_activity("ERROR", f"Cohort assembly failed: {e}")
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
    
    config_path = "config_files/overall_config_settings/active_data_config.json"
    
    log_operation("EXECUTE", "Starting pipeline execution", str(PIPELINE_SCRIPT),
                 code_executed=f"OCR={run_ocr}, LLM={do_llm_summarization}, Match={do_patient_matching}, Eval={do_evaluation}")
    log_activity("PIPELINE STARTED", f"OCR={run_ocr}, LLM={do_llm_summarization}, Match={do_patient_matching}, Eval={do_evaluation}")
    
    # Check if pipeline script exists
    if not PIPELINE_SCRIPT.exists():
        log_operation("ERROR", "Pipeline script not found", str(PIPELINE_SCRIPT), result="not_found")
        log_activity("ERROR", "Pipeline script not found", str(PIPELINE_SCRIPT))
        
        set_last_action(
            "❌ Pipeline Error",
            f"Pipeline script not found",
            {
                "files_affected": [str(PIPELINE_SCRIPT)],
                "code_executed": f"os.path.exists('{PIPELINE_SCRIPT}')  # Returns False",
                "result": f"Script should be at: {PIPELINE_SCRIPT}"
            }
        )
        
        return {
            "error": f"Pipeline script not found at:\n{PIPELINE_SCRIPT}\n\n"
                     f"orchestrate_pipeline.py should be in the sigmatch root folder:\n{BASE_DIR}",
            "hint": "Make sure orchestrate_pipeline.py is in the correct location",
            "success": False
        }
    
    # Build command
    cmd = [
        sys.executable,
        str(PIPELINE_SCRIPT),
        "--data_config_json", config_path,
        "--run_ocr", str(run_ocr),
        "--do_llm_summarization", str(do_llm_summarization),
        "--do_patient_matching", str(do_patient_matching),
        "--do_evaluation", str(do_evaluation)
    ]
    
    cmd_str = " ".join(cmd)
    log_operation("EXECUTE", "Running pipeline command", str(BASE_DIR), code_executed=cmd_str)
    
    try:
        env = os.environ.copy()
        
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=3600,
            env=env
        )
        
        if result.returncode == 0:
            log_operation("EXECUTE", "Pipeline completed successfully", "results_dir/matching/", result="success")
            log_activity("PIPELINE COMPLETED", "Success!", "results_dir/matching/")
            
            set_last_action(
                "✅ Pipeline Completed",
                "Pipeline executed successfully",
                {
                    "files_affected": [
                        str(PIPELINE_SCRIPT),
                        str(BASE_DIR / config_path),
                        "results_dir/matching/*/matching_results.csv"
                    ],
                    "code_executed": cmd_str,
                    "result": "Pipeline completed with exit code 0"
                }
            )
        else:
            log_operation("ERROR", f"Pipeline failed: exit code {result.returncode}", result="error")
            log_activity("PIPELINE FAILED", f"Exit code: {result.returncode}")
            
            set_last_action(
                "❌ Pipeline Failed",
                f"Pipeline exited with code {result.returncode}",
                {
                    "code_executed": cmd_str,
                    "result": f"Exit code: {result.returncode}\nStderr: {result.stderr[:500] if result.stderr else 'None'}"
                }
            )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": cmd_str
        }
        
    except subprocess.TimeoutExpired:
        log_operation("ERROR", "Pipeline timed out after 1 hour", result="timeout")
        log_activity("ERROR", "Pipeline timed out after 1 hour")
        return {
            "error": "Pipeline timed out after 1 hour. The process may still be running.",
            "success": False
        }
    except Exception as e:
        log_operation("ERROR", f"Pipeline error: {str(e)}", result="error")
        log_activity("ERROR", f"Pipeline error: {str(e)}")
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
        log_operation("CREATE", f"Created snapshot directory", str(snapshot_dir))
        
        if CONFIG_DIR.exists():
            shutil.copytree(CONFIG_DIR, snapshot_dir / "config_files")
            log_operation("SAVE", f"Copied config_files to snapshot", str(snapshot_dir / "config_files"),
                         code_executed=f"shutil.copytree('{CONFIG_DIR}', '{snapshot_dir}/config_files')")
        
        log_activity("SNAPSHOT SAVED", f"snapshot_{timestamp}", str(snapshot_dir))
        show_toast(f"Snapshot saved: {timestamp}", "📸")
        
        # Set action modal
        set_last_action(
            "📸 Snapshot Created",
            f"Saved snapshot of all configuration files",
            {
                "files_affected": [
                    str(snapshot_dir),
                    str(snapshot_dir / "config_files")
                ],
                "code_executed": f"""
# Create snapshot directory
os.makedirs("{snapshot_dir}", exist_ok=True)

# Copy all config files
shutil.copytree("{CONFIG_DIR}", "{snapshot_dir}/config_files")
""",
                "result": f"Snapshot saved to: {snapshot_dir}"
            }
        )
        
        return str(snapshot_dir)
    except Exception as e:
        log_operation("ERROR", f"Snapshot failed: {e}", result="error")
        log_activity("ERROR", f"Snapshot failed: {e}")
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
    backup_path = f"config_files/prompt_settings/sigmatch_standard_prompt_content_{timestamp}.json"
    active_path = "config_files/prompt_settings/sigmatch_standard_prompt_content.json"
    
    log_operation("SAVE", f"Saving prompts backup", str(BASE_DIR / backup_path))
    save_json(backup_path, prompts, log_action=False)
    
    log_operation("SAVE", f"Saving active prompts", str(BASE_DIR / active_path))
    
    # Log activity
    log_activity("PROMPTS SAVED", f"Backup: {timestamp}", backup_path)
    show_toast("Prompts saved successfully", "🤖")
    
    # Set action modal
    agent_names = list(prompts.keys())
    set_last_action(
        "🤖 Prompts Saved",
        f"Saved prompts for {len(agent_names)} agents",
        {
            "files_affected": [
                str(BASE_DIR / backup_path),
                str(BASE_DIR / active_path)
            ],
            "code_executed": f"""
# Agents updated: {agent_names}
# Backup: {backup_path}
json.dump(prompts, "{active_path}")
""",
            "data_saved": {"agents": agent_names},
            "result": f"Saved {len(agent_names)} agent prompts"
        }
    )
    
    # Save as current
    return save_json(active_path, prompts, log_action=False)

def get_results_summary() -> Dict[str, Any]:
    """Get summary of matching results."""
    config = get_active_config()
    cohort_name = config.get("cohortName", "unknown")
    matching_result_dir = config.get("matching_result_dir", "")
    
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

# Initialize all session state
init_session_state()

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

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Configure"

# =============================================================================
# PAGE FUNCTIONS
# =============================================================================

def page_setup_paths():
    """Setup & Paths page - Verify file structure."""
    st.markdown('<p class="main-header">📁 Setup & File Paths</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Verify your file structure and paths</p>', unsafe_allow_html=True)
    
    log_activity("PAGE VIEW", "Setup / Paths")
    
    paths = get_paths_info()
    
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
        log_activity("REFRESH", "Status check refreshed")
        st.rerun()


def page_configure():
    """Configure Pipeline page - Main configuration interface."""
    st.markdown('<p class="main-header">⚙️ Configure Pipeline</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Set up your clinical trial matching parameters</p>', unsafe_allow_html=True)
    
    config = st.session_state.config
    trials = get_trials()
    cohorts = get_cohorts()
    
    # ASSEMBLE COHORT SECTION
    st.markdown("### 👥 Assemble Cohort")
    st.markdown("Define criteria to identify matching patients from a cohort source")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Patient Criteria**")
        
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
                        log_activity("CRITERION REMOVED", f"Removed criterion {i+1}")
                        st.rerun()
        
        if st.button("➕ Add Criterion"):
            st.session_state.criteria_list.append('')
            log_activity("CRITERION ADDED", f"Total: {len(st.session_state.criteria_list)}")
            st.rerun()
        
        st.markdown("---")
        
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
    
    # TRIAL AND COHORT SELECTION
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Trial Selection")
        st.markdown("Choose or upload a clinical trial")
        
        if not trials:
            st.warning("No trial files found. Add trial JSON files to config_files/trial_files/")
            selected_trial = None
        else:
            trial_options = {t['filename']: t['title'] for t in trials}
            current_trial = config.get('trial_file_config_path', '').split('/')[-1] if config.get('trial_file_config_path') else None
            
            selected_trial = st.selectbox(
                "Select Trial",
                options=list(trial_options.keys()),
                format_func=lambda x: trial_options.get(x, x),
                index=list(trial_options.keys()).index(current_trial) if current_trial in trial_options else 0,
                key="selected_trial",
                on_change=lambda: log_operation("SELECT", f"Selected trial: {st.session_state.selected_trial}", 
                                                str(TRIAL_FILES_DIR / st.session_state.selected_trial))
            )
        
        uploaded_file = st.file_uploader("Upload Trial JSON", type=['json'], key="trial_upload")
        if uploaded_file:
            try:
                trial_data = json.load(uploaded_file)
                filename = uploaded_file.name
                save_json(f"config_files/trial_files/{filename}", trial_data)
                st.rerun()
            except Exception as e:
                st.error(f"Error uploading file: {e}")
        
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
                        st.rerun()
                else:
                    st.warning("Please fill in both title and description.")
    
    with col2:
        st.markdown("### 📊 Cohort Selection")
        st.markdown("Select patient cohort for matching")
        
        cohort_names = [c['name'] for c in cohorts]
        
        if not cohort_names:
            st.warning("No cohort files found. Add cohort JSON files to config_files/pipeline_json_files/")
            cohort_type = 'custom'
        else:
            cohort_type = st.radio(
                "Choose cohort",
                options=cohort_names + ['custom'],
                key="cohort_type",
                on_change=lambda: log_operation("SELECT", f"Selected cohort: {st.session_state.cohort_type}",
                                                str(COHORT_FILES_DIR / f"{st.session_state.cohort_type}.json") 
                                                if st.session_state.cohort_type != 'custom' else "")
            )
        
        custom_path = ""
        if cohort_type == 'custom':
            custom_path = st.text_input(
                "Custom Path",
                placeholder="config_files/pipeline_json_files/...",
                key="custom_cohort_path"
            )
        
        cohort_name = st.text_input(
            "Cohort Name",
            value=config.get('cohortName', ''),
            key="cohort_name"
        )
    
    st.divider()
    
    # PIPELINE STEPS AND ACTIONS
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
        
        run_pipeline_btn = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)
        
        if run_pipeline_btn:
            updated_config = {
                **config,
                "cohortName": cohort_name,
                "trial_file_config_path": f"config_files/trial_files/{selected_trial}" if selected_trial else "",
                "patients_file_path": f"config_files/pipeline_json_files/{cohort_type}.json" if cohort_type != 'custom' else custom_path,
            }
            
            save_active_config(updated_config)
            st.session_state.config = updated_config
            
            # Show modal for pipeline execution
            st.info("🔄 **Pipeline Starting...**")
            st.markdown(f"""
            **Configuration:**
            - Trial: `{selected_trial}`
            - Cohort: `{cohort_name}`
            - Steps: OCR={run_ocr}, LLM={do_llm_summarization}, Match={do_patient_matching}, Eval={do_evaluation}
            """)
            
            with st.spinner("🔄 Running pipeline... This may take several minutes."):
                result = run_pipeline(
                    run_ocr=run_ocr,
                    do_llm_summarization=do_llm_summarization,
                    do_patient_matching=do_patient_matching,
                    do_evaluation=do_evaluation
                )
                st.session_state.pipeline_result = result
            
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
        
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            
            if result.get("stdout"):
                with st.expander("📄 View Pipeline Output", expanded=not result.get("success", False)):
                    st.code(result.get("stdout", ""), language="text")
            
            if result.get("stderr"):
                with st.expander("⚠️ View Warnings/Errors"):
                    st.code(result.get("stderr", ""), language="text")
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📸 Save Snapshot", use_container_width=True):
                log_operation("SAVE", "Creating snapshot of config files", str(SNAPSHOTS_DIR))
                try:
                    snapshot_path = save_snapshot()
                    st.success(f"Snapshot saved!")
                    st.rerun()
                except Exception as e:
                    log_operation("ERROR", f"Snapshot failed: {e}", result="error")
                    st.error(str(e))
        
        with col_b:
            if st.button("💾 Save Config", use_container_width=True):
                # Log the action first
                log_operation("SAVE", f"Saving config for cohort: {cohort_name}", 
                             str(OVERALL_CONFIG))
                
                updated_config = {
                    **config,
                    "cohortName": cohort_name,
                    "trial_file_config_path": f"config_files/trial_files/{selected_trial}" if selected_trial else "",
                    "patients_file_path": f"config_files/pipeline_json_files/{cohort_type}.json" if cohort_type != 'custom' else custom_path,
                }
                
                if save_active_config(updated_config):
                    st.session_state.config = updated_config
                    log_operation("SAVE", "Config saved successfully", str(OVERALL_CONFIG))
                    st.success("Configuration saved!")
                    st.rerun()  # Force rerun to update console
        
        with st.expander("🔧 View Pipeline Command (for debugging)"):
            cmd_str = generate_pipeline_command(
                run_ocr, do_llm_summarization, do_patient_matching, do_evaluation
            )
            st.code(cmd_str, language="bash")
            st.caption("Copy this command to run the pipeline manually in a terminal.")


def page_adjust_prompts():
    """Adjust Prompts page - Configure AI agent prompts."""
    st.markdown('<p class="main-header">🤖 Adjust Prompts</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure AI agent system and main prompts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("💾 Save All Prompts", type="primary"):
            if save_prompts(st.session_state.prompts):
                st.success("All prompts saved successfully!")
    
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
    
    if prompts:
        tabs = st.tabs([agent_labels.get(name, name) for name in prompts.keys()])
        
        for i, (agent_name, prompt_data) in enumerate(prompts.items()):
            with tabs[i]:
                skip_val = prompt_data.get('skip', False)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{agent_labels.get(agent_name, agent_name)}**")
                with col2:
                    new_skip = st.checkbox("Skip", value=skip_val, key=f"skip_{agent_name}")
                    if new_skip != skip_val:
                        st.session_state.prompts[agent_name]['skip'] = new_skip
                        log_activity("AGENT TOGGLED", f"{agent_name}: skip={new_skip}")
                
                if skip_val:
                    st.info("This agent is currently skipped in the pipeline.")
                
                st.markdown("**System Prompt**")
                system_prompt = st.text_area(
                    "System Prompt",
                    value=prompt_data.get('system_prompt', ''),
                    height=150,
                    key=f"sys_{agent_name}",
                    label_visibility="collapsed"
                )
                
                st.markdown("**Main Prompt**")
                main_prompt = st.text_area(
                    "Main Prompt",
                    value=prompt_data.get('main_prompt', ''),
                    height=200,
                    key=f"main_{agent_name}",
                    label_visibility="collapsed"
                )
                
                if st.button(f"💾 Save {agent_labels.get(agent_name, agent_name)}", key=f"save_{agent_name}"):
                    st.session_state.prompts[agent_name]['system_prompt'] = system_prompt
                    st.session_state.prompts[agent_name]['main_prompt'] = main_prompt
                    if save_prompts(st.session_state.prompts):
                        st.success(f"{agent_labels.get(agent_name, agent_name)} saved!")
    else:
        st.warning("No prompts found. Check your prompt settings file at config_files/prompt_settings/")


def page_evaluation_criteria():
    """Evaluation Criteria page - Chat interface for criteria configuration."""
    st.markdown('<p class="main-header">📋 Evaluation Criteria</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure criteria through conversation</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Chat")
        st.markdown("Discuss and refine evaluation criteria")
        
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
        
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input("Type your message...", key="chat_input", 
                                       label_visibility="collapsed", 
                                       placeholder="Type your message...")
        with col_btn:
            send_clicked = st.button("➤", key="send_btn")
        
        if send_clicked and user_input:
            st.session_state.chat_messages.append({
                'role': 'user',
                'content': user_input
            })
            
            response = f'I received your message: "{user_input}". How can I help you refine the evaluation criteria?'
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': response
            })
            
            log_activity("CHAT MESSAGE", f"User: {user_input[:30]}...")
            
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
    st.markdown('<p class="main-header">✓ Manual Review Results</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Review and approve/reject patient matches</p>', unsafe_allow_html=True)
    
    st.markdown("### 📋 Patient Matches")
    
    st.markdown(f"""
    <div style="border: 2px dashed {NATERA_BLUE}66; border-radius: 0.5rem; padding: 2rem; text-align: center; margin: 1rem 0; background: linear-gradient(135deg, {NATERA_LIGHT_BLUE}30 0%, {NATERA_LIGHT_GREEN}30 100%);">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🕐</p>
        <h3 style="margin-bottom: 0.5rem; color: {NATERA_DARK_BLUE};">Feature In Development</h3>
        <p style="color: #64748b;">
            The manual review functionality is currently being developed. 
            Below is a preview of how it will look.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    dummy_patients = [
        {"id": "PT-001", "decision": "Matched", "score": 4.2, "status": "pending"},
        {"id": "PT-002", "decision": "Not Matched", "score": 2.1, "status": "pending"},
        {"id": "PT-003", "decision": "Matched", "score": 4.8, "status": "approved"},
        {"id": "PT-004", "decision": "Matched", "score": 3.5, "status": "rejected"},
    ]
    
    st.markdown("---")
    
    cols = st.columns([1, 1.5, 1, 1, 2])
    cols[0].markdown("**Patient ID**")
    cols[1].markdown("**Decision**")
    cols[2].markdown("**Score**")
    cols[3].markdown("**Status**")
    cols[4].markdown("**Actions**")
    
    st.markdown("---")
    
    for patient in dummy_patients:
        cols = st.columns([1, 1.5, 1, 1, 2])
        
        cols[0].write(patient['id'])
        
        if patient['decision'] == 'Matched':
            cols[1].markdown(f'<span style="background-color: {NATERA_GREEN}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["decision"]}</span>', unsafe_allow_html=True)
        else:
            cols[1].markdown(f'<span style="background-color: #64748b; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["decision"]}</span>', unsafe_allow_html=True)
        
        cols[2].write(f"{patient['score']:.1f}")
        
        status_colors = {
            'pending': '#f59e0b',
            'approved': NATERA_GREEN,
            'rejected': '#ef4444'
        }
        cols[3].markdown(f'<span style="border: 1px solid {status_colors[patient["status"]]}; color: {status_colors[patient["status"]]}; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">{patient["status"]}</span>', unsafe_allow_html=True)
        
        with cols[4]:
            btn_cols = st.columns(2)
            btn_cols[0].button("✓ Approve", key=f"approve_{patient['id']}", disabled=True)
            btn_cols[1].button("✕ Reject", key=f"reject_{patient['id']}", disabled=True)


def page_results_summary():
    """Results Summary page - Display matching results and statistics."""
    st.markdown('<p class="main-header">📊 Results Summary</p>', unsafe_allow_html=True)
    
    col_header1, col_header2 = st.columns([4, 1])
    with col_header2:
        if st.button("🔄 Refresh Results"):
            log_activity("REFRESH", "Results refreshed")
            st.rerun()
    
    summary = get_results_summary()
    
    if not summary.get('has_results'):
        st.markdown('<p class="sub-header">View matching results and statistics</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 4rem 2rem; border: 1px solid {NATERA_BLUE}33; border-radius: 0.75rem; margin: 2rem 0; background: linear-gradient(135deg, {NATERA_LIGHT_BLUE}30 0%, {NATERA_LIGHT_GREEN}30 100%);">
            <p style="font-size: 4rem; margin-bottom: 1rem;">⚠️</p>
            <h3 style="margin-bottom: 0.5rem; color: {NATERA_DARK_BLUE};">No Results Available</h3>
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
    
    col1, col2 = st.columns([4, 1])
    with col2:
        csv_data = summary['dataframe'].to_csv(index=False)
        if st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"matching_results_{summary['cohort_name']}.csv",
            mime="text/csv"
        ):
            log_activity("DOWNLOAD", f"Results CSV for {summary['cohort_name']}")
    
    st.markdown("---")
    cols = st.columns(4)
    
    metrics = [
        ("Total Patients", summary['total_patients'], "👥", NATERA_BLUE),
        ("Matched", summary['matched_count'], "✓", NATERA_GREEN),
        ("Not Matched", summary['not_matched_count'], "✕", "#ef4444"),
        ("Match Rate", f"{summary['match_percentage']:.1f}%", "📊", NATERA_BLUE)
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
    
    st.markdown("### 📊 Score Distribution")
    st.markdown("Distribution of matching scores across all patients")
    
    score_dist = summary['score_distribution']
    
    chart_data = []
    colors = ['#ef4444', '#f97316', '#eab308', NATERA_GREEN, NATERA_BLUE]
    
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
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Count'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Detailed Results")
    
    df = summary['dataframe']
    
    display_cols = ['patient_id', 'final_decision', 'overall_score']
    if 'primary_reasons' in df.columns:
        display_cols.append('primary_reasons')
    
    def color_decision(val):
        if val == 'MATCH':
            return f'background-color: {NATERA_LIGHT_GREEN}; color: #166534;'
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
    
    # Natera Logo in sidebar
    st.sidebar.markdown(f"""
    <div class="natera-logo">
        <img src="{NATERA_LOGO_URL}" alt="Natera" onerror="this.style.display='none'">
        <h2 style="background: linear-gradient(90deg, {NATERA_GREEN} 0%, {NATERA_BLUE} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0.5rem 0;">Sigmatch</h2>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Get current page from session state or default
    current_page = st.session_state.get('current_page', 'Configure')
    
    selection = st.sidebar.radio(
        "Navigation",
        options=list(pages.keys()),
        index=list(pages.keys()).index(current_page) if current_page in pages else 1,
        format_func=lambda x: f"{page_icons[x]} {x}",
        label_visibility="collapsed",
        key="page_selector"
    )
    
    # Log page navigation if changed
    if selection != st.session_state.get('current_page'):
        st.session_state.current_page = selection
        log_operation("SELECT", f"Navigated to: {selection}", "", 
                     code_executed=f"page = '{selection}'")
    
    st.sidebar.markdown("---")
    
    # Current config info
    config = st.session_state.config
    if config:
        st.sidebar.markdown("### 📌 Current Config")
        st.sidebar.markdown(f"**Cohort:** {config.get('cohortName', 'Not set')}")
        trial_path = config.get('trial_file_config_path', '')
        trial_name = trial_path.split('/')[-1].replace('.json', '') if trial_path else 'Not set'
        st.sidebar.markdown(f"**Trial:** {trial_name}")
    
    st.sidebar.markdown("---")
    
    # Operations Console (scrollable terminal)
    render_operations_console()
    
    # Activity Summary
    render_activity_log()
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📂 Base: {BASE_DIR}")
    
    # Render action modal in main area if there's a recent action
    render_action_modal()
    
    # Render selected page
    pages[selection]()


if __name__ == "__main__":
    main()
