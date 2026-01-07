"""
Pydantic models for Sigmatch API request/response schemas.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============ Config Schemas ============

class DataConfig(BaseModel):
    """Main configuration schema that the UI modifies."""
    model_config = ConfigDict(extra="allow")  # Allow extra fields from frontend
    
    cohortName: Optional[str] = None  # Optional - can update trial or cohort independently
    patients_file_path: Optional[str] = None  # Optional - can update trial or cohort independently
    pdf_data_dir: Optional[str] = None
    ocr_data_dir: Optional[str] = None
    llm_summarization_result_dir: Optional[str] = None
    matching_result_dir: Optional[str] = None
    trial_file_config_path: Optional[str] = None  # Made optional - users can save cohort before selecting trial
    pdf_info_path: Optional[str] = None
    signatera_df_path: Optional[str] = None
    signatera_filter_patients: Optional[str] = None
    llm_argument_json: Optional[str] = None
    extracted_features_path: Optional[str] = None
    evaluation_results_path: Optional[str] = None


class ConfigResponse(BaseModel):
    """Response for GET /api/config."""
    config: Dict[str, Any]
    last_modified: str


class ConfigSaveResponse(BaseModel):
    """Response for POST /api/config."""
    status: str
    version_file: str
    active_file: str


class SnapshotResponse(BaseModel):
    """Response for POST /api/config/snapshot."""
    status: str
    snapshot_dir: str
    files_saved: List[str]


# ============ Trial Schemas ============

class TrialBase(BaseModel):
    """Base trial schema."""
    title: str
    full_text: str
    id: Optional[str] = Field(None, serialization_alias="_id")


class TrialCreate(BaseModel):
    """Request body for creating a trial."""
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    
    title: str
    full_text: str
    id: Optional[str] = Field(None, alias="_id")


class TrialSummary(BaseModel):
    """Summary of a trial file."""
    filename: str
    title: str
    id: str = Field(serialization_alias="_id")


class TrialListResponse(BaseModel):
    """Response for GET /api/trials."""
    trials: List[TrialSummary]


class TrialResponse(BaseModel):
    """Full trial content response."""
    id: str = Field(serialization_alias="_id")
    title: str
    full_text: str


class TrialCreateResponse(BaseModel):
    """Response for POST /api/trials."""
    status: str
    filename: str
    path: str


class TrialUploadResponse(BaseModel):
    """Response for POST /api/trials/upload."""
    status: str
    filename: str
    trial: Dict[str, Any]


# ============ Cohort Schemas ============

class Patient(BaseModel):
    """Patient record schema."""
    patient_id: str
    full_text: str


class CohortSummary(BaseModel):
    """Summary of a cohort file."""
    filename: str
    patient_count: int


class CohortListResponse(BaseModel):
    """Response for GET /api/cohorts."""
    cohorts: List[CohortSummary]


class CohortDetailResponse(BaseModel):
    """Response for GET /api/cohorts/{filename}."""
    filename: str
    patients: List[Patient]
    patient_count: int


class CohortGenerateRequest(BaseModel):
    """Request body for generating a cohort."""
    name: str
    patient_count: int = 25


class CohortGenerateResponse(BaseModel):
    """Response for POST /api/cohorts/generate."""
    status: str
    filename: str
    patient_count: int


class CohortAssembleRequest(BaseModel):
    """Request for POST /api/cohorts/assemble."""
    criteria: List[str]
    max_patients: int = 100
    cohort_source: str = "dummy_cohort1.json"


class MatchedPatient(BaseModel):
    """A patient that matched the criteria."""
    patient_id: str
    match_reasons: List[str]


class CohortAssembleResponse(BaseModel):
    """Response for POST /api/cohorts/assemble."""
    status: str
    criteria_used: List[str]
    total_searched: int
    matched_count: int
    matched_patients: List[MatchedPatient]
    patient_ids_list: List[str]


# ============ Prompt Schemas ============

class AgentPrompt(BaseModel):
    """Single agent prompt configuration."""
    system_prompt: Optional[str] = None
    main_prompt: str
    skip: bool = False


class PromptUpdate(BaseModel):
    """Request body for updating a prompt."""
    system_prompt: Optional[str] = None
    main_prompt: Optional[str] = None
    skip: Optional[bool] = None


class PromptsResponse(BaseModel):
    """Response for GET /api/prompts."""
    prompts: Dict[str, Dict[str, Any]]
    last_modified: str


class PromptDetailResponse(BaseModel):
    """Response for GET /api/prompts/{agent_name}."""
    agent_name: str
    system_prompt: Optional[str] = None
    main_prompt: str
    skip: bool


class PromptUpdateResponse(BaseModel):
    """Response for PUT /api/prompts/{agent_name}."""
    status: str
    agent_name: str


class PromptsSaveResponse(BaseModel):
    """Response for POST /api/prompts/save."""
    status: str
    version_file: str


# ============ Pipeline Schemas ============

class PipelineRunRequest(BaseModel):
    """Request body for running the pipeline."""
    config_path: str = "config_files/overall_config_settings/active_data_config.json"
    run_ocr: bool = False
    do_llm_summarization: bool = True
    do_patient_matching: bool = True
    do_evaluation: bool = False


class PipelineRunResponse(BaseModel):
    """Response for POST /api/pipeline/run."""
    command: str
    config_used: Dict[str, Any]


class PipelineStatusResponse(BaseModel):
    """Response for GET /api/pipeline/status."""
    status: str
    last_run: Optional[str] = None
    last_command: Optional[str] = None


# ============ Results Schemas ============

class ResultsSummaryResponse(BaseModel):
    """Response for GET /api/results/summary."""
    has_results: bool
    cohort_name: str
    total_patients: int
    matched_count: int
    not_matched_count: int
    match_percentage: float
    score_distribution: Dict[str, int]


class MatchingResult(BaseModel):
    """Single matching result."""
    patient_id: str
    final_decision: str
    overall_score: int
    primary_reasons: str
    concerns: str
    decision_reasoning: str


class ResultsDetailedResponse(BaseModel):
    """Response for GET /api/results/detailed."""
    results: List[MatchingResult]


# ============ Chat Schemas ============

class ChatMessage(BaseModel):
    """Single chat message."""
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatMessageRequest(BaseModel):
    """Request body for adding a chat message."""
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    """Response for GET /api/chat/history."""
    messages: List[ChatMessage]
    final_criteria: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Response for POST /api/chat/message."""
    status: str
    message: ChatMessage


class SaveCriteriaRequest(BaseModel):
    """Request body for saving evaluation criteria."""
    final_criteria: str


class SaveCriteriaResponse(BaseModel):
    """Response for POST /api/chat/save-criteria."""
    status: str
    file: str

