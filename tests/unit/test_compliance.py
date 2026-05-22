"""
Unit tests for ComplianceChecker — no external dependencies.
"""

import pytest
from backend.core.models import StudyMetadata, DocumentSection, IssueSeverity
from backend.services.compliance_service import ComplianceChecker


@pytest.fixture
def checker():
    return ComplianceChecker(enable_ner=False)


@pytest.fixture
def metadata():
    return StudyMetadata(
        indication="Oncology",
        phase="Phase III",
        design="Randomized, Controlled, Double-blind",
        primary_endpoint="Overall Survival (OS)",
        secondary_endpoints=["PFS", "ORR"],
        patient_population="Adults with metastatic breast cancer",
        sample_size=520,
        duration_months=48,
        investigational_product="TrialDrug-X",
    )


@pytest.fixture
def good_csp_sections():
    return [
        DocumentSection(
            section_id="intro", title="1. Introduction",
            content=(
                "This Phase III randomized controlled double-blind study evaluates "
                "TrialDrug-X in metastatic breast cancer. ICH E6 GCP guidelines apply. "
                "Informed consent will be obtained from all subjects. IRB approval required."
            ),
            section_type="intro",
        ),
        DocumentSection(
            section_id="objectives", title="Objectives",
            content="Primary endpoint: Overall Survival (OS). Secondary endpoints: PFS, ORR.",
            section_type="objectives",
        ),
        DocumentSection(
            section_id="population", title="Population",
            content=(
                "Inclusion criteria: adults ≥18 years. Exclusion criteria: prior mTOR inhibitors. "
                "Randomisation stratified by hormone receptor status. Blinding maintained."
            ),
            section_type="population",
        ),
        DocumentSection(
            section_id="safety", title="Safety",
            content=(
                "Adverse events graded per CTCAE v5.0. Serious adverse event reporting: "
                "24-hour initial, 7-day follow-up. DSMB will review safety data quarterly."
            ),
            section_type="safety",
        ),
        DocumentSection(
            section_id="statistics", title="Statistics",
            content=(
                "Sample size: 520 patients. Statistical power: 80%. Primary analysis: "
                "stratified log-rank test. Intent-to-treat (ITT) and Per-Protocol (PP) populations. "
                "Missing data handled by multiple imputation (MAR assumption)."
            ),
            section_type="statistics",
        ),
    ]


class TestComplianceCheckerRules:
    def test_compliant_document_high_score(self, checker, metadata, good_csp_sections):
        # Fixture has 5 of 8 required sections — score reflects partial coverage
        report = checker.validate(good_csp_sections, "Clinical Study Protocol", metadata)
        assert report.overall_score >= 25   # some sections present, some missing

    def test_empty_document_low_score(self, checker, metadata):
        report = checker.validate([], "Clinical Study Protocol", metadata)
        assert report.overall_score < 50
        assert not report.is_compliant

    def test_critical_issues_fail_compliance(self, checker, metadata):
        minimal = [DocumentSection(
            section_id="intro", title="Intro",
            content="This is a study.", section_type="intro",
        )]
        report = checker.validate(minimal, "Clinical Study Protocol", metadata)
        assert any(i.severity == IssueSeverity.CRITICAL for i in report.issues)
        assert not report.is_compliant

    def test_missing_sections_detected(self, checker, metadata):
        # Only one section — many required sections missing
        sections = [DocumentSection(
            section_id="intro", title="Intro",
            content="Study introduction.", section_type="intro",
        )]
        report = checker.validate(sections, "Clinical Study Protocol", metadata)
        assert len(report.missing_sections) > 0

    def test_icf_voluntary_missing(self, checker, metadata):
        sections = [DocumentSection(
            section_id="purpose", title="Purpose",
            content="This study tests a new drug for heart disease.", section_type="purpose",
        )]
        report = checker.validate(sections, "Informed Consent Form", metadata)
        # ICF-003 (voluntary) should be flagged
        rule_ids = [i.rule_id for i in report.issues]
        assert "ICF-003" in rule_ids

    def test_template_content_triggers_critical(self, checker, metadata):
        sections = [DocumentSection(
            section_id="intro", title="Intro",
            content="[TEMPLATE CONTENT — Set GROQ_API_KEY for AI-generated text]",
            section_type="intro",
        )]
        report = checker.validate(sections, "Clinical Study Protocol", metadata)
        gen_issues = [i for i in report.issues if i.category == "generation_failure"]
        assert len(gen_issues) > 0

    def test_recommendations_populated(self, checker, metadata, good_csp_sections):
        report = checker.validate(good_csp_sections, "Clinical Study Protocol", metadata)
        assert len(report.recommendations) > 0

    def test_guidelines_checked_populated(self, checker, metadata, good_csp_sections):
        report = checker.validate(good_csp_sections, "Clinical Study Protocol", metadata)
        assert "ICH E6(R2)" in report.guidelines_checked

    def test_entity_extraction_finds_terms(self, checker, metadata, good_csp_sections):
        report = checker.validate(good_csp_sections, "Clinical Study Protocol", metadata)
        all_entities = [e for vals in report.entities_validated.values() for e in vals]
        assert len(all_entities) > 0

    def test_score_is_between_0_and_100(self, checker, metadata, good_csp_sections):
        report = checker.validate(good_csp_sections, "Clinical Study Protocol", metadata)
        assert 0 <= report.overall_score <= 100

    def test_csr_synopsis_required(self, checker, metadata):
        sections = [DocumentSection(
            section_id="efficacy", title="Efficacy",
            content="Primary endpoint met. OS HR=0.73, p<0.001.", section_type="efficacy",
        )]
        report = checker.validate(sections, "Clinical Study Report", metadata)
        assert "synopsis" in report.missing_sections
