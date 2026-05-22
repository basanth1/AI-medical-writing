"""
Integration tests for the full document generation pipeline.
Mocks the Groq API — no real network calls.
"""

import pytest
from types import SimpleNamespace
from backend.core.models import StudyMetadata, DocumentRequest
from backend.services.rag_service import RAGPipeline
from backend.services.generation_service import DocumentGenerator
from backend.services.compliance_service import ComplianceChecker


MOCK_GROQ_RESPONSE = (
    "This Phase III randomized, double-blind, placebo-controlled study evaluates "
    "the efficacy and safety of TrialDrug-X 150 mg in patients with HER2-positive "
    "metastatic breast cancer. The study is conducted in accordance with ICH E6(R2) "
    "Good Clinical Practice guidelines. Primary endpoint: Overall Survival (OS). "
    "Inclusion criteria: adults ≥18 years, ECOG 0-1, measurable disease per RECIST v1.1. "
    "Exclusion criteria: prior PI3K/AKT/mTOR inhibitors, untreated CNS metastases. "
    "Adverse events graded per CTCAE v5.0. SAE reporting: 24-hour initial notification. "
    "Sample size: 520 patients, 80% power, HR=0.73, alpha=0.05. "
    "Intent-to-treat (ITT) population is the primary analysis set. "
    "Randomisation stratified by prior lines and hormone receptor status. "
    "Ethics committee approval required before study initiation. "
    "Informed consent obtained from all participants. IRB review mandatory."
)


@pytest.fixture
def mock_llm_client():
    class MockLLMClient:
        def __init__(self, available=True):
            self.available = available
            self._ollama = SimpleNamespace(model="mock-ollama")
            self._groq = SimpleNamespace(model_name="mock-groq")

        def status(self):
            return {
                "ollama": {"available": self.available, "model": "mock-ollama", "host": "mock"},
                "groq": {"available": False, "fallback_model": "mock-groq"},
                "active_generator": "ollama" if self.available else "template",
            }

        def is_available(self):
            return self.available

        def generate_scored(self, section_id, prompt, *, system="", allow_groq=True):
            breakdown = SimpleNamespace(word_count=len(MOCK_GROQ_RESPONSE.split()))
            return MOCK_GROQ_RESPONSE, 0.92, breakdown

        def generate_with_system(self, system, prompt):
            return MOCK_GROQ_RESPONSE

    return MockLLMClient()


@pytest.fixture
def fallback_llm_client():
    class FallbackLLMClient:
        _ollama = SimpleNamespace(model="mock-ollama")
        _groq = SimpleNamespace(model_name="mock-groq")

        def status(self):
            return {
                "ollama": {"available": False, "model": "mock-ollama", "host": "mock"},
                "groq": {"available": False, "fallback_model": "mock-groq"},
                "active_generator": "template",
            }

        def is_available(self):
            return False

        def generate_scored(self, section_id, prompt, *, system="", allow_groq=True):
            text = "[TEMPLATE CONTENT] Offline generated section for testing."
            breakdown = SimpleNamespace(word_count=len(text.split()))
            return text, 0.0, breakdown

        def generate_with_system(self, system, prompt):
            return "[TEMPLATE CONTENT] Offline generated section for testing."

    return FallbackLLMClient()


@pytest.fixture
def rag():
    return RAGPipeline(vector_dim=384)


@pytest.fixture
def metadata():
    return StudyMetadata(
        indication="Oncology",
        phase="Phase III",
        design="Randomized, Controlled, Double-blind",
        primary_endpoint="Overall Survival (OS)",
        secondary_endpoints=["Progression-Free Survival", "ORR"],
        patient_population="Adults with HER2-positive metastatic breast cancer",
        sample_size=520,
        duration_months=48,
        investigational_product="TrialDrug-X 150mg",
        sponsor="PharmaCo Inc.",
        therapeutic_area="Oncology",
    )


class TestRAGPipeline:
    def test_builtin_docs_loaded(self, rag):
        stats = rag.stats()
        assert stats["sample_documents_loaded"] >= 4

    def test_retrieve_returns_results(self, rag):
        results = rag.retrieve("Phase III Oncology breast cancer overall survival", top_k=3)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_retrieve_result_structure(self, rag):
        results = rag.retrieve("Phase III Oncology", top_k=1)
        assert "content" in results[0]
        assert "metadata" in results[0]
        assert "score" in results[0]

    def test_ingest_and_retrieve(self, rag):
        doc_id = rag.ingest(
            "Novel Phase II study in non-small cell lung cancer using pembrolizumab. "
            "Primary endpoint: Progression-Free Survival. Double-blind randomized design.",
            metadata={"doc_type": "test", "indication": "Oncology"}
        )
        assert doc_id is not None
        results = rag.retrieve("pembrolizumab lung cancer", top_k=3)
        assert any("lung cancer" in r["content"].lower() or
                   "pembrolizumab" in r["content"].lower() for r in results)

    def test_guidelines_returned(self, rag):
        guidelines = rag.get_guidelines("Clinical Study Protocol", "Phase III")
        assert "ICH" in guidelines
        assert len(guidelines) > 100

    def test_stats_structure(self, rag):
        stats = rag.stats()
        required_keys = {"retriever_type", "total_documents", "total_chunks",
                         "index_size", "sample_documents_loaded"}
        assert required_keys.issubset(stats.keys())


class TestDocumentGeneratorIntegration:
    @pytest.mark.asyncio
    async def test_generate_returns_sections(self, mock_llm_client, rag, metadata):
        generator = DocumentGenerator(client=mock_llm_client)
        retrieved = rag.retrieve(metadata.to_query_text(), top_k=3)
        guidelines = rag.get_guidelines("Clinical Study Protocol", metadata.phase)

        sections = await generator.generate(
            metadata=metadata,
            document_type="Clinical Study Protocol",
            retrieved_docs=retrieved,
            guidelines=guidelines,
        )
        assert isinstance(sections, list)
        assert len(sections) > 0
        assert all(hasattr(s, "section_id") for s in sections)
        assert all(hasattr(s, "content") for s in sections)
        assert all(s.word_count > 0 for s in sections)

    @pytest.mark.asyncio
    async def test_rag_enrich_runs(self, mock_llm_client, rag, metadata):
        generator = DocumentGenerator(client=mock_llm_client)
        retrieved = rag.retrieve(metadata.to_query_text(), top_k=3)
        guidelines = rag.get_guidelines("Clinical Study Protocol")

        sections = await generator.generate(
            metadata=metadata,
            document_type="Clinical Study Protocol",
            retrieved_docs=retrieved,
            guidelines=guidelines,
        )
        enriched = await generator.rag_enrich(sections, rag, metadata)
        assert len(enriched) == len(sections)

    @pytest.mark.asyncio
    async def test_fallback_client_still_generates(self, fallback_llm_client, rag, metadata):
        generator = DocumentGenerator(client=fallback_llm_client)
        retrieved = rag.retrieve(metadata.to_query_text(), top_k=3)

        sections = await generator.generate(
            metadata=metadata,
            document_type="Informed Consent Form",
            retrieved_docs=retrieved,
            guidelines="",
        )
        assert len(sections) > 0
        assert all(isinstance(s.content, str) for s in sections)


class TestFullPipeline:
    @pytest.mark.asyncio
    async def test_generate_then_validate(self, mock_llm_client, rag, metadata):
        generator = DocumentGenerator(client=mock_llm_client)
        checker   = ComplianceChecker(enable_ner=False)

        retrieved  = rag.retrieve(metadata.to_query_text(), top_k=5)
        guidelines = rag.get_guidelines("Clinical Study Protocol", metadata.phase)

        sections = await generator.generate(
            metadata=metadata,
            document_type="Clinical Study Protocol",
            retrieved_docs=retrieved,
            guidelines=guidelines,
        )
        sections = await generator.rag_enrich(sections, rag, metadata)
        report   = checker.validate(sections, "Clinical Study Protocol", metadata)

        assert 0 <= report.overall_score <= 100
        assert isinstance(report.is_compliant, bool)
        assert len(report.guidelines_checked) > 0
