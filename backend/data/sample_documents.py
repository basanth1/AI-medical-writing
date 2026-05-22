"""
backend/data/sample_documents.py
Historical clinical trial documents pre-loaded into FAISS on startup.
Add new sample documents here to enrich retrieval quality.
"""

from typing import List, Dict, Any

SAMPLE_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "id": "hist_csp_onc_001",
        "content": """
Phase III Oncology Protocol — HER2+ Metastatic Breast Cancer:
Randomized, double-blind, placebo-controlled study. Primary endpoint: Overall Survival (OS).
Inclusion: adults ≥18, HER2+ mBC, ECOG 0-1, measurable disease per RECIST v1.1,
ANC ≥1.5×10⁹/L, PLT ≥100×10⁹/L, Hgb ≥9 g/dL, CrCl ≥30 mL/min.
Exclusion: prior PI3K/AKT/mTOR inhibitors, untreated CNS metastases, QTcF >470ms.
Stratification: prior lines (1 vs ≥2), HR status, geographic region.
Sample size: 520 (1:1), 415 OS events required, 80% power, HR=0.73, alpha=0.05.
Safety: CTCAE v5.0, SAE reporting 24h initial, 7-day follow-up. DSMB quarterly review.
Dose modifications: Drug A 150mg→100mg→50mg; paclitaxel per standard tables.
Ethics: IRB/IEC approval required per ICH E6(R2). Informed consent prior to any procedure.
        """.strip(),
        "metadata": {
            "indication":  "Oncology",
            "sub":         "Breast Cancer",
            "phase":       "Phase III",
            "doc_type":    "Clinical Study Protocol",
            "endpoint":    "Overall Survival",
            "year":        "2022",
        },
    },
    {
        "id": "hist_icf_cv_001",
        "content": """
Informed Consent Form — Phase II Cardiovascular Heart Failure Study:
Study purpose: evaluate [Drug] vs placebo for HFrEF (EF<40%).
Procedures: randomized 1:1, 24-week treatment, clinic visits every 4 weeks.
Lab assessments: BNP, eGFR, electrolytes, liver function at each visit.
ECG: screening, Week 4, Week 12, Week 24.
Common side effects: headache 15%, nausea 12%, dizziness 8%, fatigue 10%.
Serious risks: hypotension (2%), allergic reactions (<1%), liver enzyme elevations.
Benefits: potential improvement in symptoms; no guarantee of personal benefit.
Voluntary: participation voluntary; withdrawal at any time without penalty or loss of care.
Confidentiality: data identified by code number only; sponsor may inspect records.
Contact: Principal Investigator (24-hr emergency line) and IRB contact provided.
HIPAA authorization included as separate document per 45 CFR 164.508.
        """.strip(),
        "metadata": {
            "indication": "Cardiovascular",
            "phase":      "Phase II",
            "doc_type":   "Informed Consent Form",
            "endpoint":   "NYHA Class Improvement",
        },
    },
    {
        "id": "hist_csr_dm_001",
        "content": """
Clinical Study Report Synopsis — Phase III Type 2 Diabetes:
Design: multicenter, 2:1 (drug:placebo), double-blind, 52-week. N=450.
Population: adults 18–75, T2DM, HbA1c 7.5–10.5%, BMI 25–40 kg/m².
Primary result: HbA1c reduction −1.8% vs −0.3%; p<0.001; 95%CI (−1.7, −1.3).
Secondary: fasting glucose −2.1 vs −0.4 mmol/L (p<0.001); body weight −3.2 vs +0.5 kg (p<0.001).
Patient disposition: 450 enrolled, 421 completed (drug 94%, placebo 89%).
Safety: well-tolerated; no hypoglycaemia; no CV signal; DKA 0 events.
Common AEs: nasopharyngitis 12%, back pain 8%, diarrhoea 7%.
Conclusion: superior glycaemic control; favourable benefit-risk profile.
        """.strip(),
        "metadata": {
            "indication": "Endocrinology",
            "sub":        "Type 2 Diabetes",
            "phase":      "Phase III",
            "doc_type":   "Clinical Study Report",
            "endpoint":   "HbA1c Reduction",
        },
    },
    {
        "id": "hist_sap_onc_001",
        "content": """
Statistical Analysis Plan — Oncology Phase III:
Primary: stratified log-rank test (two-sided alpha=0.05). KM curves; Cox PH for HR+95%CI.
Sample size: 380 events for 80% power (HR=0.75, median OS 18 vs 24 months).
Populations: ITT (primary), PP (supportive), Safety (all dosed ≥1 dose).
Multiplicity: hierarchical — OS (alpha=0.04); PFS (alpha=0.01 conditional on OS significance).
Missing data: MI under MAR primary; MNAR tipping-point sensitivity analysis.
Subgroups: pre-specified by age, sex, ECOG PS, prior lines, geographic region.
Interim: 50% and 75% events, O'Brien-Fleming spending function. Futility at first IA.
Software: SAS 9.4 (primary); R 4.3 for graphical analyses. Analysis code locked prior to DBL.
        """.strip(),
        "metadata": {
            "indication": "Oncology",
            "phase":      "Phase III",
            "doc_type":   "Statistical Analysis Plan",
            "endpoint":   "Overall Survival",
        },
    },
    {
        "id": "hist_csp_neuro_001",
        "content": """
Phase II Neurology Protocol — Alzheimer's Disease:
Design: randomized, double-blind, placebo-controlled, 18-month treatment.
Primary endpoint: CDR-SB change from baseline at Month 18.
Secondary: MMSE, ADAS-Cog 13, ADCS-ADL, amyloid PET SUVr.
Population: mild cognitive impairment or mild AD, amyloid positive by PET or CSF.
Inclusion: MMSE 20–28, CDR-GS 0.5 or 1.0, confirmed amyloid pathology.
Exclusion: significant vascular disease on MRI, ARIA history, anticoagulation.
Safety: MRI safety monitoring for ARIA at Weeks 4, 8, 12, 26, 52, 78.
Stopping rules: ≥2 ARIA-E with symptoms → pause; independent safety committee review.
Sample size: 200 per arm (400 total), 90% power to detect −0.45 CDR-SB difference.
        """.strip(),
        "metadata": {
            "indication": "Neurology",
            "sub":        "Alzheimer's Disease",
            "phase":      "Phase II",
            "doc_type":   "Clinical Study Protocol",
            "endpoint":   "CDR-SB",
        },
    },
    {
        "id": "hist_csp_immuno_001",
        "content": """
Phase III Immunology Protocol — Rheumatoid Arthritis:
Randomized, double-blind study of [Drug] vs methotrexate in MTX-naïve RA patients.
Primary endpoint: ACR20 response rate at Week 24.
Secondary: DAS28-CRP, ACR50/70, HAQ-DI, mTSS radiographic progression.
Population: adults 18–75, active RA (≥6 swollen joints, ≥6 tender joints, CRP>1×ULN).
Exclusion: prior biologic DMARD, active TB or positive QuantiFERON, hepatitis B/C.
Concomitant medications: stable low-dose corticosteroids (≤10mg/day prednisone) permitted.
Safety: infections (bacterial, opportunistic, TB reactivation), malignancy, cardiovascular.
Sample size: 300 per arm (600 total), 85% power for ACR20 superiority.
Regulatory: FDA Fast Track designation granted; EMA Scientific Advice received.
        """.strip(),
        "metadata": {
            "indication": "Immunology",
            "sub":        "Rheumatoid Arthritis",
            "phase":      "Phase III",
            "doc_type":   "Clinical Study Protocol",
            "endpoint":   "ACR20",
        },
    },
]
