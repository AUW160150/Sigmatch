# Sigmatch Frontend (Streamlit)

A Streamlit-based frontend for the Sigmatch clinical trial matching pipeline.

## Setup on SageMaker

### 1. Navigate to your sigmatch folder:
```bash
cd /user-default-efs/sigmatch
```

### 2. Clone this repo as the streamlit folder:
```bash
git clone https://github.com/AUW160150/Sigmatch.git streamlit_frontend
```

Or if you already have it, pull the latest:
```bash
cd streamlit_frontend
git pull origin main
```

### 3. Setup Python environment:
```bash
cd streamlit_frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the app:
```bash
streamlit run app.py --server.port 8501
```

## Expected File Structure

The app expects to be placed in a subfolder of your main sigmatch directory:

```
/sigmatch/                              ← Parent directory
├── orchestrate_pipeline.py             ← Your pipeline script (REQUIRED)
├── agent_framework.py
├── execute_llm_summarization.py
├── ...other scripts...
│
├── config_files/
│   ├── overall_config_settings/
│   │   └── active_data_config.json     ← Auto-created/updated
│   ├── prompt_settings/
│   │   └── sigmatch_standard_prompt_content.json
│   ├── trial_files/
│   │   └── *.json                      ← Trial definition files
│   └── pipeline_json_files/
│       └── *.json                      ← Patient cohort files
│
├── documents/
│   ├── ocr/
│   └── pdfs/
│
├── results_dir/
│   ├── matching/
│   │   └── {cohort_name}/
│   │       └── matching_results.csv    ← Pipeline output
│   ├── llm_summarization/
│   └── evaluation/
│
└── streamlit_frontend/                 ← This app folder
    ├── app.py                          ← Main Streamlit app
    ├── requirements.txt
    ├── README.md
    └── venv/                           ← Python virtual environment
```

## Pipeline Requirements

Your `orchestrate_pipeline.py` must accept these command-line arguments:

```bash
python orchestrate_pipeline.py \
    --data_config_json config_files/overall_config_settings/active_data_config.json \
    --run_ocr True/False \
    --do_llm_summarization True/False \
    --do_patient_matching True/False \
    --do_evaluation True/False
```

The pipeline should:
1. Read the config from the specified JSON path
2. Write results to `results_dir/matching/{cohort_name}/matching_results.csv`
3. Output should include columns: `patient_id`, `final_decision`, `overall_score`, `primary_reasons`

## Usage

1. Open the app URL provided by SageMaker/Streamlit
2. Go to **"Setup / Paths"** to verify all files are found (green checkmarks)
3. Go to **"Configure"** to:
   - Select your trial and cohort
   - Set the cohort name
   - Choose pipeline steps
   - Click **"Run Pipeline"**
4. View results in **"Results Summary"**

## Pages

| Page | Description |
|------|-------------|
| **Setup / Paths** | Verify file structure and paths |
| **Configure** | Set up trial, cohort, and run pipeline |
| **Adjust Prompts** | Edit AI agent prompts |
| **Evaluation Criteria** | Chat interface for criteria |
| **Review Results** | Manual review (in development) |
| **Results Summary** | View matching results and statistics |

## Troubleshooting

### "orchestrate_pipeline.py NOT found"
- Make sure the pipeline script is in the parent directory (not in the streamlit folder)
- Check the path shown in "Setup / Paths"

### "No trial files" or "No cohort files"
- Add JSON files to `config_files/trial_files/` and `config_files/pipeline_json_files/`

### Pipeline fails
- Check the "View Warnings/Errors" expander for details
- Make sure all required Python packages are installed in your environment
- Verify paths in `active_data_config.json` are correct

## Development

To modify the frontend:
1. Edit `app.py`
2. Streamlit auto-reloads on file changes
3. Use `st.rerun()` to force a refresh

## Contact

For issues with the frontend, contact Rodela.
For issues with the pipeline, contact Noah.

