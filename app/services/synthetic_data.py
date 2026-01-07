"""
Synthetic data generation service for Sigmatch.
Generates realistic clinical trial data for testing.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


# Sample data pools for generating realistic clinical records
ETHNICITIES = ["Caucasian", "African American", "Asian", "Hispanic", "Native American", "Pacific Islander"]
GENDERS = ["male", "female"]
CANCER_TYPES = [
    ("colorectal adenocarcinoma", "colon"),
    ("rectal adenocarcinoma", "rectum"),
    ("sigmoid colon cancer", "sigmoid"),
    ("ascending colon cancer", "colon"),
    ("transverse colon cancer", "colon"),
]
STAGES = ["I", "II", "IIA", "IIB", "IIC", "III", "IIIA", "IIIB", "IIIC", "IV", "IVA", "IVB"]
SURGERIES = [
    "right hemicolectomy",
    "left hemicolectomy", 
    "sigmoid colectomy",
    "low anterior resection",
    "abdominoperineal resection",
    "total colectomy",
    "subtotal colectomy",
    "transanal excision",
    "laparoscopic colectomy"
]
MEDICATIONS = [
    "Ondansetron 8mg PRN",
    "Oxycodone 5mg PRN",
    "Pantoprazole 40mg daily",
    "Lisinopril 10mg daily",
    "Metformin 500mg BID",
    "Aspirin 81mg daily",
    "Atorvastatin 20mg daily",
    "Omeprazole 20mg daily",
    "Metoprolol 25mg BID",
    "Amlodipine 5mg daily",
    "Gabapentin 300mg TID",
    "Ferrous sulfate 325mg daily"
]
COMORBIDITIES = [
    "hypertension",
    "type 2 diabetes",
    "hyperlipidemia",
    "GERD",
    "osteoarthritis",
    "hypothyroidism",
    "obesity",
    "CKD stage 3",
    "COPD",
    "atrial fibrillation"
]
CHEMO_REGIMENS = ["FOLFOX", "FOLFIRI", "CAPOX", "5-FU/LV", "capecitabine"]


def _random_date(start_year: int = 2023, end_year: int = 2024) -> str:
    """Generate a random date string in MM/DD/YYYY format."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date = start + timedelta(days=random_days)
    return date.strftime("%m/%d/%Y")


def _generate_lab_values() -> str:
    """Generate realistic lab values string."""
    cea = round(random.uniform(0.5, 25.0), 1)
    wbc = round(random.uniform(3.5, 10.0), 1)
    hgb = round(random.uniform(9.5, 14.5), 1)
    platelets = random.randint(120, 350)
    creatinine = round(random.uniform(0.6, 1.4), 1)
    alt = random.randint(15, 55)
    ast = random.randint(15, 50)
    
    date = _random_date()
    return f"Lab values ({date}): CEA {cea} ng/mL, WBC {wbc}, Hgb {hgb}, Platelets {platelets}, Creatinine {creatinine}, ALT {alt}, AST {ast}."


def _generate_patient_record(patient_num: int) -> Dict[str, str]:
    """Generate a single synthetic patient record."""
    age = random.randint(35, 82)
    gender = random.choice(GENDERS)
    ethnicity = random.choice(ETHNICITIES)
    cancer_type, location = random.choice(CANCER_TYPES)
    stage = random.choice(STAGES)
    surgery = random.choice(SURGERIES)
    ecog = random.randint(0, 2)
    
    # Random number of medications and comorbidities
    num_meds = random.randint(1, 4)
    num_comorbidities = random.randint(0, 3)
    
    meds = random.sample(MEDICATIONS, min(num_meds, len(MEDICATIONS)))
    comorbidities = random.sample(COMORBIDITIES, min(num_comorbidities, len(COMORBIDITIES)))
    
    # Generate diagnosis info
    diagnosis_date = _random_date(2023, 2023)
    surgery_date = _random_date(2023, 2024)
    
    # Build the full text
    full_text = f"Patient is a {age}-year-old {ethnicity} {gender} with a diagnosis of stage {stage} {cancer_type}. "
    full_text += f"Initial diagnosis was made on {diagnosis_date} following colonoscopy with biopsy. "
    full_text += f"Patient underwent {surgery} on {surgery_date} with R0 resection. "
    
    # Add pathology details
    nodes_positive = random.randint(0, 6)
    nodes_total = random.randint(12, 28)
    differentiation = random.choice(["well", "moderately", "poorly"])
    full_text += f"Pathology confirmed {differentiation} differentiated adenocarcinoma. "
    full_text += f"{nodes_positive} of {nodes_total} lymph nodes positive for metastatic disease.\n\n"
    
    # Add medications
    if meds:
        full_text += f"Current medications: {', '.join(meds)}.\n\n"
    
    # Add lab values
    full_text += _generate_lab_values() + "\n\n"
    
    # Add ECOG status
    full_text += f"ECOG Performance Status: {ecog}\n\n"
    
    # Add hepatitis status
    full_text += "Patient is HBsAg negative, HCV antibody negative. No active infections. "
    
    # Add comorbidities
    if comorbidities:
        full_text += f"Medical history includes {', '.join(comorbidities)}. "
    
    full_text += "No history of other malignancies. No known drug allergies.\n\n"
    
    # Add Signatera result (50% positive)
    signatera_date = _random_date(2023, 2024)
    if random.random() > 0.5:
        mtm = round(random.uniform(0.5, 5.0), 1)
        full_text += f"Signatera ctDNA test ({signatera_date}): Positive ({mtm} MTM/mL)\n\n"
    else:
        full_text += f"Signatera ({signatera_date}): Negative\n\n"
    
    # Add treatment plan
    if stage in ["III", "IIIA", "IIIB", "IIIC"]:
        regimen = random.choice(CHEMO_REGIMENS)
        full_text += f"Plan: Adjuvant {regimen} chemotherapy x 6 months."
    elif stage in ["II", "IIA", "IIB"]:
        full_text += "Consideration for observation vs adjuvant chemotherapy given risk features."
    else:
        full_text += "Surveillance protocol initiated."
    
    return {
        "patient_id": f"P{patient_num:03d}",
        "full_text": full_text.strip()
    }


def generate_dummy_patients(n: int = 25) -> List[Dict[str, str]]:
    """
    Generate n synthetic patient records for testing.
    
    Each patient has varied:
    - Age (35-82)
    - Sex (Male/Female)
    - Ethnicity
    - Cancer type (colorectal focus)
    - Stage (I through IV)
    - Treatment history
    - Lab values
    - ECOG status (0-2)
    
    Args:
        n: Number of patients to generate
        
    Returns:
        List of patient dictionaries with patient_id and full_text
    """
    return [_generate_patient_record(i + 1) for i in range(n)]


def generate_dummy_trial() -> Dict[str, Any]:
    """
    Generate a synthetic clinical trial description.
    
    Returns:
        Trial dictionary with _id, title, and full_text
    """
    trial_id = f"synthetic_trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    trial = {
        "_id": trial_id,
        "title": "Synthetic Colorectal Cancer Clinical Trial",
        "full_text": """Key inclusion criteria: Eligible subjects shall meet all of the following:
(1) Histopathologically diagnosed with colorectal adenocarcinoma.
(2) The primary location of the tumor is the colon or rectum.
(3) Clinical stage II or III colorectal cancer for which R0 resection has been performed or scheduled.
(4) Age ≥18 years at informed consent.
(5) ECOG Performance Status 0 or 1.
(6) Adequate organ function as defined by: ANC ≥1500/mm³, Platelets ≥100,000/mm³, Hemoglobin ≥9.0 g/dL, Creatinine ≤1.5x ULN, Bilirubin ≤1.5x ULN, AST/ALT ≤3x ULN.
(7) Written informed consent provided.

Key exclusion criteria:
(1) Prior systemic chemotherapy or radiotherapy for colorectal cancer (except neoadjuvant therapy for rectal cancer).
(2) Active double cancer (synchronous or metachronous malignancy within 5 years).
(3) Known BRAF V600E mutation (for certain study arms).
(4) Pregnant or breastfeeding women.
(5) Serious uncontrolled medical conditions or infections.
(6) Positive HBsAg or positive HCV antibody with detectable RNA.
(7) HIV antibody positive.
(8) Known hypersensitivity to study drugs.
(9) Psychiatric illness that would limit compliance with study requirements."""
    }
    
    return trial


def generate_dummy_results(patient_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Generate synthetic matching results for given patients.
    
    Args:
        patient_ids: List of patient IDs to generate results for
        
    Returns:
        List of matching result dictionaries
    """
    results = []
    
    decisions = ["MATCH", "NO-MATCH"]
    match_reasons = [
        "Stage III colorectal adenocarcinoma confirmed",
        "R0 resection achieved",
        "ECOG PS 0-1",
        "Age appropriate",
        "No exclusion criteria met",
        "Adequate organ function",
        "MSI-H status favorable"
    ]
    no_match_reasons = [
        "Stage IV disease with active treatment",
        "Prior therapy within 6 months",
        "ECOG PS 2 or higher",
        "Exclusion criteria triggered",
        "Inadequate organ function",
        "Age outside range"
    ]
    concerns = [
        "Missing some follow-up imaging data",
        "Borderline lab values",
        "Multiple comorbidities",
        "Prior radiation therapy",
        "Delayed therapy start",
        "None significant"
    ]
    
    for patient_id in patient_ids:
        decision = random.choice(decisions)
        score = random.randint(1, 5)
        
        # Bias scores based on decision
        if decision == "MATCH":
            score = max(3, score)
        else:
            score = min(3, score)
        
        reasons = match_reasons if decision == "MATCH" else no_match_reasons
        primary_reason = random.sample(reasons, min(3, len(reasons)))
        
        result = {
            "patient_id": patient_id,
            "final_decision": decision,
            "overall_score": score,
            "primary_reasons": "; ".join(primary_reason),
            "concerns": random.choice(concerns),
            "decision_reasoning": f"Patient evaluation complete. {decision} determination based on analysis of clinical data and trial criteria."
        }
        results.append(result)
    
    return results

