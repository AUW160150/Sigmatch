"""
Sigmatch Backend - FastAPI Application Entry Point

A clinical trial matching software backend that:
1. Serves API endpoints for a React frontend
2. Manages JSON configuration files (read/write/version)
3. Handles file operations (create directories, move files)
4. Generates and returns pipeline command strings
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import config, trials, cohorts, prompts, pipeline, results, chat
from app.services import file_ops, config_manager, synthetic_data


def initialize_application():
    """
    Initialize the application on startup.
    
    Ensures:
    1. Default directories exist
    2. Default files exist (creates from template if missing)
    3. Dummy cohorts are generated if missing
    4. At least one trial file exists
    5. trial_analyzer_agent is in prompt settings
    6. Active config has valid cohortName and complete paths
    """
    # Ensure base directories exist
    file_ops.ensure_base_directories()
    
    # Ensure active config exists (creates default if missing)
    config = config_manager.get_active_config()
    
    # Fix empty or invalid cohortName
    cohort_name = config.get("cohortName", "").strip()
    if not cohort_name:
        print("WARN: Config has empty cohortName, fixing...")
        # Try to extract from patients_file_path
        patients_path = config.get("patients_file_path", "")
        if patients_path:
            filename = patients_path.split("/")[-1]
            cohort_name = filename.replace(".json", "")
        else:
            cohort_name = "dummy_cohort1"
        
        # Update config with valid cohortName and paths
        config["cohortName"] = cohort_name
        config_manager.save_config(config)
        print(f"INFO: Fixed cohortName to '{cohort_name}' with complete paths")
    
    # Verify paths are complete (not missing cohort folder)
    matching_dir = config.get("matching_result_dir", "")
    if matching_dir and not cohort_name in matching_dir:
        print(f"WARN: Incomplete paths detected, regenerating...")
        config_manager.save_config(config)
        print(f"INFO: Paths regenerated for cohort '{cohort_name}'")
    
    # Ensure prompt settings exist with trial_analyzer_agent
    config_manager.get_prompt_settings()
    
    # Check for dummy cohorts and generate if missing
    cohorts_dir = "config_files/pipeline_json_files"
    existing_cohorts = file_ops.list_files(cohorts_dir, ".json")
    
    if "dummy_cohort1.json" not in existing_cohorts:
        patients = synthetic_data.generate_dummy_patients(25)
        file_ops.write_json(f"{cohorts_dir}/dummy_cohort1.json", patients)
        print("Generated dummy_cohort1.json")
    
    if "dummy_cohort2.json" not in existing_cohorts:
        patients = synthetic_data.generate_dummy_patients(25)
        file_ops.write_json(f"{cohorts_dir}/dummy_cohort2.json", patients)
        print("Generated dummy_cohort2.json")
    
    # Check for trial files
    trials_dir = "config_files/trial_files"
    existing_trials = file_ops.list_files(trials_dir, ".json")
    
    if not existing_trials:
        # Generate a default trial
        trial = synthetic_data.generate_dummy_trial()
        file_ops.write_json(f"{trials_dir}/default_trial.json", trial)
        print("Generated default_trial.json")
    
    print("Sigmatch backend initialized successfully!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    initialize_application()
    yield
    # Shutdown (cleanup if needed)
    print("Sigmatch backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Sigmatch Backend",
    description="Clinical trial matching software backend API",
    version="1.0.0",
    lifespan=lifespan
)


# Add custom validation error handler for debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ VALIDATION ERROR on {request.method} {request.url.path}")
    print(f"Request body: {await request.body()}")
    print(f"Validation errors: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Validation failed - check the request data format"
        },
    )


# Configure CORS for local development and Lovable frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(config.router)
app.include_router(trials.router)
app.include_router(cohorts.router)
app.include_router(prompts.router)
app.include_router(pipeline.router)
app.include_router(results.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Sigmatch Backend",
        "version": "1.0.0",
        "description": "Clinical trial matching software backend",
        "docs": "/docs",
        "endpoints": {
            "config": "/api/config",
            "trials": "/api/trials",
            "cohorts": "/api/cohorts",
            "prompts": "/api/prompts",
            "pipeline": "/api/pipeline",
            "results": "/api/results",
            "chat": "/api/chat"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
