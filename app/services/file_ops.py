"""
File operations service for Sigmatch.
Handles JSON read/write, directory creation, and file versioning.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Base directory for all Sigmatch data
BASE_DIR = Path(__file__).parent.parent / "data" / "Sigmatch"


def get_base_dir() -> Path:
    """Get the base directory for Sigmatch data."""
    return BASE_DIR


def read_json(filepath: str) -> Dict[str, Any]:
    """
    Safely read a JSON file.
    
    Args:
        filepath: Path relative to BASE_DIR
        
    Returns:
        Parsed JSON content as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    full_path = BASE_DIR / filepath
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_json_list(filepath: str) -> List[Dict[str, Any]]:
    """
    Read a JSON file that contains a list.
    
    Args:
        filepath: Path relative to BASE_DIR
        
    Returns:
        Parsed JSON content as list
    """
    full_path = BASE_DIR / filepath
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(
    filepath: str, 
    data: Union[Dict[str, Any], List[Dict[str, Any]]], 
    create_dirs: bool = True
) -> str:
    """
    Write JSON file, optionally creating directories.
    
    Args:
        filepath: Path relative to BASE_DIR
        data: Data to write (dict or list)
        create_dirs: Whether to create parent directories
        
    Returns:
        Full path to written file
    """
    full_path = BASE_DIR / filepath
    if create_dirs:
        full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return str(full_path)


def file_exists(filepath: str) -> bool:
    """Check if a file exists relative to BASE_DIR."""
    return (BASE_DIR / filepath).exists()


def get_file_modified_time(filepath: str) -> Optional[str]:
    """
    Get the last modified time of a file as ISO format string.
    
    Args:
        filepath: Path relative to BASE_DIR
        
    Returns:
        ISO format datetime string or None if file doesn't exist
    """
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return None
    mtime = os.path.getmtime(full_path)
    return datetime.fromtimestamp(mtime).isoformat()


def create_versioned_filename(
    base_name: str, 
    identifier: str, 
    extension: str = "json"
) -> str:
    """
    Create a versioned filename with timestamp.
    
    Args:
        base_name: Base name for the file (e.g., "data_config")
        identifier: Identifier to include (e.g., cohort name)
        extension: File extension without dot
        
    Returns:
        Versioned filename like "data_config_my_cohort__20240115_103000.json"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{identifier}__{timestamp}.{extension}"


def ensure_directories(cohort_name: str) -> None:
    """
    Create all necessary directories for a cohort.
    
    Args:
        cohort_name: Name of the cohort
    """
    dirs = [
        f"results_dir/llm_summarization/{cohort_name}",
        f"results_dir/matching/{cohort_name}",
        f"results_dir/llm_extracted_features/{cohort_name}",
        "results_dir/evaluation",
        f"documents/ocr/{cohort_name}",
        f"documents/pdfs/{cohort_name}",
        "snapshots"
    ]
    for d in dirs:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)


def ensure_base_directories() -> None:
    """Create all base directories needed for the application."""
    dirs = [
        "config_files/overall_config_settings",
        "config_files/trial_files",
        "config_files/pipeline_json_files",
        "config_files/prompt_settings",
        "config_files/other_config_files",
        "results_dir/llm_summarization",
        "results_dir/matching",
        "results_dir/llm_extracted_features",
        "results_dir/evaluation",
        "documents/ocr",
        "documents/pdfs",
        "snapshots"
    ]
    for d in dirs:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)


def list_files(directory: str, extension: str = ".json") -> List[str]:
    """
    List all files with given extension in directory.
    
    Args:
        directory: Directory path relative to BASE_DIR
        extension: File extension including dot (e.g., ".json")
        
    Returns:
        List of filenames (not full paths)
    """
    dir_path = BASE_DIR / directory
    if not dir_path.exists():
        return []
    return [f.name for f in dir_path.glob(f"*{extension}")]


def copy_file(src: str, dest: str) -> str:
    """
    Copy a file from src to dest (both relative to BASE_DIR).
    
    Args:
        src: Source path relative to BASE_DIR
        dest: Destination path relative to BASE_DIR
        
    Returns:
        Full path to destination file
    """
    src_path = BASE_DIR / src
    dest_path = BASE_DIR / dest
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest_path)
    return str(dest_path)


def create_snapshot(snapshot_name: Optional[str] = None) -> tuple[str, List[str]]:
    """
    Create a full snapshot of all config files.
    
    Args:
        snapshot_name: Optional custom snapshot name. If None, uses timestamp.
        
    Returns:
        Tuple of (snapshot directory path, list of files saved)
    """
    if snapshot_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snapshot_{timestamp}"
    
    snapshot_dir = f"snapshots/{snapshot_name}"
    (BASE_DIR / snapshot_dir).mkdir(parents=True, exist_ok=True)
    
    files_saved = []
    
    # Copy config files
    config_dirs = [
        "config_files/overall_config_settings",
        "config_files/prompt_settings",
        "config_files/trial_files",
        "config_files/pipeline_json_files"
    ]
    
    for config_dir in config_dirs:
        src_dir = BASE_DIR / config_dir
        if src_dir.exists():
            for json_file in src_dir.glob("*.json"):
                # Maintain directory structure in snapshot
                relative_path = json_file.relative_to(BASE_DIR)
                dest_path = BASE_DIR / snapshot_dir / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(json_file, dest_path)
                files_saved.append(str(relative_path))
    
    return snapshot_dir, files_saved


def read_csv(filepath: str) -> List[Dict[str, str]]:
    """
    Read a CSV file and return as list of dictionaries.
    
    Args:
        filepath: Path relative to BASE_DIR
        
    Returns:
        List of dictionaries, one per row
    """
    import csv
    full_path = BASE_DIR / filepath
    with open(full_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(filepath: str, data: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    """
    Write data to a CSV file.
    
    Args:
        filepath: Path relative to BASE_DIR
        data: List of dictionaries to write
        fieldnames: Column names
        
    Returns:
        Full path to written file
    """
    import csv
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return str(full_path)


def get_full_path(filepath: str) -> Path:
    """Get the full absolute path for a file."""
    return BASE_DIR / filepath

