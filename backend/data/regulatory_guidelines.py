"""
backend/data/regulatory_guidelines.py
Regulatory guideline text loaded into the FAISS vector store and injected into LLM prompts.
Add or update guidelines here — no service code needs to change.
"""

from typing import Dict

# ── Guidelines injected into LLM prompts per document type ───────────────────
REGULATORY_GUIDELINES: Dict[str, Dict[str, str]] = {
    "Clinical Study Protocol": {
        "ICH E6(R2)": """
ICH E6(R2) Good Clinical Practice — Protocol Requirements:
• Primary and secondary endpoints defined with measurement methods and timepoints.
• Inclusion/exclusion criteria precisely enumerated.
• Investigational product: description, dose, route, regimen, packaging, labelling.
• AE/SAE definitions per CTCAE, reporting timelines (24h/7d/15d), DSMB charter.
• Ethics committee approval and informed consent procedures.
• Statistical methodology per ICH E9. Data management and quality assurance.
""",
        "ICH E8": """
ICH E8 — General Considerations for Clinical Trials:
• Objectives scientifically justified and clinically meaningful.
• Risk-benefit assessment documented for each study phase.
• Sample size adequate with statistical power. Patient population representative.
• Design must be statistically sound (adequate power, controlled comparator).
""",
        "FDA 21 CFR 312": """
FDA 21 CFR Part 312 — IND Protocol Requirements:
• Statement of objectives and purpose.
• Subject selection criteria (inclusion/exclusion).
• Study design including control group rationale.
• Dosage, route, duration.
• Observations and measurements to assess effects.
• Clinical procedures, laboratory tests, and other measures.
""",
    },
    "Informed Consent Form": {
        "ICH E6 §4.8": """
ICH E6 Informed Consent (§4.8):
• Language comprehensible to subject (plain language, ≤8th grade).
• Purpose of trial, investigational nature of treatment.
• Expected duration and all procedures.
• All foreseeable risks and discomforts.
• Reasonably expected benefits (or lack thereof).
• Alternative treatments available outside trial.
• Extent of confidentiality. Compensation in case of injury.
• Voluntary nature, right to withdraw without penalty. Contact information.
""",
        "45 CFR 46": """
45 CFR 46 — Protection of Human Subjects:
• Eight required elements of informed consent.
• HIPAA authorisation language where applicable.
• Re-consent triggers (new risks identified).
• Waiver criteria (risk not increased, research not practicable otherwise).
""",
    },
    "Clinical Study Report": {
        "ICH E3": """
ICH E3 — Structure and Content of Clinical Study Reports:
• Title page: study number, title, phase, investigational product, dates.
• Synopsis (~2 pages) covering all key elements.
• Introduction, study objectives, investigational plan: design, randomisation, blinding.
• Study subjects: disposition, demographics, baseline.
• Efficacy evaluation: primary and secondary analyses, subgroups.
• Safety evaluation: exposure, AEs, deaths, labs, vitals, ECG.
• Discussion and conclusions. Appendices: protocol, SAP, patient data listings.
""",
    },
    "Statistical Analysis Plan": {
        "ICH E9(R1)": """
ICH E9(R1) — Statistical Principles and Estimands:
• Estimand framework: treatment policy, hypothetical, composite strategies.
• Confirmatory vs exploratory analyses pre-specified.
• Sample size justification with power, effect size, SD assumptions.
• Analysis populations: ITT (primary), PP (supportive), Safety.
• Handling intercurrent events and missing data per ICH E9(R1).
• Multiple endpoint multiplicity control (hierarchical, Bonferroni, Holm).
• Interim analysis with alpha spending (O'Brien-Fleming, Pocock).
""",
    },
    "Investigator Brochure": {
        "ICH E6 §7": """
ICH E6 §7 — Investigator's Brochure Requirements:
• Summary of physical, chemical, pharmaceutical properties.
• Non-clinical studies: pharmacology, toxicology, pharmacokinetics.
• Effects in humans: pharmacokinetics, safety, efficacy.
• Summary of data and guidance for investigator.
• Updated at least annually or when new significant data available.
""",
    },
}

# ── Phase-specific addendum guidelines ───────────────────────────────────────
PHASE_GUIDELINES: Dict[str, str] = {
    "Phase I": """
=== Phase I Specific Guidelines ===
• First-in-human studies require enhanced safety monitoring.
• Starting dose must be justified from preclinical NOAEL/HNSTD data.
• Dose escalation design (3+3, mTPI, BOIN) must be pre-specified.
• DSMB/DMC oversight mandatory; PK sampling schedule detailed.
• No efficacy claims; safety/tolerability/PK are primary objectives.
• FDA Guidance for Industry: Estimating the Maximum Safe Starting Dose (2005).
""",
    "Phase Ib": """
=== Phase Ib / Dose-Expansion Guidelines ===
• Dose confirmed from Phase Ia; focus on PK/PD in target population.
• Expansion cohorts require pre-specified eligibility and endpoints.
• Biomarker-selected populations must have validated assay.
""",
    "Phase II": """
=== Phase II Specific Guidelines ===
• Proof-of-concept or dose-finding; signal detection focus.
• Sample size may be smaller; exploratory endpoints acceptable.
• Pre-specify primary endpoint for regulatory alignment.
• Adaptive designs encouraged (response-adaptive, seamless Phase II/III).
""",
    "Phase III": """
=== Phase III Specific Guidelines ===
• Confirmatory design per FDA 21 CFR 314.126 (adequate and well-controlled).
• Pre-specified primary + secondary hypotheses with alpha control.
• Interim analysis plan with pre-specified stopping boundaries.
• Consider pre-submission Type B meeting with FDA / Scientific Advice with EMA.
""",
    "Phase IV": """
=== Phase IV / Post-Marketing Guidelines ===
• Post-marketing commitment or requirement from approval.
• Long-term safety follow-up, real-world effectiveness.
• REMS requirements if applicable.
• Pharmacovigilance plan integrated with study design.
""",
}


def get_guidelines(doc_type: str, phase: str = "") -> str:
    """Return combined guideline text for a document type and study phase."""
    base = REGULATORY_GUIDELINES.get(doc_type, {})
    parts = [f"=== {name} ===\n{body.strip()}" for name, body in base.items()]

    for phase_key, phase_text in PHASE_GUIDELINES.items():
        if phase_key in phase:
            parts.append(phase_text.strip())
            break

    return "\n\n".join(parts) if parts else "Standard GCP guidelines apply."
