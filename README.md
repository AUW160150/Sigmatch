# Sigmatch Frontend (Streamlit)

A Streamlit-based frontend for the Sigmatch clinical trial matching pipeline.

## Quick Setup on SageMaker

```bash
# 1. Navigate to your sigmatch folder
cd /user-default-efs/sigmatch

# 2. Clone this repo
git clone https://github.com/AUW160150/Sigmatch.git streamlit_frontend

# 3. Setup environment
cd streamlit_frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py --server.port 8501
```

## Your Existing Structure

This app expects your existing sigmatch folder to have:

```
/user-default-efs/sigmatch/
├── orchestrate_pipeline.py          ← Your pipeline script (REQUIRED)
├── agent_framework.py
├── execute_llm_summarization.py
├── ocr.py
├── ...other scripts...
│
├── config_files/
│   ├── overall_config_settings/
│   │   └── active_data_config.json  ← Created/updated by app
│   ├── prompt_settings/
│   │   └── sigmatch_standard_prompt_content.json
│   ├── trial_files/
│   │   └── *.json                   ← Trial definitions
│   └── pipeline_json_files/
│       └── *.json                   ← Patient cohorts
│
├── documents/
│   ├── ocr/
│   └── pdfs/
│
├── results_dir/
│   ├── matching/
│   │   └── {cohort_name}/
│   │       └── matching_results.csv ← Pipeline output
│   ├── llm_summarization/
│   └── evaluation/
│
└── streamlit_frontend/              ← THIS REPO (cloned here)
    ├── app.py                       ← Main Streamlit app
    ├── requirements.txt
    └── README.md
```

## How It Works

1. The app looks for files in the **PARENT** directory (`/sigmatch/`)
2. When you click "Run Pipeline", it executes your `orchestrate_pipeline.py`
3. Results are saved to `results_dir/matching/{cohort_name}/`
4. Config is saved to `config_files/overall_config_settings/`

## Pipeline Requirements

Your `orchestrate_pipeline.py` must accept these arguments:

```bash
python orchestrate_pipeline.py \
    --data_config_json config_files/overall_config_settings/active_data_config.json \
    --run_ocr True/False \
    --do_llm_summarization True/False \
    --do_patient_matching True/False \
    --do_evaluation True/False
```

## Pages

| Page | Description |
|------|-------------|
| **Setup / Paths** | Verify file structure and paths |
| **Configure** | Set up trial, cohort, and run pipeline |
| **Adjust Prompts** | Edit AI agent prompts |
| **Evaluation Criteria** | Chat interface for criteria |
| **Review Results** | Manual review (in development) |
| **Results Summary** | View matching results and statistics |

## First Time Usage

1. Run the app and go to **"Setup / Paths"**
2. Verify all checkmarks are green (✅)
3. If `orchestrate_pipeline.py` shows ❌, check it's in `/sigmatch/`
4. Go to **"Configure"** to set up your first run

## Troubleshooting

### "orchestrate_pipeline.py NOT found"
Make sure it's in the parent folder (`/sigmatch/`), not inside `streamlit_frontend/`

### "No trial files" or "No cohort files"  
Add JSON files to `config_files/trial_files/` and `config_files/pipeline_json_files/`

### Pipeline fails
- Check the "View Warnings/Errors" expander for details
- Verify all Python dependencies are installed
- Check paths in `active_data_config.json`

## Updating

```bash
cd /user-default-efs/sigmatch/streamlit_frontend
git pull origin main
```

## Contact

- Frontend issues: Rodela
- Pipeline issues: Noah

