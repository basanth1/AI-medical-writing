"""
Utility helpers — text processing, ID generation, document formatting.
"""

from __future__ import annotations
import re, uuid, hashlib, io, json
from typing import List, Dict, Tuple
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from textwrap import wrap
from datetime import datetime
_PLACEHOLDER_RE = re.compile(
    r"\[([A-Z][A-Z0-9_]{1,})\]"   # Changed {2,} to {1,} — allows [HR], [CI] etc.
)

# Common placeholders the LLM inserts — used as hints for the frontend
_PLACEHOLDER_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9_\-/ ]{1,80})\]")
_NON_TOKEN_CHARS_RE = re.compile(r"[^A-Z0-9]+")
_EXCLUDED_PLACEHOLDERS = {"COMPLIANT", "CRITICAL", "WARNING", "INFO", "TBD", "NA"}

COMMON_PLACEHOLDERS: Dict[str, str] = {
    "INVESTIGATIONAL_PRODUCT": "Investigational product name and dose",
    "SPONSOR_NAME":            "Sponsor / company name",
    "PROTOCOL_NUMBER":         "Protocol identification number",
    "PRINCIPAL_INVESTIGATOR":  "Full name of the principal investigator",
    "PI_PHONE":                "Principal investigator 24-hour phone number",
    "STUDY_SITE":              "Study site / institution name",
    "INVESTIGATOR_NAME":       "Investigator full name",
    "SITE_COORDINATOR_NAME":   "Study site coordinator full name",
    "SITE_COORDINATOR_PHONE":  "Study site coordinator phone number",
    "SITE_COORDINATOR_EMAIL":  "Study site coordinator email address",
    "IRB_CONTACT_NAME":        "IRB / IEC contact name",
    "IRB_PHONE":               "IRB / IEC phone number",
    "IRB_EMAIL":               "IRB / IEC email address",
    "SPONSOR_MEDICAL_MONITOR": "Sponsor medical monitor name",
    "MEDICAL_MONITOR_PHONE":   "Sponsor medical monitor phone number",
    "MEDICAL_MONITOR_EMAIL":   "Sponsor medical monitor email address",
    "PATIENT_NAME":            "Patient / participant full name",
    "PATIENT_PHONE":           "Patient / participant phone number",
    "PATIENT_EMAIL":           "Patient / participant email address",
    "PATIENT_ADDRESS":         "Patient / participant mailing address",
    "PATIENT_ID":              "Patient / participant identifier",
    "SAMPLE_SIZE":             "Total sample size (N)",
    "HR":                      "Hazard ratio value",
    "P_VALUE":                 "p-value",
    "CI":                      "Confidence interval bounds",
    "DURATION_MONTHS":         "Study duration in months",
    "DOSE":                    "Drug dose and unit",
    "FORMULATION":             "Drug formulation description",
    "COUNTRY":                 "Country or region",
    "START_DATE":              "Study start date",
    "END_DATE":                "Study end date / completion date",
    "IND_NUMBER":              "IND / CTA reference number",
    "IRB_NUMBER":              "IRB / IEC reference number",
    "NCT_NUMBER":              "ClinicalTrials.gov NCT number",
    "VERSION_NUMBER":          "Protocol version number",
    "DATE":                    "Relevant date",
}

PLACEHOLDER_ALIASES: Dict[str, str] = {
    "DRUG": "INVESTIGATIONAL_PRODUCT",
    "DRUG_NAME": "INVESTIGATIONAL_PRODUCT",
    "PRODUCT": "INVESTIGATIONAL_PRODUCT",
    "STUDY_DRUG": "INVESTIGATIONAL_PRODUCT",
    "IP": "INVESTIGATIONAL_PRODUCT",
    "SPONSOR": "SPONSOR_NAME",
    "COMPANY_NAME": "SPONSOR_NAME",
    "PROTOCOL_ID": "PROTOCOL_NUMBER",
    "STUDY_NUMBER": "PROTOCOL_NUMBER",
    "STUDY_ID": "PROTOCOL_NUMBER",
    "PI": "PRINCIPAL_INVESTIGATOR",
    "PI_NAME": "PRINCIPAL_INVESTIGATOR",
    "PRINCIPAL_INVESTIGATOR_NAME": "PRINCIPAL_INVESTIGATOR",
    "INVESTIGATOR": "INVESTIGATOR_NAME",
    "INVESTIGATOR_FULL_NAME": "INVESTIGATOR_NAME",
    "SITE": "STUDY_SITE",
    "SITE_NAME": "STUDY_SITE",
    "SITE_COORDINATOR": "SITE_COORDINATOR_NAME",
    "COORDINATOR": "SITE_COORDINATOR_NAME",
    "COORDINATOR_NAME": "SITE_COORDINATOR_NAME",
    "STUDY_COORDINATOR": "SITE_COORDINATOR_NAME",
    "STUDY_COORDINATOR_NAME": "SITE_COORDINATOR_NAME",
    "COORDINATOR_PHONE": "SITE_COORDINATOR_PHONE",
    "STUDY_COORDINATOR_PHONE": "SITE_COORDINATOR_PHONE",
    "COORDINATOR_EMAIL": "SITE_COORDINATOR_EMAIL",
    "STUDY_COORDINATOR_EMAIL": "SITE_COORDINATOR_EMAIL",
    "IRB_CONTACT": "IRB_CONTACT_NAME",
    "IEC_CONTACT": "IRB_CONTACT_NAME",
    "IEC_CONTACT_NAME": "IRB_CONTACT_NAME",
    "IEC_PHONE": "IRB_PHONE",
    "IEC_EMAIL": "IRB_EMAIL",
    "MEDICAL_MONITOR": "SPONSOR_MEDICAL_MONITOR",
    "MEDICAL_MONITOR_NAME": "SPONSOR_MEDICAL_MONITOR",
    "SPONSOR_MONITOR": "SPONSOR_MEDICAL_MONITOR",
    "SPONSOR_MONITOR_NAME": "SPONSOR_MEDICAL_MONITOR",
    "PATIENT": "PATIENT_NAME",
    "PATIENT_FULL_NAME": "PATIENT_NAME",
    "PARTICIPANT": "PATIENT_NAME",
    "PARTICIPANT_NAME": "PATIENT_NAME",
    "SUBJECT_NAME": "PATIENT_NAME",
    "SUBJECT_PHONE": "PATIENT_PHONE",
    "PARTICIPANT_PHONE": "PATIENT_PHONE",
    "SUBJECT_EMAIL": "PATIENT_EMAIL",
    "PARTICIPANT_EMAIL": "PATIENT_EMAIL",
    "SUBJECT_ADDRESS": "PATIENT_ADDRESS",
    "PARTICIPANT_ADDRESS": "PATIENT_ADDRESS",
    "SUBJECT_ID": "PATIENT_ID",
    "PARTICIPANT_ID": "PATIENT_ID",
    "SUBJECT_IDENTIFIER": "PATIENT_ID",
    "N": "SAMPLE_SIZE",
    "NUMBER_OF_SUBJECTS": "SAMPLE_SIZE",
    "NUMBER_OF_PATIENTS": "SAMPLE_SIZE",
    "P": "P_VALUE",
    "PVALUE": "P_VALUE",
    "P_VAL": "P_VALUE",
    "CONFIDENCE_INTERVAL": "CI",
    "DURATION": "DURATION_MONTHS",
    "STUDY_DURATION": "DURATION_MONTHS",
    "STUDY_DURATION_MONTHS": "DURATION_MONTHS",
    "START": "START_DATE",
    "COMPLETION_DATE": "END_DATE",
    "END": "END_DATE",
    "VERSION": "VERSION_NUMBER",
}

PLACEHOLDER_GENERATION_GUIDE = "\n".join(
    f"     - [{token}]: {description}"
    for token, description in COMMON_PLACEHOLDERS.items()
)


def normalize_placeholder_token(token: str) -> str:
    """
    Convert model-generated placeholder variants to the shared token shape.
    Examples: "p-VALUE" -> "P_VALUE", "Patient Name" -> "PATIENT_NAME".
    """
    normalized = _NON_TOKEN_CHARS_RE.sub("_", token.strip().upper()).strip("_")
    return re.sub(r"_+", "_", normalized)


def canonicalize_placeholder_token(token: str) -> str:
    """
    Map a normalized placeholder variant to the canonical token used by the UI.
    """
    normalized = normalize_placeholder_token(token)
    return PLACEHOLDER_ALIASES.get(normalized, normalized)


def extract_placeholders(text: str) -> List[str]:
    """
    Return a sorted, deduplicated list of placeholder tokens found in text.
    e.g. ["INVESTIGATIONAL_PRODUCT", "SAMPLE_SIZE", "SPONSOR_NAME"]
    """
    found = _PLACEHOLDER_RE.findall(text)
    return sorted({
        canonical
        for raw in found
        if (canonical := canonicalize_placeholder_token(raw)) not in _EXCLUDED_PLACEHOLDERS
    })


def extract_placeholders_from_sections(sections: List[dict]) -> List[str]:
    """
    Scan all section content and return every unique placeholder token found.
    """
    all_text = " ".join(s.get("content", "") for s in sections)
    return extract_placeholders(all_text)


def apply_placeholder_replacements(
    sections: List[dict],
    replacements: Dict[str, str],
) -> Tuple[List[dict], int, List[str]]:
    """
    Replace placeholder tokens in section content. Model-generated variants are
    canonicalized, so replacing P_VALUE also fills [p-VALUE] or [P VALUE].

    Args:
        sections:     List of section dicts (each has "content" key).
        replacements: {"INVESTIGATIONAL_PRODUCT": "TrialDrug-X 150mg", ...}

    Returns:
        (updated_sections, count_of_replacements_made, remaining_placeholders)
    """
    total_replaced = 0
    cleaned_replacements = {
        canonicalize_placeholder_token(token): value.strip()
        for token, value in replacements.items()
        if value and value.strip()
    }

    for sec in sections:
        content = sec.get("content", "")

        def replace_match(match: re.Match) -> str:
            nonlocal total_replaced
            canonical = canonicalize_placeholder_token(match.group(1))
            value = cleaned_replacements.get(canonical)
            if not value:
                return match.group(0)
            total_replaced += 1
            return value

        content = _PLACEHOLDER_RE.sub(replace_match, content)
        sec["content"]    = content
        sec["word_count"] = len(content.split())

    remaining = extract_placeholders_from_sections(sections)
    return sections, total_replaced, remaining



def generate_session_id(indication: str, phase: str) -> str:
    """Generate a human-readable session ID."""
    ind_code   = re.sub(r"[^A-Za-z]", "", indication)[:3].upper()
    phase_code = re.sub(r"[^IVX0-9]", "", phase)[:2]
    ts         = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"SES-{ind_code}-P{phase_code}-{ts}"


def stable_doc_id(text: str) -> str:
    """Deterministic ID from document content (first 200 chars)."""
    return hashlib.md5(text[:200].encode()).hexdigest()[:12]


def word_count(text: str) -> int:
    return len(text.split())


def truncate(text: str, max_chars: int = 2000) -> str:
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def flesch_kincaid_grade(text: str) -> float:
    """
    Approximate Flesch-Kincaid grade level.
    Useful for ICF readability checks (target ≤8th grade).
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words     = text.split()
    syllables = sum(_syllable_count(w) for w in words)

    if not sentences or not words:
        return 0.0

    asl = len(words) / len(sentences)       # avg sentence length
    asw = syllables / len(words)            # avg syllables per word
    return 0.39 * asl + 11.8 * asw - 15.59


def _syllable_count(word: str) -> int:
    word    = word.lower().strip(".,!?;:'\"")
    count   = 0
    vowels  = "aeiouy"
    prev_v  = False
    for char in word:
        is_v = char in vowels
        if is_v and not prev_v:
            count += 1
        prev_v = is_v
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)

def _cover_block(doc_type: str, meta: dict, status: str = "") -> List[str]:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# {doc_type}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **Protocol Number** | {meta.get('protocol_number', '[PROTOCOL_NUMBER]')} |",
        f"| **Sponsor** | {meta.get('sponsor', '[SPONSOR_NAME]')} |",
        f"| **Indication** | {meta.get('indication', '—')} |",
        f"| **Phase** | {meta.get('phase', '—')} |",
        f"| **Design** | {meta.get('design', '—')} |",
        f"| **Primary Endpoint** | {meta.get('primary_endpoint', '—')} |",
        f"| **Sample Size** | {meta.get('sample_size', 'TBD')} |",
        f"| **Duration** | {meta.get('duration_months', 'TBD')} months |",
        f"| **Generated** | {ts} |",
    ]
    if status:
        lines.append(f"| **Status** | {status} |")
    lines += ["", "---", ""]
    return lines


def _section_to_markdown(sec: dict, idx: int) -> List[str]:
    title   = sec.get("title", f"Section {idx + 1}")
    content = sec.get("content", "").strip()
    conf    = sec.get("confidence_score", 0.0)
    revised = sec.get("revised", False)
    rev_tag = " *(revised)*" if revised else ""

    lines = [
        f"## {title}{rev_tag}",
        "",
    ]

    # Render the content — tables in LLM output are passed through as-is
    lines.append(content)
    lines.append("")

    # Metadata footer
    lines += [
        f"> **Confidence:** {conf:.0%}  |  "
        f"**Words:** {sec.get('word_count', len(content.split()))}",
        "",
        "---",
        "",
    ]
    return lines


def document_to_markdown(
    document_type: str,
    metadata_dict: dict,
    sections:      List[dict],
    status:        str = "",
) -> str:
    """
    Convert a generated document to human-readable Markdown.
    Tables in section content are preserved as-is.
    """
    lines: List[str] = []
    lines += _cover_block(document_type, metadata_dict, status)

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for i, sec in enumerate(sections):
        title = sec.get("title", f"Section {i + 1}")
        anchor = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        lines.append(f"{i + 1}. [{title}](#{anchor})")
    lines += ["", "---", ""]

    # Sections
    for i, sec in enumerate(sections):
        lines += _section_to_markdown(sec, i)

    return "\n".join(lines)


def document_to_json(
    session_id:    str,
    document_type: str,
    metadata_dict: dict,
    sections:      List[dict],
    compliance:    dict = None,
    status:        str  = "",
) -> str:
    """
    Export the document as a structured JSON string.
    """
    payload = {
        "session_id":    session_id,
        "document_type": document_type,
        "status":        status or "generated",
        "exported_at":   datetime.now(timezone.utc).isoformat(),
        "metadata":      metadata_dict,
        "sections": [
            {
                "section_id":       s.get("section_id"),
                "title":            s.get("title"),
                "content":          s.get("content"),
                "word_count":       s.get("word_count", 0),
                "confidence_score": round(s.get("confidence_score", 0.0), 4),
                "revised":          s.get("revised", False),
                "revision_count":   s.get("revision_count", 0),
                "sources_used":     s.get("sources_used", []),
            }
            for s in sections
        ],
        "compliance_summary": {
            "overall_score": compliance.get("overall_score", 0) if compliance else None,
            "is_compliant":  compliance.get("is_compliant", False) if compliance else None,
            "critical_issues": len([
                i for i in (compliance or {}).get("issues", [])
                if i.get("severity") == "critical"
            ]),
        } if compliance else None,
        "total_words": sum(s.get("word_count", 0) for s in sections),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


# def document_to_pdf(
#     document_type: str,
#     metadata_dict: dict,
#     sections:      List[dict],
#     status:        str = "",
# ) -> bytes:
#     """
#     Export the generated clinical trial document to a styled PDF.
#     Uses ReportLab (pure-Python, no external binaries required).
#     Falls back to UTF-8 Markdown bytes when ReportLab is not installed
#     so the endpoint never hard-crashes.
#     Returns raw bytes ready to stream as application/pdf.
#     """
#     try:
#         from reportlab.lib.pagesizes  import A4
#         from reportlab.lib.units      import cm
#         from reportlab.lib.styles     import getSampleStyleSheet, ParagraphStyle
#         from reportlab.lib            import colors
#         from reportlab.platypus       import (
#             SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
#             PageBreak, HRFlowable,
#         )
#         from reportlab.lib.enums      import TA_CENTER, TA_LEFT, TA_JUSTIFY
#     except ImportError:
#         # Graceful fallback: ship markdown as bytes (frontend shows a toast)
#         return document_to_markdown(document_type, metadata_dict, sections, status).encode("utf-8")
#     buf = io.BytesIO()
#     # ── Page setup ────────────────────────────────────────────────────────────
#     doc = SimpleDocTemplate(
#         buf,
#         pagesize    = A4,
#         leftMargin  = 2.2 * cm,
#         rightMargin = 2.2 * cm,
#         topMargin   = 2.5 * cm,
#         bottomMargin= 2.0 * cm,
#         title       = document_type,
#         author      = metadata_dict.get("sponsor", "TrialDoc AI"),
#     )
#     W = A4[0] - 4.4 * cm   # usable text width
#     # ── Colour palette (clinical / professional) ──────────────────────────────
#     C_NAVY    = colors.HexColor("#1a3a5c")
#     C_ACCENT  = colors.HexColor("#2e6da4")
#     C_MUTED   = colors.HexColor("#6b7a8d")
#     C_RULE    = colors.HexColor("#d0d8e4")
#     C_REVISED = colors.HexColor("#c05c00")
#     C_BG_CELL = colors.HexColor("#f0f4f8")
#     C_WHITE   = colors.white
#     C_BLACK   = colors.HexColor("#1a1a2e")
#     # ── Styles ─────────────────────────────────────────────────────────────────
#     base = getSampleStyleSheet()
#     def style(name, **kw):
#         return ParagraphStyle(name, **kw)
#     S_TITLE = style("DocTitle",
#         fontName="Helvetica-Bold", fontSize=22,
#         textColor=C_NAVY, alignment=TA_CENTER,
#         spaceAfter=6,
#     )
#     S_SUBTITLE = style("DocSubtitle",
#         fontName="Helvetica", fontSize=11,
#         textColor=C_ACCENT, alignment=TA_CENTER,
#         spaceAfter=4,
#     )
#     S_COVER_LABEL = style("CoverLabel",
#         fontName="Helvetica-Bold", fontSize=9,
#         textColor=C_NAVY,
#     )
#     S_COVER_VALUE = style("CoverValue",
#         fontName="Helvetica", fontSize=9,
#         textColor=C_BLACK,
#     )
#     S_SECTION_HEADING = style("SectionHeading",
#         fontName="Helvetica-Bold", fontSize=13,
#         textColor=C_NAVY, spaceBefore=14, spaceAfter=6,
#         borderPadding=(0, 0, 3, 0),
#     )
#     S_REVISED_BADGE = style("RevisedBadge",
#         fontName="Helvetica-Bold", fontSize=8,
#         textColor=C_REVISED,
#     )
#     S_BODY = style("BodyText",
#         fontName="Helvetica", fontSize=9.5,
#         textColor=C_BLACK, leading=14,
#         alignment=TA_JUSTIFY, spaceAfter=4,
#     )
#     S_BULLET = style("BulletItem",
#         fontName="Helvetica", fontSize=9.5,
#         textColor=C_BLACK, leading=13,
#         leftIndent=14, bulletIndent=4,
#         spaceAfter=2,
#     )
#     S_CAPTION = style("Caption",
#         fontName="Helvetica-Oblique", fontSize=8,
#         textColor=C_MUTED, spaceAfter=10,
#     )
#     S_FOOTER_NOTE = style("FooterNote",
#         fontName="Helvetica-Oblique", fontSize=7.5,
#         textColor=C_MUTED, alignment=TA_CENTER,
#     )
#     S_TABLE_HEADER = style("TableHeader",
#         fontName="Helvetica-Bold", fontSize=8.5,
#         textColor=C_WHITE,
#     )
#     S_TABLE_CELL = style("TableCell",
#         fontName="Helvetica", fontSize=8.5,
#         textColor=C_BLACK, leading=12,
#     )
#     story = []
#     # ─────────────────────────────────────────────────────────────────────────
#     # COVER PAGE
#     # ─────────────────────────────────────────────────────────────────────────
#     story.append(Spacer(1, 1.8 * cm))
#     story.append(Paragraph(document_type, S_TITLE))
#     story.append(Paragraph("AI-Generated Clinical Trial Document", S_SUBTITLE))
#     story.append(Spacer(1, 0.4 * cm))
#     story.append(HRFlowable(width=W, thickness=1.5, color=C_ACCENT, spaceAfter=12))
#     # Cover metadata table
#     cover_fields = [
#         ("Protocol Number",  metadata_dict.get("protocol_number", "[PROTOCOL_NUMBER]")),
#         ("Sponsor",          metadata_dict.get("sponsor",          "[SPONSOR_NAME]")),
#         ("Indication",       metadata_dict.get("indication",       "—")),
#         ("Phase",            metadata_dict.get("phase",            "—")),
#         ("Study Design",     metadata_dict.get("design",           "—")),
#         ("Primary Endpoint", metadata_dict.get("primary_endpoint", "—")),
#         ("Sample Size",      str(metadata_dict.get("sample_size",  "TBD"))),
#         ("Duration",         f"{metadata_dict.get('duration_months', 'TBD')} months"),
#         ("Document Status",  status or "Generated"),
#         ("Generated At",     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
#     ]
#     cover_data = [
#         [Paragraph(label, S_COVER_LABEL), Paragraph(str(value), S_COVER_VALUE)]
#         for label, value in cover_fields
#     ]
#     cover_tbl = Table(cover_data, colWidths=[4.5 * cm, W - 4.5 * cm])
#     cover_tbl.setStyle(TableStyle([
#         ("BACKGROUND",  (0, 0), (0, -1), C_BG_CELL),
#         ("BACKGROUND",  (1, 0), (1, -1), C_WHITE),
#         ("GRID",        (0, 0), (-1, -1), 0.4, C_RULE),
#         ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
#         ("TOPPADDING",  (0, 0), (-1, -1), 5),
#         ("BOTTOMPADDING",(0,0), (-1, -1), 5),
#         ("LEFTPADDING", (0, 0), (-1, -1), 7),
#         ("RIGHTPADDING",(0, 0), (-1, -1), 7),
#         ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_BG_CELL, C_WHITE]),
#     ]))
#     story.append(cover_tbl)
#     story.append(Spacer(1, 0.6 * cm))
#     # Section count summary
#     total_words = sum(s.get("word_count", 0) for s in sections)
#     story.append(Paragraph(
#         f"{len(sections)} sections · {total_words:,} words · "
#         f"TrialDoc AI · ICH E6/E3 Compliant Draft",
#         S_CAPTION,
#     ))
#     story.append(PageBreak())
#     # ─────────────────────────────────────────────────────────────────────────
#     # SECTION PAGES
#     # ─────────────────────────────────────────────────────────────────────────
#     for sec in sections:
#         title   = sec.get("title",            "Section")
#         content = sec.get("content",          "").strip()
#         revised = sec.get("revised",          False)
#         conf    = sec.get("confidence_score", 0.0)
#         words   = sec.get("word_count",       0)
#         # Section heading row
#         heading_text = title
#         story.append(Paragraph(heading_text, S_SECTION_HEADING))
#         if revised:
#             story.append(Paragraph("[ REVISED BY REVIEWER ]", S_REVISED_BADGE))
#         story.append(HRFlowable(width=W, thickness=0.5, color=C_RULE, spaceAfter=6))
#         # Parse content — handle markdown tables, bullets, headings, plain text
#         _render_content(content, story, W, S_BODY, S_BULLET, S_TABLE_HEADER, S_TABLE_CELL, C_NAVY, C_ACCENT, C_RULE, C_BG_CELL, C_WHITE, C_BLACK)
#         # Footer meta line
#         story.append(Spacer(1, 4))
#         story.append(Paragraph(
#             f"Confidence score: {conf:.0%}  ·  {words:,} words",
#             S_CAPTION,
#         ))
#         story.append(HRFlowable(width=W, thickness=0.3, color=C_RULE, spaceAfter=4))
#         story.append(Spacer(1, 6))
#     # ─────────────────────────────────────────────────────────────────────────
#     # BUILD
#     # ─────────────────────────────────────────────────────────────────────────
#     def _on_page(canvas, doc_):
#         """Draw header/footer on every page."""
#         canvas.saveState()
#         # Top rule
#         canvas.setStrokeColor(C_RULE)
#         canvas.setLineWidth(0.5)
#         canvas.line(2.2 * cm, A4[1] - 1.8 * cm, A4[0] - 2.2 * cm, A4[1] - 1.8 * cm)
#         # Header text
#         canvas.setFont("Helvetica", 7.5)
#         canvas.setFillColor(C_MUTED)
#         canvas.drawString(2.2 * cm, A4[1] - 1.55 * cm, document_type)
#         canvas.drawRightString(A4[0] - 2.2 * cm, A4[1] - 1.55 * cm,
#                                metadata_dict.get("indication", "") + "  ·  " + metadata_dict.get("phase", ""))
#         # Bottom rule + page number
#         canvas.line(2.2 * cm, 1.6 * cm, A4[0] - 2.2 * cm, 1.6 * cm)
#         canvas.drawCentredString(A4[0] / 2, 1.1 * cm, f"Page {doc_.page}")
#         canvas.restoreState()
#     doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
#     buf.seek(0)
#     return buf.read()
# # ── Content renderer ──────────────────────────────────────────────────────────
# def _render_content(content, story, W, S_BODY, S_BULLET, S_TH, S_TC,
#                     C_NAVY, C_ACCENT, C_RULE, C_BG_CELL, C_WHITE, C_BLACK):
#     """
#     Parse markdown-ish section content into ReportLab flowables.
#     Handles:
#       - Markdown tables  (| col | col |)
#       - Bullet lines     (- text  or  * text)
#       - Numbered lists   (1. text)
#       - Sub-headings     (## heading  or  ### heading)
#       - Bold inline      (**text**)
#       - Plain paragraphs (everything else)
#     """
#     from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
#     from reportlab.lib      import colors as rl_colors
#     lines = content.split("\n")
#     buffer_lines: List[str] = []
#     table_rows:   List[List[str]] = []
#     in_table = False
#     def flush_buffer():
#         if not buffer_lines:
#             return
#         para_text = " ".join(l for l in buffer_lines if l.strip())
#         if para_text.strip():
#             story.append(Paragraph(_md_inline(para_text), S_BODY))
#         buffer_lines.clear()
#     def flush_table():
#         if not table_rows:
#             return
#         max_cols = max(len(r) for r in table_rows)
#         # Pad rows to max_cols
#         padded = [r + [""] * (max_cols - len(r)) for r in table_rows]
#         col_w  = W / max_cols
#         tbl_data = []
#         for ri, row in enumerate(padded):
#             if ri == 0:
#                 tbl_data.append([Paragraph(c, S_TH) for c in row])
#             else:
#                 tbl_data.append([Paragraph(c, S_TC) for c in row])
#         tbl = Table(tbl_data, colWidths=[col_w] * max_cols, repeatRows=1)
#         tbl.setStyle(TableStyle([
#             ("BACKGROUND",   (0, 0), (-1, 0),  C_NAVY),
#             ("BACKGROUND",   (0, 1), (-1, -1), C_WHITE),
#             ("ROWBACKGROUNDS",(0, 1),(-1, -1), [C_BG_CELL, C_WHITE]),
#             ("GRID",         (0, 0), (-1, -1), 0.4, C_RULE),
#             ("TOPPADDING",   (0, 0), (-1, -1), 4),
#             ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
#             ("LEFTPADDING",  (0, 0), (-1, -1), 5),
#             ("RIGHTPADDING", (0, 0), (-1, -1), 5),
#             ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
#         ]))
#         story.append(tbl)
#         story.append(Spacer(1, 6))
#         table_rows.clear()
#     for raw_line in lines:
#         line = raw_line.rstrip()
#         # ── Markdown table line ────────────────────────────────────────────
#         if "|" in line and line.strip().startswith("|"):
#             if not in_table:
#                 flush_buffer()
#                 in_table = True
#             if re.match(r"^\s*\|[-:\s|]+\|\s*$", line):
#                 continue   # skip separator
#             cells = [c.strip() for c in line.strip().strip("|").split("|")]
#             table_rows.append(cells)
#             continue

#         if in_table:
#             flush_table()
#             in_table = False

#         stripped = line.strip()

#         # ── Sub-heading (## or ###) ────────────────────────────────────────
#         if stripped.startswith("### ") or stripped.startswith("## ") or stripped.startswith("# "):
#             flush_buffer()
#             heading_txt = re.sub(r"^#{1,3}\s+", "", stripped)
#             from reportlab.lib.styles import ParagraphStyle
#             from reportlab.lib.enums  import TA_LEFT
#             sub_style = ParagraphStyle("SubH",
#                 fontName="Helvetica-Bold", fontSize=10,
#                 textColor=C_ACCENT, spaceBefore=8, spaceAfter=3,
#             )
#             story.append(Paragraph(_md_inline(heading_txt), sub_style))
#             continue

#         # ── Bullet ────────────────────────────────────────────────────────
#         if re.match(r"^[-*•]\s+", stripped):
#             flush_buffer()
#             bullet_text = re.sub(r"^[-*•]\s+", "", stripped)
#             story.append(Paragraph("•  " + _md_inline(bullet_text), S_BULLET))
#             continue

#         # ── Numbered list ─────────────────────────────────────────────────
#         if re.match(r"^\d+\.\s+", stripped):
#             flush_buffer()
#             num_text = re.sub(r"^\d+\.\s+", "", stripped)
#             story.append(Paragraph(_md_inline(stripped[:stripped.index(".")+1]) + "  " + _md_inline(num_text), S_BULLET))
#             continue

#         # ── Empty line = paragraph break ──────────────────────────────────
#         if not stripped:
#             flush_buffer()
#             continue

#         # ── Normal text ───────────────────────────────────────────────────
#         buffer_lines.append(line)

#     # Flush any remaining
#     if in_table:
#         flush_table()
#     flush_buffer()


# def _md_inline(text: str) -> str:
#     """
#     Convert basic markdown inline markup to ReportLab XML tags.
#     Handles: **bold**, *italic*, `code`
#     Escapes ReportLab XML special chars first.
#     """
#     # Escape XML
#     text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
#     # Bold
#     text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
#     # Italic
#     text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
#     # Code
#     text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
#     return text
def document_to_pdf(document_type: str, metadata_dict: dict, sections: List[dict], status: str = "") -> bytes:
    """
    Export to PDF using reportlab.
    Returns raw bytes that can be streamed to the client.
    """
    from io import BytesIO
    from datetime import datetime

    # Create a byte buffer to hold the PDF data
    buffer = BytesIO()

    # Set up the PDF canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Get page width and height

    def draw_wrapped_text(c, text, x, y, max_width=500, font="Helvetica", font_size=12):
        """Draw text that wraps to fit within the specified max width."""
        c.setFont(font, font_size)
        lines = wrap(text, width=70)  # Wrap text to fit within the given width
        for line in lines:
            c.drawString(x, y, line)
            y -= font_size + 2  # Adjust y-position for the next line
            if y < 100:  # Check if we are near the bottom of the page
                c.showPage()  # Create a new page if we reach the bottom
                y = height - 100  # Reset to top of the page
        return y

    # Title and Metadata
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, document_type)  # Title of the document
    c.setFont("Helvetica", 12)

    # Add metadata (like protocol number, sponsor, etc.)
    y_position = 730
    metadata_lines = [
        f"Protocol Number: {metadata_dict.get('protocol_number', 'N/A')}",
        f"Sponsor: {metadata_dict.get('sponsor', 'N/A')}",
        f"Indication: {metadata_dict.get('indication', 'N/A')}",
        f"Phase: {metadata_dict.get('phase', 'N/A')}",
        f"Primary Endpoint: {metadata_dict.get('primary_endpoint', 'N/A')}",
        f"Sample Size: {metadata_dict.get('sample_size', 'TBD')}",
        f"Duration: {metadata_dict.get('duration_months', 'TBD')} months",
        f"Status: {status}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    ]
    
    # Draw metadata lines
    for line in metadata_lines:
        y_position = draw_wrapped_text(c, line, 72, y_position)
    
    # Page break
    c.showPage()

    # Add the sections
    for section in sections:
        title = section.get("title", "Section")
        content = section.get("content", "")
        word_count = section.get("word_count", 0)
        confidence = section.get("confidence_score", 0.0)

        # Section Title
        c.setFont("Helvetica-Bold", 14)
        y_position = draw_wrapped_text(c, title, 72, y_position)

        # Section Content
        c.setFont("Helvetica", 12)
        y_position = draw_wrapped_text(c, content, 72, y_position)

        # Confidence and word count footer
        c.setFont("Helvetica", 10)
        c.drawString(72, y_position, f"Confidence: {confidence:.0%}  |  Words: {word_count}")
        y_position -= 30

        # Page break between sections if needed
        if y_position < 100:
            c.showPage()
            y_position = height - 100  # Reset to top of the page

    # Finalize PDF and return as bytes
    c.save()

    # Get the value of the BytesIO buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes



def document_to_docx(document_type: str, metadata_dict: dict, sections: List[dict], status: str = "") -> bytes:
    """
    Export to DOCX using pypandoc.
    Returns raw bytes that can be streamed to the client.
    """
    import os
    import tempfile

    try:
        import pypandoc
    except ImportError as exc:
        raise RuntimeError("DOCX export requires the pypandoc package to be installed.") from exc

    markdown = document_to_markdown(document_type, metadata_dict, sections, status)

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        output_path = tmp.name

    try:
        pypandoc.convert_text(
            markdown,
            "docx",
            format="md",
            outputfile=output_path,
            extra_args=["--standalone"],
        )
        with open(output_path, "rb") as docx_file:
            return docx_file.read()
    finally:
        try:
            os.remove(output_path)
        except OSError:
            pass


# def document_to_docx(
#     document_type: str,
#     metadata_dict: dict,
#     sections:      List[dict],
#     status:        str = "",
# ) -> bytes:
#     """
#     Export to .docx using python-docx.
#     Returns raw bytes that can be streamed to the client.
#     Falls back to a UTF-8 encoded Markdown string if python-docx is not installed.
#     """
#     try:
#         from docx import Document
#         from docx.shared import Pt, RGBColor, Inches
#         from docx.enum.text import WD_ALIGN_PARAGRAPH
#     except ImportError:
#         # Fallback: return markdown bytes
#         md = document_to_markdown(document_type, metadata_dict, sections, status)
#         return md.encode("utf-8")

#     doc = Document()

#     # ── Styles ────────────────────────────────────────────────────────────────
#     style = doc.styles["Normal"]
#     style.font.name = "Calibri"
#     style.font.size = Pt(11)

#     # ── Title page ───────────────────────────────────────────────────────────
#     title_para = doc.add_heading(document_type, level=0)
#     title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

#     doc.add_paragraph()

#     # Cover table
#     table = doc.add_table(rows=0, cols=2)
#     table.style = "Table Grid"
#     cover_fields = [
#         ("Protocol Number", metadata_dict.get("protocol_number", "[PROTOCOL_NUMBER]")),
#         ("Sponsor",         metadata_dict.get("sponsor", "[SPONSOR_NAME]")),
#         ("Indication",      metadata_dict.get("indication", "—")),
#         ("Phase",           metadata_dict.get("phase", "—")),
#         ("Design",          metadata_dict.get("design", "—")),
#         ("Primary Endpoint",metadata_dict.get("primary_endpoint", "—")),
#         ("Sample Size",     str(metadata_dict.get("sample_size", "TBD"))),
#         ("Duration",        f"{metadata_dict.get('duration_months', 'TBD')} months"),
#         ("Status",          status or "Generated"),
#         ("Generated",       datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
#     ]
#     for label, value in cover_fields:
#         row  = table.add_row()
#         cell_label = row.cells[0]
#         cell_value = row.cells[1]
#         cell_label.text = label
#         cell_value.text = str(value)
#         cell_label.paragraphs[0].runs[0].bold = True

#     doc.add_page_break()

#     # ── Sections ─────────────────────────────────────────────────────────────
#     for sec in sections:
#         title   = sec.get("title", "Section")
#         content = sec.get("content", "").strip()
#         revised = sec.get("revised", False)
#         conf    = sec.get("confidence_score", 0.0)

#         heading_text = f"{title}{'  [REVISED]' if revised else ''}"
#         doc.add_heading(heading_text, level=1)

#         # Detect markdown tables in the content and render them as Word tables
#         lines       = content.split("\n")
#         buffer      = []
#         in_table    = False
#         table_rows  = []

#         def flush_buffer(buf):
#             if buf:
#                 para_text = " ".join(buf).strip()
#                 if para_text:
#                     doc.add_paragraph(para_text)

#         for line in lines:
#             if "|" in line and line.strip().startswith("|"):
#                 if not in_table:
#                     flush_buffer(buffer)
#                     buffer   = []
#                     in_table = True
#                 # Skip separator rows like |---|---|
#                 if re.match(r"^\s*\|[-:\s|]+\|\s*$", line):
#                     continue
#                 cells = [c.strip() for c in line.strip().strip("|").split("|")]
#                 table_rows.append(cells)
#             else:
#                 if in_table:
#                     # Render collected table rows into a Word table
#                     if table_rows:
#                         max_cols = max(len(r) for r in table_rows)
#                         word_tbl = doc.add_table(rows=len(table_rows), cols=max_cols)
#                         word_tbl.style = "Table Grid"
#                         for ri, row_cells in enumerate(table_rows):
#                             for ci, cell_text in enumerate(row_cells):
#                                 if ci < max_cols:
#                                     word_tbl.rows[ri].cells[ci].text = cell_text
#                                     if ri == 0:
#                                         word_tbl.rows[ri].cells[ci].paragraphs[0].runs[0].bold = True
#                         doc.add_paragraph()
#                     table_rows = []
#                     in_table   = False
#                 buffer.append(line)

#         if in_table and table_rows:
#             max_cols = max(len(r) for r in table_rows)
#             word_tbl = doc.add_table(rows=len(table_rows), cols=max_cols)
#             word_tbl.style = "Table Grid"
#             for ri, row_cells in enumerate(table_rows):
#                 for ci, cell_text in enumerate(row_cells):
#                     if ci < max_cols:
#                         word_tbl.rows[ri].cells[ci].text = cell_text
#                         if ri == 0:
#                             word_tbl.rows[ri].cells[ci].paragraphs[0].runs[0].bold = True
#             doc.add_paragraph()
#         else:
#             flush_buffer(buffer)

#         # Metadata footnote
#         doc.add_paragraph(
#             f"Confidence: {conf:.0%}  |  Words: {sec.get('word_count', 0)}",
#             style="Caption",
#         )
#         doc.add_paragraph()

#     # ── Serialize ─────────────────────────────────────────────────────────────
#     buf = io.BytesIO()
#     doc.save(buf)
#     buf.seek(0)
#     return buf.read()
