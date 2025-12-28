"""
Configuration manager service for Sigmatch.
Handles active config management, versioning, and path generation.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from app.services import file_ops


# Default paths
ACTIVE_CONFIG_PATH = "config_files/overall_config_settings/active_data_config.json"
PROMPT_SETTINGS_PATH = "config_files/prompt_settings/sigmatch_standard_prompt_content.json"
EVALUATION_CRITERIA_PATH = "config_files/overall_config_settings/evaluation_criteria.json"


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration template."""
    return {
        "cohortName": "dummy_cohort1",
        "patients_file_path": "config_files/pipeline_json_files/dummy_cohort1.json",
        "pdf_data_dir": "documents/pdfs/dummy_cohort1",
        "ocr_data_dir": "documents/ocr/dummy_cohort1",
        "llm_summarization_result_dir": "results_dir/llm_summarization/dummy_cohort1",
        "matching_result_dir": "results_dir/matching/dummy_cohort1",
        "trial_file_config_path": "config_files/trial_files/pcv_trial.json",
        "pdf_info_path": "config_files/other_config_files/Circulate_pdf_data_pull.csv",
        "signatera_df_path": "config_files/other_config_files/All_Bladder_Cancer_Signatera.csv",
        "signatera_filter_patients": "config_files/other_config_files/bladder_signatera_positive_with_6m.txt",
        "llm_argument_json": "config_files/",
        "extracted_features_path": "results_dir/llm_summarization/dummy_cohort1/patient_feature_summaries_dummy_cohort1.csv",
        "evaluation_results_path": "results_dir/evaluation/matching_results_summary_dummy_cohort1.xlsx"
    }


def get_active_config() -> Dict[str, Any]:
    """
    Get the current active configuration.
    Creates default config if it doesn't exist.
    
    Returns:
        Active configuration dictionary
    """
    if not file_ops.file_exists(ACTIVE_CONFIG_PATH):
        # Create default config
        default_config = get_default_config()
        file_ops.write_json(ACTIVE_CONFIG_PATH, default_config)
        return default_config
    
    return file_ops.read_json(ACTIVE_CONFIG_PATH)


def get_active_config_modified_time() -> str:
    """Get the last modified time of the active config."""
    modified = file_ops.get_file_modified_time(ACTIVE_CONFIG_PATH)
    if modified is None:
        return datetime.now().isoformat()
    return modified


def auto_generate_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-generate paths based on cohortName.
    ALWAYS overrides paths to ensure they match the cohortName.
    If cohortName is empty, extracts it from patients_file_path.
    
    Args:
        config: Configuration dictionary with at least cohortName or patients_file_path
        
    Returns:
        Updated configuration with generated paths
    """
    cohort_name = config.get("cohortName", "").strip()
    
    # If cohortName is empty, try to extract from patients_file_path
    if not cohort_name:
        patients_path = config.get("patients_file_path", "")
        if patients_path:
            # Extract filename from path like "config_files/pipeline_json_files/dummy_cohort1.json"
            filename = patients_path.split("/")[-1]  # "dummy_cohort1.json"
            cohort_name = filename.replace(".json", "")  # "dummy_cohort1"
            print(f"INFO: Extracted cohort name '{cohort_name}' from patients_file_path")
    
    # Default fallback
    if not cohort_name:
        cohort_name = "dummy_cohort1"
        print(f"WARN: No cohortName found, using default: {cohort_name}")
    
    # Set the cohortName in config
    config["cohortName"] = cohort_name
    
    # ALWAYS generate paths based on cohortName (override existing values)
    config["pdf_data_dir"] = f"documents/pdfs/{cohort_name}"
    config["ocr_data_dir"] = f"documents/ocr/{cohort_name}"
    config["llm_summarization_result_dir"] = f"results_dir/llm_summarization/{cohort_name}"
    config["matching_result_dir"] = f"results_dir/matching/{cohort_name}"
    config["extracted_features_path"] = f"results_dir/llm_summarization/{cohort_name}/patient_feature_summaries_{cohort_name}.csv"
    config["evaluation_results_path"] = f"results_dir/evaluation/matching_results_summary_{cohort_name}.xlsx"
    
    return config


def save_config(config: Dict[str, Any]) -> tuple[str, str]:
    """
    Save configuration with versioning.
    
    1. Merge with existing config for partial updates
    2. Auto-generate paths based on cohortName
    3. Create directories if they don't exist
    4. Save versioned copy
    5. Update active config
    
    Args:
        config: Configuration dictionary to save (can be partial)
        
    Returns:
        Tuple of (versioned filename, active filename)
    """
    # Get existing config and merge with updates
    existing_config = get_active_config()
    
    # Merge the incoming config with existing (incoming values override)
    for key, value in config.items():
        if value is not None:  # Only update if value is provided
            existing_config[key] = value
    
    # Auto-generate paths based on cohortName
    final_config = auto_generate_paths(existing_config)
    
    cohort_name = final_config.get("cohortName", "dummy_cohort1")
    
    # Ensure directories exist
    file_ops.ensure_directories(cohort_name)
    
    # Create versioned filename
    versioned_filename = file_ops.create_versioned_filename("data_config", cohort_name)
    versioned_path = f"config_files/overall_config_settings/{versioned_filename}"
    
    # Save versioned copy
    file_ops.write_json(versioned_path, final_config)
    
    # Update active config
    file_ops.write_json(ACTIVE_CONFIG_PATH, final_config)
    
    return versioned_filename, "active_data_config.json"


def get_default_prompt_settings() -> Dict[str, Any]:
    """Get default prompt settings with all required agents."""
    return {
        "final_decision_agent": {
            "system_prompt": "You are the final decision-making agent in a clinical trial matching system.",
            "main_prompt": "Make a final match decision for this patient-trial pair.",
            "skip": False
        },
        "eligibility_checker_agent": {
            "system_prompt": "You are a clinical trial eligibility expert.",
            "main_prompt": "Analyze patient eligibility for this trial.",
            "skip": False
        },
        "patient_analyzer_agent": {
            "system_prompt": "You are a clinical expert specializing in patient analysis.",
            "main_prompt": "Analyze this patient information and extract structured data.",
            "skip": False
        },
        "trial_analyzer_agent": {
            "system_prompt": "You are an expert at analyzing clinical trial protocols.",
            "main_prompt": "Analyze this clinical trial and extract key eligibility information.",
            "skip": False
        },
        "patient_record_summarize": {
            "main_prompt": "You are an expert clinical reasoning AI specializing in oncology.",
            "skip": False
        },
        "extract_features": {
            "main_prompt": "You are an expert clinical reasoning AI specializing in oncology.",
            "skip": False
        }
    }


def get_prompt_settings() -> Dict[str, Any]:
    """
    Get prompt settings, creating defaults if needed.
    Also ensures trial_analyzer_agent exists.
    
    Returns:
        Prompt settings dictionary
    """
    if not file_ops.file_exists(PROMPT_SETTINGS_PATH):
        default_prompts = get_default_prompt_settings()
        file_ops.write_json(PROMPT_SETTINGS_PATH, default_prompts)
        return default_prompts
    
    prompts = file_ops.read_json(PROMPT_SETTINGS_PATH)
    
    # Ensure trial_analyzer_agent exists
    if "trial_analyzer_agent" not in prompts:
        prompts["trial_analyzer_agent"] = {
            "system_prompt": "You are an expert at analyzing clinical trial protocols.",
            "main_prompt": "Analyze this clinical trial and extract key eligibility information.",
            "skip": False
        }
        file_ops.write_json(PROMPT_SETTINGS_PATH, prompts)
    
    return prompts


def get_prompt_settings_modified_time() -> str:
    """Get the last modified time of prompt settings."""
    modified = file_ops.get_file_modified_time(PROMPT_SETTINGS_PATH)
    if modified is None:
        return datetime.now().isoformat()
    return modified


def update_agent_prompt(agent_name: str, updates: Dict[str, Any]) -> bool:
    """
    Update a specific agent's prompt settings.
    
    Args:
        agent_name: Name of the agent to update
        updates: Dictionary with updates (system_prompt, main_prompt, skip)
        
    Returns:
        True if successful, False if agent not found
    """
    prompts = get_prompt_settings()
    
    if agent_name not in prompts:
        return False
    
    # Update only provided fields
    if updates.get("system_prompt") is not None:
        prompts[agent_name]["system_prompt"] = updates["system_prompt"]
    if updates.get("main_prompt") is not None:
        prompts[agent_name]["main_prompt"] = updates["main_prompt"]
    if updates.get("skip") is not None:
        prompts[agent_name]["skip"] = updates["skip"]
    
    file_ops.write_json(PROMPT_SETTINGS_PATH, prompts)
    return True


def save_prompts_versioned() -> str:
    """
    Save prompts with versioning.
    
    Returns:
        Versioned filename
    """
    prompts = get_prompt_settings()
    versioned_filename = file_ops.create_versioned_filename(
        "sigmatch_standard_prompt_content", 
        "backup"
    )
    versioned_path = f"config_files/prompt_settings/{versioned_filename}"
    file_ops.write_json(versioned_path, prompts)
    return versioned_filename


def get_evaluation_criteria() -> Dict[str, Any]:
    """
    Get evaluation criteria chat history.
    
    Returns:
        Evaluation criteria dictionary with messages and final_criteria
    """
    if not file_ops.file_exists(EVALUATION_CRITERIA_PATH):
        return {
            "messages": [],
            "final_criteria": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    return file_ops.read_json(EVALUATION_CRITERIA_PATH)


def save_evaluation_criteria(data: Dict[str, Any]) -> None:
    """Save evaluation criteria data."""
    data["updated_at"] = datetime.now().isoformat()
    if "created_at" not in data:
        data["created_at"] = datetime.now().isoformat()
    file_ops.write_json(EVALUATION_CRITERIA_PATH, data)


def add_chat_message(role: str, content: str) -> Dict[str, Any]:
    """
    Add a message to the evaluation criteria chat history.
    
    Args:
        role: Message role ("user" or "assistant")
        content: Message content
        
    Returns:
        The added message with timestamp
    """
    criteria = get_evaluation_criteria()
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    criteria["messages"].append(message)
    save_evaluation_criteria(criteria)
    
    return message


def save_final_criteria(final_criteria: str) -> None:
    """
    Save the final evaluation criteria text.
    
    Args:
        final_criteria: The final criteria text
    """
    criteria = get_evaluation_criteria()
    criteria["final_criteria"] = final_criteria
    save_evaluation_criteria(criteria)

