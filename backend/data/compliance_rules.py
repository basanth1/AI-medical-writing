"""
backend/data/compliance_rules.py
All regulatory compliance rules, entity patterns, and required-section
definitions in one place. Add/modify rules here — no service code changes needed.
"""

from typing import Dict, List, Tuple

# ── Rule format ───────────────────────────────────────────────────────────────
# Each rule is a dict:
#   id          : unique identifier (e.g. "CSP-001")
#   pattern     : regex pattern searched across all section content
#   required    : True → critical/warning if missing; False → info if missing
#   severity    : "critical" | "warning" | "info"
#   ref         : regulatory reference string
#   desc        : short description of what's missing
#   fix         : actionable suggestion shown to the user

COMPLIANCE_RULES: Dict[str, List[Dict]] = {
    "Clinical Study Protocol": [
        {
            "id": "CSP-001",
            "pattern": r"primary endpoint|primary efficacy endpoint|primary outcome",
            "required": True, "severity": "critical",
            "ref": "ICH E8 §2.2",
            "desc": "Primary endpoint not clearly defined",
            "fix": "Define the primary endpoint with measurement method and timepoint",
        },
        {
            "id": "CSP-002",
            "pattern": r"inclusion criteria|eligibility criteria",
            "required": True, "severity": "critical",
            "ref": "ICH E6 §6.4",
            "desc": "Inclusion criteria section missing",
            "fix": "Add specific, numbered inclusion criteria",
        },
        {
            "id": "CSP-003",
            "pattern": r"exclusion criteria",
            "required": True, "severity": "critical",
            "ref": "ICH E6 §6.4",
            "desc": "Exclusion criteria section missing",
            "fix": "Add specific, numbered exclusion criteria",
        },
        {
            "id": "CSP-004",
            "pattern": r"sample size|statistical power|power calculation",
            "required": True, "severity": "critical",
            "ref": "ICH E9",
            "desc": "Sample size justification absent",
            "fix": "Include sample size calculation with power, effect size, and assumptions",
        },
        {
            "id": "CSP-005",
            "pattern": r"adverse event|SAE|serious adverse event",
            "required": True, "severity": "critical",
            "ref": "ICH E6 §6.8",
            "desc": "Adverse event reporting procedures missing",
            "fix": "Define AE/SAE with CTCAE grading and reporting timelines (24h/7d/15d)",
        },
        {
            "id": "CSP-006",
            "pattern": r"ethics|IRB|IEC|informed consent",
            "required": True, "severity": "warning",
            "ref": "ICH E6 §6.14",
            "desc": "Ethics/IRB reference absent",
            "fix": "Add ethics committee approval pathway and ICF reference",
        },
        {
            "id": "CSP-007",
            "pattern": r"Good Clinical Practice|GCP|ICH E6",
            "required": False, "severity": "info",
            "ref": "ICH E6",
            "desc": "Explicit GCP reference recommended",
            "fix": "Reference ICH E6(R2) Good Clinical Practice guidelines",
        },
        {
            "id": "CSP-008",
            "pattern": r"randomis|randomiz",
            "required": True, "severity": "warning",
            "ref": "ICH E6 §6.5",
            "desc": "Randomisation procedure not described",
            "fix": "Describe randomisation method, stratification, and IWRS/IVRS system",
        },
        {
            "id": "CSP-009",
            "pattern": r"DSMB|DMC|data safety monitoring|data monitoring committee",
            "required": False, "severity": "info",
            "ref": "ICH E6 §5.19",
            "desc": "DSMB/DMC reference recommended for Phase II/III studies",
            "fix": "Include Data Safety Monitoring Board charter reference",
        },
        {
            "id": "CSP-010",
            "pattern": r"stopping rule|discontinuation criteria|withdrawal criteria",
            "required": True, "severity": "warning",
            "ref": "ICH E6 §6.5.3",
            "desc": "Stopping/discontinuation rules not specified",
            "fix": "Define criteria for subject discontinuation and study stopping rules",
        },
    ],

    "Informed Consent Form": [
        {
            "id": "ICF-001",
            "pattern": r"purpose|why.*study|reason.*study|aim.*study",
            "required": True, "severity": "critical",
            "ref": "45 CFR 46.116(b)(1)",
            "desc": "Study purpose not explained in plain language",
            "fix": "Explain the purpose of the research clearly at ≤8th-grade reading level",
        },
        {
            "id": "ICF-002",
            "pattern": r"risk|side effect|discomfort|harm|danger",
            "required": True, "severity": "critical",
            "ref": "45 CFR 46.116(b)(2)",
            "desc": "Risks and discomforts not disclosed",
            "fix": "Disclose all foreseeable risks, including common, uncommon, and serious events",
        },
        {
            "id": "ICF-003",
            "pattern": r"voluntar|withdraw|stop participating|right to refuse",
            "required": True, "severity": "critical",
            "ref": "45 CFR 46.116(b)(8)",
            "desc": "Voluntary participation statement missing",
            "fix": "State that participation is voluntary and the subject may withdraw at any time without penalty",
        },
        {
            "id": "ICF-004",
            "pattern": r"confidential|privacy|data protection|identif",
            "required": True, "severity": "critical",
            "ref": "45 CFR 46.116(b)(5)",
            "desc": "Confidentiality provisions absent",
            "fix": "Describe how participant data will be protected and who may access it",
        },
        {
            "id": "ICF-005",
            "pattern": r"contact|question|problem|phone|call",
            "required": True, "severity": "warning",
            "ref": "45 CFR 46.116(b)(7)",
            "desc": "Contact information missing",
            "fix": "Provide contact details for study questions, injuries, and emergency situations",
        },
        {
            "id": "ICF-006",
            "pattern": r"benefit|potential benefit",
            "required": True, "severity": "warning",
            "ref": "45 CFR 46.116(b)(3)",
            "desc": "Benefits not described",
            "fix": "Describe potential benefits, or explicitly state no direct benefit is expected",
        },
        {
            "id": "ICF-007",
            "pattern": r"alternative|other treatment|standard of care",
            "required": True, "severity": "warning",
            "ref": "45 CFR 46.116(b)(4)",
            "desc": "Alternative treatments not mentioned",
            "fix": "Describe appropriate alternative procedures or treatments available outside the trial",
        },
    ],

    "Clinical Study Report": [
        {
            "id": "CSR-001",
            "pattern": r"synopsis|summary",
            "required": True, "severity": "critical",
            "ref": "ICH E3 §2",
            "desc": "Synopsis section missing (mandatory per ICH E3)",
            "fix": "Add a comprehensive synopsis per ICH E3 format (~2 pages)",
        },
        {
            "id": "CSR-002",
            "pattern": r"efficacy|effectiveness|primary endpoint result|treatment effect",
            "required": True, "severity": "critical",
            "ref": "ICH E3 §11",
            "desc": "Efficacy results section absent",
            "fix": "Include primary and secondary efficacy analysis results with statistics (p-value, 95%CI)",
        },
        {
            "id": "CSR-003",
            "pattern": r"adverse event|safety|tolerability",
            "required": True, "severity": "critical",
            "ref": "ICH E3 §12",
            "desc": "Safety results section absent",
            "fix": "Include adverse events, laboratory results, vital signs, and other safety data",
        },
        {
            "id": "CSR-004",
            "pattern": r"patient disposition|subject disposition",
            "required": True, "severity": "warning",
            "ref": "ICH E3 §10",
            "desc": "Patient disposition section missing",
            "fix": "Add patient disposition with reasons for discontinuation and completion rates",
        },
        {
            "id": "CSR-005",
            "pattern": r"conclusion|overall conclusion|benefit.risk",
            "required": True, "severity": "warning",
            "ref": "ICH E3 §15",
            "desc": "Conclusions section absent",
            "fix": "Add overall conclusions including benefit-risk assessment",
        },
    ],

    "Statistical Analysis Plan": [
        {
            "id": "SAP-001",
            "pattern": r"intent.to.treat|ITT|per.protocol|PP|safety population",
            "required": True, "severity": "critical",
            "ref": "ICH E9 §5.2",
            "desc": "Analysis populations not defined",
            "fix": "Define ITT, PP, and Safety populations with clear inclusion criteria",
        },
        {
            "id": "SAP-002",
            "pattern": r"primary analysis|primary endpoint analysis|statistical test",
            "required": True, "severity": "critical",
            "ref": "ICH E9 §5.5",
            "desc": "Primary analysis method not pre-specified",
            "fix": "Pre-specify primary statistical test, model, covariates, and alpha level",
        },
        {
            "id": "SAP-003",
            "pattern": r"missing data|imputation|LOCF|MAR|MCAR|MNAR",
            "required": True, "severity": "warning",
            "ref": "ICH E9(R1)",
            "desc": "Missing data handling strategy absent",
            "fix": "Specify primary and sensitivity missing data strategies per ICH E9(R1) estimand framework",
        },
        {
            "id": "SAP-004",
            "pattern": r"interim analysis|alpha.spending|O.Brien|Pocock",
            "required": False, "severity": "info",
            "ref": "ICH E9 §4.5",
            "desc": "Interim analysis plan not included (required if planned)",
            "fix": "If interim analyses are planned, specify stopping boundaries and alpha-spending function",
        },
        {
            "id": "SAP-005",
            "pattern": r"multiplicity|hierarchical|Bonferroni|Holm|family.wise",
            "required": True, "severity": "warning",
            "ref": "ICH E9 §5.7",
            "desc": "Multiplicity adjustment strategy absent",
            "fix": "Specify how multiple endpoints will be handled to control family-wise type I error",
        },
        {
            "id": "SAP-006",
            "pattern": r"sensitivity analysis|sensitivity|robustness",
            "required": False, "severity": "info",
            "ref": "ICH E9 §5.3",
            "desc": "Sensitivity analyses not described",
            "fix": "Pre-specify sensitivity analyses to assess robustness of primary analysis",
        },
    ],

    "Investigator Brochure": [
        {
            "id": "IB-001",
            "pattern": r"pharmacokinetic|PK|absorption|distribution|metabolism|elimination",
            "required": True, "severity": "critical",
            "ref": "ICH E6 §7.3",
            "desc": "Pharmacokinetic data not included",
            "fix": "Include summary of PK data from preclinical and clinical studies",
        },
        {
            "id": "IB-002",
            "pattern": r"toxicology|preclinical|non.clinical|animal stud",
            "required": True, "severity": "critical",
            "ref": "ICH E6 §7.2",
            "desc": "Non-clinical study summary missing",
            "fix": "Include summary of preclinical pharmacology and toxicology studies",
        },
    ],
}


# ── Required section IDs per document type ────────────────────────────────────
REQUIRED_SECTION_IDS: Dict[str, List[str]] = {
    "Clinical Study Protocol": [
        "intro", "study_design", "objectives", "population",
        "treatment", "safety", "statistics", "ethics",
    ],
    "Informed Consent Form": [
        "purpose", "procedures", "risks", "benefits",
        "confidentiality", "voluntary",
    ],
    "Clinical Study Report": [
        "synopsis", "introduction", "study_design",
        "patient_disposition", "efficacy", "safety",
        "discussion", "conclusions",
    ],
    "Statistical Analysis Plan": [
        "objectives", "populations", "sample_size",
        "primary_analysis", "safety_analysis", "missing_data",
    ],
    "Investigator Brochure": [
        "summary", "introduction", "physicochemical",
        "nonclinical", "clinical_pks", "safety_summary",
    ],
}


# ── Guidelines checked per document type (shown in compliance report) ─────────
GUIDELINES_PER_TYPE: Dict[str, List[str]] = {
    "Clinical Study Protocol":  ["ICH E6(R2)", "ICH E8", "FDA 21 CFR 312", "GCP"],
    "Informed Consent Form":    ["ICH E6", "45 CFR 46", "FDA 21 CFR 50", "GDPR/HIPAA"],
    "Clinical Study Report":    ["ICH E3", "EMA Module 5"],
    "Statistical Analysis Plan":["ICH E9", "ICH E9(R1)", "FDA Statistical Guidance"],
    "Investigator Brochure":    ["ICH E6 §7", "FDA Guidance IB"],
}


# ── Clinical entity patterns for NER (regex) ─────────────────────────────────
ENTITY_PATTERNS: Dict[str, List[str]] = {
    "Adverse Events": [
        r"\b(adverse event|AE|SAE|serious adverse event|SUSAR|adverse reaction|ADR|CTCAE)\b",
        r"\b(toxicity|side effect|complication)\b",
    ],
    "Endpoints": [
        r"\b(overall survival|OS|progression.free survival|PFS|objective response rate|ORR)\b",
        r"\b(disease.free survival|DFS|complete response|CR|partial response|PR)\b",
        r"\b(HbA1c|blood pressure|LDL|ejection fraction|LVEF|CDR.SB|MMSE|ACR20)\b",
        r"\b(quality of life|QoL|patient.reported outcome|PRO|EQ.5D)\b",
    ],
    "Drug Terms": [
        r"\b(investigational product|IP|study drug|test article)\b",
        r"\b(placebo|comparator|active control|reference drug)\b",
        r"\b(\d+(\.\d+)?\s*(mg|g|mcg|μg|mg/kg|mg/m2|IU|mL))\b",
    ],
    "Regulatory Terms": [
        r"\b(ICH E6|ICH E3|ICH E8|ICH E9|ICH E10|ICH E2A)\b",
        r"\b(FDA|EMA|GCP|GMP|IND|NDA|BLA|MAA|PMDA)\b",
        r"\b(IRB|IEC|ethics committee|institutional review board)\b",
        r"\b(informed consent|ICF|HIPAA|GDPR)\b",
    ],
    "Statistical Terms": [
        r"\b(intent.to.treat|ITT|per.protocol|PP|modified ITT|mITT)\b",
        r"\b(p.value|p=|p<|confidence interval|CI|hazard ratio|HR|odds ratio|OR)\b",
        r"\b(randomis|randomiz|stratif|blinding|double.blind|open.label)\b",
        r"\b(sample size|statistical power|alpha|type I error|type II error)\b",
    ],
    "Safety Terms": [
        r"\b(DSMB|DMC|data monitoring committee|data safety monitoring)\b",
        r"\b(stopping rule|dose.limiting toxicity|DLT|maximum tolerated dose|MTD)\b",
        r"\b(ARIA|vital signs|ECG|electrocardiogram|QTcF)\b",
    ],
}
