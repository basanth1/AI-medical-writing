from typing import Dict, List, Tuple
STRUCTURE_PATTERNS: List[str] = [
    r"\b(inclusion criteria|exclusion criteria)\b",
    r"\b(primary endpoint|secondary endpoint)\b",
    r"\b(randomis|randomiz)\b",
    r"\b(ICH E\d|FDA|EMA|GCP|CTCAE)\b",
    r"\b(adverse event|SAE|DSMB|DMC)\b",
    r"\b(sample size|statistical power|hazard ratio|p.value|confidence interval)\b",
    r"\b(informed consent|IRB|IEC|ethics committee)\b",
    r"\b(dose|dosage|mg|QD|BID|once.daily|twice.daily)\b",
]


UNCERTAINTY_PHRASES: List[str] = [
    r"\b(i (am not sure|cannot|can't|don't know))\b",
    r"\b(i am unable to)\b",
    r"\b(i cannot provide|i can't provide)\b",
    r"\b(as an ai|as a language model|as an llm)\b",
    r"\b(hallucin|made.?up|fabricat)\b",
    r"\b(placeholder|insert here|tbd|to be determined|fill in)\b",
    r"\[template content\]",
    r"\[generation failed",
    r"\[template —",
]



SECTION_COVERAGE: dict[str, List[str]] = {
    "intro": [
        r"\b(unmet medical need|disease burden|rationale)\b",
        r"\b(mechanism of action|preclinical|clinical evidence)\b",
    ],
    "study_design": [
        r"\b(randomis|randomiz|double.blind|placebo.controlled)\b",
        r"\b(stratif|stratification|IWRS|IVRS)\b",
    ],
    "objectives": [
        r"\b(primary (endpoint|objective|outcome))\b",
        r"\b(secondary (endpoint|objective))\b",
    ],
    "population": [
        r"\b(inclusion criteria)\b",
        r"\b(exclusion criteria)\b",
        r"\b(ECOG|Karnofsky|performance status)\b",
    ],
    "treatment": [
        r"\b(dose|dosage|mg)\b",
        r"\b(dose (modification|reduction|escalation))\b",
    ],
    "safety": [
        r"\b(adverse event|AE|SAE)\b",
        r"\b(CTCAE|DSMB|DMC|stopping rule)\b",
    ],
    "statistics": [
        r"\b(sample size|statistical power)\b",
        r"\b(intent.to.treat|ITT|per.protocol|PP)\b",
        r"\b(alpha|p.value|confidence interval)\b",
    ],
    "ethics": [
        r"\b(ethics committee|IRB|IEC|informed consent)\b",
        r"\b(Helsinki|GCP|ICH E6)\b",
    ],
    "synopsis": [
        r"\b(primary endpoint|primary outcome)\b",
        r"\b(safety|adverse event)\b",
    ],
    "efficacy": [
        r"\b(p.value|p=|p<|confidence interval|hazard ratio)\b",
        r"\b(primary endpoint|overall survival|progression.free)\b",
    ],
    "primary_analysis": [
        r"\b(ITT|intent.to.treat)\b",
        r"\b(alpha|type I error|two.sided)\b",
    ],
    "missing_data": [
        r"\b(missing data|imputation)\b",
        r"\b(MAR|MNAR|MCAR|multiple imputation)\b",
    ],
}
