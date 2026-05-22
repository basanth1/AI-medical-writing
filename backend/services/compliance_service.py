"""
Compliance Checker Service — regulatory rule validation + entity NER.
All rules, patterns, and section lists loaded from backend/data/compliance_rules.py.
"""
from __future__ import annotations
import re, logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone

from backend.core.models import (
    StudyMetadata, DocumentSection,
    ComplianceReport, ComplianceIssue, IssueSeverity,
)
from backend.data.compliance_rules import (
    COMPLIANCE_RULES, REQUIRED_SECTION_IDS,
    GUIDELINES_PER_TYPE, ENTITY_PATTERNS,
)

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """
    Validates clinical trial documents against regulatory rules.
    Rules come from backend/data/compliance_rules.py — no code changes needed
    to add/modify a rule.
    """

    def __init__(self, enable_ner: bool = True):
        self._ner = None
        if enable_ner:
            self._try_load_ner()

    def _try_load_ner(self):
        try:
            from transformers import pipeline
            self._ner = pipeline("ner", model="d4data/biomedical-ner-all",
                                  aggregation_strategy="simple")
            logger.info("BioBERT NER loaded")
        except Exception:
            logger.info("BioBERT NER unavailable — using regex entity extraction")

    # ── Public ────────────────────────────────────────────────────────────────

    def validate(self, sections: List[DocumentSection],
                 document_type: str, metadata: StudyMetadata) -> ComplianceReport:
        full_text = " ".join(s.content for s in sections)
        missing, sec_issues = self._check_sections(sections, document_type)
        reg_issues           = self._check_rules(full_text, document_type)
        quality_issues       = self._check_quality(sections)
        all_issues           = sec_issues + reg_issues + quality_issues
        entities             = self._extract_entities(full_text)
        score                = self._score(all_issues)
        compliant            = score >= 70 and not any(
                                 i.severity == IssueSeverity.CRITICAL for i in all_issues)
        return ComplianceReport(
            overall_score      = round(score, 1),
            is_compliant       = compliant,
            issues             = all_issues,
            guidelines_checked = GUIDELINES_PER_TYPE.get(document_type, ["ICH E6"]),
            entities_validated = entities,
            missing_sections   = missing,
            recommendations    = self._recommendations(all_issues, document_type, metadata),
            checked_at         = datetime.now(timezone.utc).isoformat(),
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _check_sections(self, sections: List[DocumentSection],
                         doc_type: str) -> Tuple[List[str], List[ComplianceIssue]]:
        required = REQUIRED_SECTION_IDS.get(doc_type, [])
        present  = {s.section_id for s in sections}
        missing  = [r for r in required if r not in present]
        issues   = [ComplianceIssue(
            severity=IssueSeverity.CRITICAL, category="missing_section",
            description=f"Required section '{m}' is missing",
            suggestion=f"Add the '{m}' section for {doc_type} compliance",
            regulatory_ref="ICH E6/E3",
        ) for m in missing]
        return missing, issues

    def _check_rules(self, full_text: str, doc_type: str) -> List[ComplianceIssue]:
        rules  = COMPLIANCE_RULES.get(doc_type, [])
        issues = []
        for rule in rules:
            found = bool(re.search(rule["pattern"], full_text, re.IGNORECASE))
            if rule["required"] and not found:
                issues.append(ComplianceIssue(
                    severity=IssueSeverity(rule["severity"]), category="regulatory",
                    rule_id=rule["id"],
                    description=f"[{rule['id']}] {rule['desc']}",
                    suggestion=rule["fix"], regulatory_ref=rule["ref"],
                ))
            elif not rule["required"] and not found:
                issues.append(ComplianceIssue(
                    severity=IssueSeverity.INFO, category="regulatory",
                    rule_id=rule["id"],
                    description=f"[{rule['id']}] Recommended: {rule['desc']}",
                    suggestion=rule["fix"], regulatory_ref=rule["ref"],
                ))
        return issues

    def _check_quality(self, sections: List[DocumentSection]) -> List[ComplianceIssue]:
        issues = []
        for s in sections:
            if "[TEMPLATE CONTENT" in s.content or "[Generation failed" in s.content:
                issues.append(ComplianceIssue(
                    severity=IssueSeverity.CRITICAL, category="generation_failure",
                    section_id=s.section_id,
                    description=f"Section '{s.title}' contains template/fallback content",
                    suggestion="Set GROQ_API_KEY and regenerate this section",
                ))
            elif s.word_count < 80:
                issues.append(ComplianceIssue(
                    severity=IssueSeverity.WARNING, category="formatting",
                    section_id=s.section_id,
                    description=f"Section '{s.title}' is too brief ({s.word_count} words)",
                    suggestion="Expand with more specific regulatory and clinical detail",
                ))
            if "[SAMPLE_SIZE]" in s.content or "[HR]" in s.content or "[p-VALUE]" in s.content:
                issues.append(ComplianceIssue(
                    severity=IssueSeverity.WARNING, category="placeholders",
                    section_id=s.section_id,
                    description=f"Section '{s.title}' contains unresolved placeholders",
                    suggestion="Replace all bracketed placeholders with actual study values",
                ))
        return issues

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities: Dict[str, List[str]] = {}
        if self._ner:
            try:
                for ent in self._ner(text[:512]):
                    label = ent.get("entity_group", ent.get("entity", "OTHER"))
                    word  = ent.get("word", "")
                    entities.setdefault(label, [])
                    if word not in entities[label]:
                        entities[label].append(word)
            except Exception:
                pass
        for etype, patterns in ENTITY_PATTERNS.items():
            found = []
            for pat in patterns:
                found += re.findall(pat, text, re.IGNORECASE)
            flat = [f[0] if isinstance(f, tuple) else f for f in found]
            if flat:
                entities[etype] = list(dict.fromkeys(flat))[:8]
        return entities

    @staticmethod
    def _score(issues: List[ComplianceIssue]) -> float:
        deductions = {IssueSeverity.CRITICAL: 15.0, IssueSeverity.WARNING: 5.0, IssueSeverity.INFO: 1.0}
        return max(0.0, 100.0 - sum(deductions.get(i.severity, 0) for i in issues))

    @staticmethod
    def _recommendations(issues: List[ComplianceIssue],
                          doc_type: str, metadata: StudyMetadata) -> List[str]:
        recs = []
        crits = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        warns = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)
        if crits: recs.append(f"PRIORITY: Resolve {crits} critical issue(s) before regulatory submission")
        if warns: recs.append(f"Address {warns} warning(s) to improve document quality")
        if "Phase I" in metadata.phase:
            recs.append("Ensure FIH dose escalation rules comply with FDA Guidance (2010)")
        if "Phase III" in metadata.phase:
            recs.append("Verify primary endpoint pre-specification per FDA 21 CFR 314.126 (AWC)")
        if doc_type == "Informed Consent Form":
            recs.append("Confirm readability ≤8th grade (Flesch-Kincaid score ≥60)")
            recs.append("Obtain patient advocate review before IRB/IEC submission")
        recs += [
            "Have document reviewed by a qualified medical writer and biostatistician",
            "Run final internal QC checklist before sponsor sign-off",
        ]
        return recs
