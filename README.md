# 🏥 Sigmatch - Clinical Trial Patient Matching API

> **Intelligent backend system for matching cancer patients with clinical trial eligibility criteria using AI-powered configuration management**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🌐 **Live Demo:** [sigmatch.lovable.app](https://sigmatch.lovable.app)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [API Endpoints](#-api-endpoints)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Advanced Features](#-advanced-features)
- [Documentation](#-documentation)

---

## 🎯 Overview

Sigmatch is a sophisticated **FastAPI-based backend** that powers a clinical trial matching application. It provides intelligent configuration management, dynamic cohort assembly, and automated result analysis for matching cancer patients to appropriate clinical trials.

The system is designed for **healthcare organizations, research institutions, and pharmaceutical companies** conducting clinical trials, enabling efficient patient-trial matching through:

- **Dynamic Configuration Management** - Auto-generates file paths and manages versioned configurations
- **Intelligent Cohort Assembly** - Natural language criteria parsing to filter patient cohorts
- **Real-time Results Analysis** - Statistical summaries and downloadable matching reports
- **Scalable Architecture** - Handles any number of trials, cohorts, and patients without code changes

---

## ✨ Key Features

### 🔧 Configuration Management
- **Smart Path Generation** - Automatically generates directory structures based on cohort names
- **Version Control** - Timestamped snapshots of all configuration changes
- **Auto-Repair** - Startup validation that fixes corrupted configs automatically
- **Intelligent Defaults** - Extracts cohort names from file paths when not explicitly provided

### 🧬 Cohort Management
- **Natural Language Filtering** - Assemble cohorts using plain English criteria (e.g., "colorectal cancer, male, stage 4")
- **Dynamic Keyword Extraction** - Automatically parses criteria and searches patient records
- **Flexible Matching** - AND/OR logic support with configurable maximum patient counts
- **Real-time Statistics** - Instant feedback on matched patients and match reasons

### 📊 Results Analysis
- **Statistical Summaries** - Total patients, match rates, score distributions
- **CSV Export** - Download complete matching results
- **Dynamic Path Resolution** - Always finds results regardless of cohort name
- **Visual Data** - Score distribution charts (1-5 rating scale)

### 🎨 AI Prompt Management
- **Multi-Agent System** - Manage prompts for 6 different AI agents
- **Live Updates** - Modify system/main prompts without code deployment
- **Skip Toggles** - Disable specific agents for testing
- **Versioned Backups** - Save prompt configurations with timestamps

### 📁 Trial Management
- **JSON Upload** - Upload trial definitions via API
- **Free-text Creation** - Create trials from plain text descriptions
- **Dynamic Discovery** - Automatically scans filesystem for all trials
- **Metadata Extraction** - Parses trial titles, IDs, and eligibility criteria

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│              (sigmatch.lovable.app)                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routers    │  │   Services   │  │    Models    │     │
│  │              │  │              │  │              │     │
│  │ • Config     │  │ • File Ops   │  │ • Pydantic   │     │
│  │ • Trials     │  │ • Config Mgr │  │ • Validation │     │
│  │ • Cohorts    │  │ • Synthetic  │  │ • Schemas    │     │
│  │ • Results    │  │              │  │              │     │
│  │ • Pipeline   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer (JSON/CSV)                          │
│  • Trial Definitions    • Patient Cohorts                  │
│  • Config Files         • Matching Results                 │
│  • Prompt Settings      • Evaluation Data                  │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

- **RESTful API** - Clean, intuitive endpoint structure
- **Separation of Concerns** - Routers → Services → Data
- **Type Safety** - Pydantic models for all requests/responses
- **Error Handling** - Graceful degradation with meaningful error messages
- **Scalability** - Filesystem-based scanning for infinite extensibility
- **Self-Healing** - Automatic validation and repair on startup

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | FastAPI 0.109.0 | High-performance async API |
| **Validation** | Pydantic 2.5.3 | Request/response validation |
| **Server** | Uvicorn 0.27.0 | ASGI server |
| **Data** | JSON/CSV | File-based storage |
| **Language** | Python 3.9+ | Backend logic |
| **CORS** | FastAPI Middleware | Cross-origin support |

---

## 📡 API Endpoints

### Configuration Management
```http
GET  /api/config              # Retrieve active configuration
POST /api/config              # Update configuration (auto-generates paths)
POST /api/config/snapshot     # Create versioned backup
```

### Trial Management
```http
GET  /api/trials              # List all available trials
GET  /api/trials/{filename}   # Get specific trial details
POST /api/trials              # Create trial from data
POST /api/trials/upload       # Upload trial JSON file
```

### Cohort Management
```http
GET  /api/cohorts             # List all cohorts with patient counts
GET  /api/cohorts/{filename}  # Get cohort details
POST /api/cohorts/generate    # Generate synthetic cohort
POST /api/cohorts/assemble    # Filter cohort by criteria
```

### Results & Analysis
```http
GET  /api/results/summary     # Statistical summary of matching results
GET  /api/results/download    # Download results CSV
GET  /api/results/detailed    # Full results as JSON
```

### AI Prompt Management
```http
GET  /api/prompts             # Get all agent prompts
GET  /api/prompts/{agent}     # Get specific agent prompt
PUT  /api/prompts/{agent}     # Update agent prompt
POST /api/prompts/save        # Create versioned backup
```

### Pipeline Execution
```http
POST /api/pipeline/run        # Generate pipeline command
GET  /api/pipeline/status     # Check pipeline status
```

### Evaluation Chat
```http
GET  /api/chat/history        # Get chat history
POST /api/chat/message        # Add message
POST /api/chat/save-criteria  # Save final criteria
```

**📖 Full API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AUW160150/sigmatch.git
   cd sigmatch
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - API: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Quick Test

```bash
# Check server health
curl http://localhost:8000/health

# List available trials
curl http://localhost:8000/api/trials | jq

# Get results summary
curl http://localhost:8000/api/results/summary | jq
```

---

## 📂 Project Structure

```
sigmatch/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── routers/                   # API endpoint handlers
│   │   ├── config.py              # Configuration management
│   │   ├── trials.py              # Trial CRUD operations
│   │   ├── cohorts.py             # Cohort management & assembly
│   │   ├── results.py             # Results analysis & download
│   │   ├── prompts.py             # AI prompt management
│   │   ├── pipeline.py            # Pipeline command generation
│   │   └── chat.py                # Evaluation chat interface
│   ├── services/                  # Business logic layer
│   │   ├── file_ops.py            # File system operations
│   │   ├── config_manager.py      # Config logic & path generation
│   │   └── synthetic_data.py      # Test data generation
│   ├── models/                    # Data models
│   │   └── schemas.py             # Pydantic request/response models
│   └── data/
│       └── Sigmatch/              # Data storage
│           ├── config_files/      # Configuration JSONs
│           │   ├── overall_config_settings/
│           │   ├── trial_files/
│           │   ├── pipeline_json_files/
│           │   └── prompt_settings/
│           ├── documents/         # PDF/OCR data
│           ├── results_dir/       # Matching results
│           └── snapshots/         # Versioned backups
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
└── Documentation/
    ├── BACKEND_AUDIT_REPORT.md    # Complete system audit
    ├── CONFIG_FIX_SUMMARY.md      # Configuration handling details
    ├── ASSEMBLE_COHORT_FEATURE.md # Cohort assembly documentation
    └── QUICK_REFERENCE.md         # Quick start guide
```

---

## 🎓 Advanced Features

### 1. Dynamic Path Generation

The system automatically generates all file paths based on cohort names:

```python
# Input
{
  "cohortName": "bladder_study_2024"
}

# Auto-generated paths
{
  "pdf_data_dir": "documents/pdfs/bladder_study_2024",
  "matching_result_dir": "results_dir/matching/bladder_study_2024",
  "extracted_features_path": "results_dir/llm_summarization/bladder_study_2024/patient_feature_summaries_bladder_study_2024.csv"
}
```

### 2. Intelligent Cohort Assembly

Natural language criteria parsing with AND logic:

```bash
POST /api/cohorts/assemble
{
  "criteria": ["colorectal cancer", "stage 4", "metastatic"],
  "max_patients": 100,
  "cohort_source": "dummy_cohort1.json"
}

# Returns matched patients with reasons
{
  "matched_count": 15,
  "matched_patients": [
    {
      "patient_id": "P001",
      "match_reasons": [
        "Matches 'colorectal cancer' (found: colorectal, cancer)",
        "Matches 'stage 4' (found: stage, 4)",
        "Matches 'metastatic' (found: metastatic)"
      ]
    }
  ]
}
```

### 3. Configuration Versioning

Every config change creates a timestamped backup:

```
config_files/overall_config_settings/
├── active_data_config.json                           # Current active
├── data_config_bladder_study__20240115_103000.json  # Backup 1
└── data_config_bladder_study__20240116_143022.json  # Backup 2
```

### 4. Self-Healing System

On startup, the backend validates and repairs configurations:

```
WARN: Config has empty cohortName, fixing...
INFO: Extracted cohort name 'dummy_cohort1' from patients_file_path
INFO: Fixed cohortName with complete paths
```

---

## 📚 Documentation

Comprehensive documentation is available in the project:

| Document | Description |
|----------|-------------|
| **BACKEND_AUDIT_REPORT.md** | Complete 11-part system audit with test results |
| **CONFIG_FIX_SUMMARY.md** | Configuration handling and auto-repair details |
| **ASSEMBLE_COHORT_FEATURE.md** | Cohort assembly API and keyword extraction |
| **QUICK_REFERENCE.md** | Quick start guide with examples |

**Interactive API Docs:** Visit `/docs` endpoint for Swagger UI with live testing

---

## 🔐 Security Notes

**Development Mode:**
- CORS enabled for all origins (`allow_origins=["*"]`)
- No authentication required
- Suitable for local development and testing

**Production Recommendations:**
- Enable authentication (OAuth2/JWT)
- Restrict CORS to specific domains
- Add rate limiting
- Use HTTPS/TLS
- Implement audit logging
- Add file size limits for uploads

---

## 🧪 Testing

The project includes comprehensive test data:

- **2 Clinical Trials** (Colorectal cancer, Bladder cancer)
- **2 Patient Cohorts** (25 and 20 patients)
- **Matching Results** (Pre-generated CSV)
- **Synthetic Data Generator** (Create test cohorts on demand)

Test all endpoints via Swagger UI at `/docs`

---

## 🤝 Contributing

This is a demonstration project showcasing:
- RESTful API design
- FastAPI best practices
- Healthcare data management
- Intelligent configuration systems
- Type-safe Python development

---

## 👨‍💻 Developer

**Backend Development:** FastAPI, Python, RESTful API Design, Healthcare Technology

Built with a focus on:
- Clean architecture and separation of concerns
- Type safety and validation
- Error handling and resilience
- Scalability and extensibility
- Developer experience (comprehensive docs, logging, debugging tools)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- **Live Application:** [sigmatch.lovable.app](https://sigmatch.lovable.app)
- **API Documentation:** `http://localhost:8000/docs`
- **GitHub Repository:** [github.com/AUW160150/sigmatch](https://github.com/AUW160150/sigmatch)

---

## 📧 Contact

For questions about this project or collaboration opportunities, please reach out through GitHub.

---

<div align="center">

**Built with ❤️ using FastAPI and Python**

⭐ Star this repo if you find it interesting!

</div>
