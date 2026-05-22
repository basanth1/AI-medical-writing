#!/usr/bin/env python3
"""
CLI — generate a clinical trial document from the command line.

Usage:
    python scripts/generate_cli.py \
        --indication Oncology \
        --phase "Phase III" \
        --design "Randomized, Controlled, Double-blind" \
        --endpoint "Overall Survival (OS)" \
        --population "Adults with metastatic breast cancer" \
        --doc-type "Clinical Study Protocol" \
        --output ./output/protocol.md
"""
import argparse, asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.groq_client import GroqClient
from backend.core.models import StudyMetadata
from backend.services.rag_service import RAGPipeline
from backend.services.generation_service import DocumentGenerator
from backend.services.compliance_service import ComplianceChecker
from backend.utils.helpers import document_to_markdown


def parse_args():
    p = argparse.ArgumentParser(description="Generate a clinical trial document using Groq + RAG")
    p.add_argument("--indication",  required=True)
    p.add_argument("--phase",       required=True)
    p.add_argument("--design",      required=True)
    p.add_argument("--endpoint",    required=True)
    p.add_argument("--population",  required=True)
    p.add_argument("--doc-type",    default="Clinical Study Protocol",
                   choices=["Clinical Study Protocol","Informed Consent Form","Clinical Study Report","Statistical Analysis Plan"])
    p.add_argument("--drug",        default=None)
    p.add_argument("--sponsor",     default=None)
    p.add_argument("--sample-size", type=int, default=None)
    p.add_argument("--duration",    type=int, default=None)
    p.add_argument("--output",      default="./generated_document.md")
    p.add_argument("--model",       default="medical", choices=["fast","default","medical"])
    p.add_argument("--top-k",       type=int, default=5)
    p.add_argument("--api-key",     default=None)
    return p.parse_args()


async def run(args):
    print(f"\n{'='*60}\n  Clinical Trial Document Generator — CLI\n{'='*60}")
    print(f"  Document : {args.doc_type}")
    print(f"  Phase    : {args.phase}\n")

    metadata = StudyMetadata(
        indication=args.indication, phase=args.phase, design=args.design,
        primary_endpoint=args.endpoint, patient_population=args.population,
        investigational_product=args.drug, sponsor=args.sponsor,
        sample_size=args.sample_size, duration_months=args.duration,
    )
    api_key = args.api_key or os.environ.get("GROQ_API_KEY","")
    client  = GroqClient(api_key=api_key, model=args.model)
    rag     = RAGPipeline()
    gen     = DocumentGenerator(client=client)
    checker = ComplianceChecker(enable_ner=False)

    status = "✓ Groq connected" if client.is_available() else "⚠ Template fallback (no GROQ_API_KEY)"
    print(f"[→] {status}")
    print(f"[→] Retrieving top-{args.top_k} documents from FAISS…")
    retrieved  = rag.retrieve(metadata.to_query_text(), top_k=args.top_k)
    guidelines = rag.get_guidelines(args.doc_type, args.phase)
    print(f"    {len(retrieved)} chunks retrieved")
    print(f"[→] Generating {args.doc_type} sections…")
    sections = await gen.generate(metadata=metadata, document_type=args.doc_type,
                                   retrieved_docs=retrieved, guidelines=guidelines)
    print(f"    {len(sections)} sections, {sum(s.word_count for s in sections):,} words")
    print(f"[→] RAG enrichment loop…")
    sections = await gen.rag_enrich(sections, rag, metadata)
    print(f"[→] Compliance check…")
    report = checker.validate(sections, args.doc_type, metadata)
    print(f"    Score: {report.overall_score}/100 ({'COMPLIANT' if report.is_compliant else 'NON-COMPLIANT'})")

    md = document_to_markdown(args.doc_type, metadata.model_dump(), [s.model_dump() for s in sections])
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output,"w",encoding="utf-8") as f:
        f.write(md)
    print(f"\n[✓] Saved: {args.output}\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
