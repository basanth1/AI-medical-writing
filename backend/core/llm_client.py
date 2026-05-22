"""
backend/core/llm_client.py
LLMClient — single entry point for all text generation and validation.

Pipeline:
    generate()   →  1. OllamaClient  (gpt-oss:120b, free)
                    2. GroqClient     (llama-3.3-70b-versatile, fallback)
                    3. template       (offline, last resort)

    validate()   →  1. GroqClient    (llama-3.1-8b-instant, fast + cheap)
                    2. rule-based     (regex, offline fallback)

Services import ONLY this class — never OllamaClient or GroqClient directly.
"""

import logging
from typing import Optional, Generator, Tuple

from backend.core.ollama_client import OllamaClient
from backend.core.groq_client   import GroqClient
from backend.core.confidence    import ConfidenceScorer, ScoreBreakdown
from backend.data.models_config  import DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# System prompt used when Groq validates Ollama-generated content
_VALIDATION_SYSTEM = (
    "You are a regulatory affairs specialist reviewing clinical trial document sections. "
    "Identify any compliance issues, missing required elements, or inaccuracies. "
    "Be concise — one issue per line, prefixed with [CRITICAL], [WARNING], or [INFO]. "
    "If the section fully meets regulatory requirements, respond with exactly: COMPLIANT"
)
MIN_RESPONSE_LENGTH = 50
MAX_RESPONSE_LENGTH = 2000
CRITICAL_WORDS = ["uncertain", "possibly", "potentially", "may", "might"]

class LLMClient:
    """
    Unified LLM orchestrator.

    Primary   : OllamaClient  → gpt-oss:120b          (free, local/hosted)
    Validator : GroqClient    → llama-3.1-8b-instant   (fast, cheap)
    Fallback  : GroqClient    → llama-3.3-70b-versatile (paid, reliable)
    """

    def __init__(
        self,
        ollama_api_key: Optional[str] = None,
        groq_api_key:   Optional[str] = None,
        ollama_model:   Optional[str] = None,   # None → OLLAMA_MODEL from config
        groq_model:     str           = "medical",
    ):
        import os

        self._ollama = OllamaClient(
            api_key = ollama_api_key or os.environ.get("OLLAMA_API_KEY", ""),
            model   = ollama_model   or os.environ.get("OLLAMA_MODEL", ""),
        )
        self._groq = GroqClient(
            api_key = groq_api_key or os.environ.get("GROQ_API_KEY", ""),
            model   = groq_model,
        )
        self._scorer = ConfidenceScorer()
        self._log_startup()

    # ── Generation ────────────────────────────────────────────────────────────

    def generate(
        self,
        prompt:     str,
        *,
        system:     str  = DEFAULT_SYSTEM_PROMPT,
        allow_groq: bool = True,
    ) -> str:
        """
        Generate text. Tries Ollama (gpt-oss:120b) first;
        falls back to Groq (llama-3.3-70b-versatile) on failure.
        """
        # 1. Ollama — gpt-oss:120b (primary, free)
        if self._ollama.is_available():
            try:
                text = self._ollama.chat(prompt, system=system)
                logger.debug(f"Ollama generated {len(text.split())} words")
                return text
            except Exception as exc:
                if not allow_groq:
                    raise
                logger.warning(
                    f"Ollama (gpt-oss:120b) failed: {exc!r} "
                    f"— falling back to Groq (llama-3.3-70b-versatile)"
                )

        # 2. Groq fallback — llama-3.3-70b-versatile
        if allow_groq and self._groq.is_available():
            logger.info("Using Groq fallback (llama-3.3-70b-versatile)")
            return self._groq.chat(prompt, system=system)

        # 3. Template (both unavailable)
        return self._groq._template_fallback(prompt)

    def generate_with_system(self, system: str, prompt: str) -> str:
        """Explicit system + user — preferred for section generation."""
        return self.generate(prompt, system=system)

    def generate_scored(
        self,
        section_id: str,
        prompt:     str,
        *,
        system:     str  = DEFAULT_SYSTEM_PROMPT,
        allow_groq: bool = True,
    ) -> Tuple[str, float, ScoreBreakdown]:
        """
        Generate text AND compute its confidence score in one call.

        Returns:
            (text, confidence_score, breakdown)

        Example:
            text, score, detail = client.generate_scored("statistics", prompt, system=sys)
            # score = 0.847
            # detail.length_score, detail.structure_score, ...
        """
        # Determine whether Groq fallback was used for the penalty
        use_fallback = not self._ollama.is_available() and self._groq.is_available()

        text = self.generate(prompt, system=system, allow_groq=allow_groq)

        breakdown = self._scorer.score_with_breakdown(
            section_id, text, use_fallback=use_fallback
        )

        logger.debug(
            f"generate_scored [{section_id}]: "
            f"score={breakdown.final:.3f}  words={breakdown.word_count}  "
            f"fallback={use_fallback}"
        )
        return text, breakdown.final, breakdown

    def stream(
        self, prompt: str, *, system: str = DEFAULT_SYSTEM_PROMPT
    ) -> Generator[str, None, None]:
        """Stream chunks — Ollama primary, Groq fallback."""
        if self._ollama.is_available():
            try:
                yield from self._ollama.stream(prompt, system=system)
                return
            except Exception as exc:
                logger.warning(f"Ollama stream failed ({exc!r}) — switching to Groq")

        if self._groq.is_available():
            yield from self._groq.stream(prompt, system=system)
        else:
            yield self._groq._template_fallback(prompt)

    def score_section(
        self,
        section_id:   str,
        response:     str,
        *,
        use_fallback: bool = False,
    ) -> float:
        """
        Score an already-generated response. Returns float in [0.0, 1.0].

        Args:
            section_id:   e.g. "intro", "statistics", "population"
            response:     the generated text to score
            use_fallback: True if Groq was used (not Ollama) — applies a penalty
        """
        return self._scorer.score(section_id, response, use_fallback=use_fallback)

    def score_section_detailed(
        self,
        section_id:   str,
        response:     str,
        *,
        use_fallback: bool = False,
    ) -> dict:
        """
        Score with full breakdown. Returns a dict suitable for logging / API response.

        Returns:
            {
                "final": 0.847,
                "word_count": 412,
                "length_score": 0.45,
                "structure_score": 0.20,
                "coverage_score": 0.15,
                "uncertainty_penalty": 0.0,
                "fallback_penalty": 0.0,
                "is_template": False,
                "uncertainty_hits": [],
                "coverage_hits": "3/3",
            }
        """
        bd = self._scorer.score_with_breakdown(
            section_id, response, use_fallback=use_fallback
        )
        return bd.to_dict()

    def score_multiple_responses(
        self,
        section_id:   str,
        responses:    list,
        *,
        use_fallback: bool = False,
    ) -> float:
        """
        Score confidence from multiple candidate responses.
        The best response + a consistency bonus is returned.
        Mirrors the original evaluate_multiple_responses() pattern.
        """
        return self._scorer.evaluate_multiple_responses(
            section_id, responses, use_fallback=use_fallback
        )
    
    # -- Rewriting (for feedback loop) ───────────────────────────────────────────
    def rewrite_section(self, original: str, comment: str, revised: str, section_id:  str  = "unknown", allow_groq: bool = True) -> str:
        if not self._ollama.is_available() and not self._groq.is_available():
            logger.warning("Ollama unavailable — skipping rewrite and returning revised text")
            return revised or original
        system_prompt_feedback = """
        You are an expert AI medical writer specializing in rewriting and structuring clinical trial documents for human readability and regulatory standards.

        Follow these strict guidelines:

        1. **Structure First (CRITICAL)**
        - Organize the content into clear sections with headings.
        - Use hierarchy:
            - Section titles → Bold or Markdown headers
            - Subsections → Bullet points or numbered lists
        - Ensure logical flow: Objectives → Design → Population → Statistics → Schedule.

        2. **Table Preservation (VERY IMPORTANT)**
        - If the input contains tabular data, ALWAYS preserve it as a proper table.
        - Reformat messy tables into clean Markdown tables.
        - Do NOT convert tables into paragraphs.
        - Ensure columns are aligned and readable.

        3. **Clarity & Readability**
        - Rewrite for easy human understanding.
        - Break long paragraphs into:
            - Bullet points
            - Short structured lines
        - Avoid dense text blocks.

        4. **Professional Clinical Tone**
        - Maintain formal, regulatory-compliant language.
        - Follow clinical writing standards (ICH/FDA style).
        - Avoid casual phrasing.

        5. **Accuracy (NON-NEGOTIABLE)**
        - Do NOT change:
            - Medical meaning
            - Drug names, doses, endpoints
        - Only improve wording and structure.

        6. **Feedback Integration**
        - Carefully apply reviewer feedback.
        - If feedback asks:
            - "clarify" → simplify language
            - "expand" → add structured detail
            - "shorten" → remove redundancy

        7. **Formatting Rules**
        - Use:
            - Headings (##, ###)
            - Bullet points (-)
            - Numbered lists (1,2,3)
        - Maintain spacing between sections.
        - Avoid long continuous paragraphs.

        8. **Final Output Quality**
        - Output must be:
            - Clean
            - Structured
            - Easy to scan (like a clinical protocol or CSR)
        - The result should look ready for:
            - Documentation
            - PPT
            - UI display

        Rewrite the section below while preserving meaning and improving structure, readability, and formatting.
        """
        rewriter_prompt = (
            f"### Original Section:\n{original}\n\n"
            f"### Reviewer Feedback:\n{comment}\n\n"
            f"### User Revision (if provided):\n{revised}\n\n"
            "### Task:\n"
            "- Rewrite the section applying the feedback.\n"
            "- Improve structure using headings, bullet points, and tables where needed.\n"
            "- Preserve all medical and technical details.\n"
            "- Ensure tables remain properly formatted.\n"
            "- Output should be clean and human-readable.\n\n"
            "### Output:\n"
            "Provide only the final rewritten section in well-structured format."
        )
        if self._ollama.is_available():
            try:
                rewritten = self._ollama.chat(rewriter_prompt, system=system_prompt_feedback)
                score = self._scorer.score(section_id, rewritten, use_fallback=False)
                logger.debug(f"Rewritten section generated with {len(rewritten.split())} words")
                return rewritten, score
            except Exception as exc:
                if not allow_groq:
                    raise
                logger.warning(
                    f"Ollama (gpt-oss:120b) failed: {exc!r} "
                    f"— falling back to Groq (llama-3.3-70b-versatile)"
                )
        if allow_groq and self._groq.is_available():
            logger.info("Using Groq fallback (llama-3.3-70b-versatile)")
            rewritten = self._groq.chat(rewriter_prompt, system=system_prompt_feedback)
            score = self._scorer.score(section_id, rewritten, use_fallback=False)
            return rewritten, score
        
        text = revised.strip() if revised and revised.strip() else original
        return text, self._scorer.score(section_id, text)  # If all else fails, return the user's revision or the original text

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(
        self,
        section_title:   str,
        section_content: str,
        doc_type:        str = "Clinical Study Protocol",
    ) -> dict:
        """
        Validate a generated section using Groq llama-3.1-8b-instant.

        Returns:
            {
                "is_compliant": bool,
                "issues":  ["[CRITICAL] ...", "[WARNING] ..."],
                "raw_response": str,
                "validator": "groq-8b" | "rule-based",
            }
        """
        if not self._groq.is_available():
            return self._rule_based_validate(section_content)

        prompt = (
            f"Document type : {doc_type}\n"
            f"Section       : {section_title}\n\n"
            f"--- SECTION CONTENT ---\n"
            f"{section_content[:2000]}\n\n"
            "Review this section against ICH E6, FDA, and EMA requirements. "
            "List any compliance issues found."
        )
        try:
            raw    = self._groq.validation_chat(prompt, system=_VALIDATION_SYSTEM)
            issues = [
                line.strip() for line in raw.splitlines()
                if line.strip().startswith(("[CRITICAL]", "[WARNING]", "[INFO]"))
            ]
            return {
                "is_compliant":  raw.strip().upper() == "COMPLIANT" or len(issues) == 0,
                "issues":        issues,
                "raw_response":  raw,
                "validator":     "groq-8b",
            }
        except Exception as exc:
            logger.warning(f"Groq validation failed ({exc!r}) — rule-based fallback")
            return self._rule_based_validate(section_content)

    def validate_batch(self, sections: list, doc_type: str = "Clinical Study Protocol") -> list:
        """Validate a list of DocumentSection objects."""
        return [
            {"section_id": s.section_id, "title": s.title,
             **self.validate(s.title, s.content, doc_type)}
            for s in sections
        ]

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "ollama": {
                "available": self._ollama.is_available(),
                "model":     self._ollama.model,
                "host":      self._ollama.host,
            },
            "groq": {
                "available":       self._groq.is_available(),
                "fallback_model":  self._groq.model_name,
                "validator_model": "llama-3.1-8b-instant",
                "role":            "validator + fallback",
            },
            "active_generator": (
                "ollama" if self._ollama.is_available()
                else "groq"  if self._groq.is_available()
                else "template"
            ),
        }

    def is_available(self) -> bool:
        return self._ollama.is_available() or self._groq.is_available()

    def set_ollama_model(self, model: str) -> None:
        """Hot-swap Ollama model at runtime — no restart required."""
        self._ollama.switch_model(model)
        logger.info(f"LLMClient: Ollama model → '{model}'")


    # ── Confidence score ──────────────────────────────────────────────────────────────
    def get_confidence_score(self, response: str, use_fallback: bool = False) -> float:
        
        # Step 1: Check if the response is valid
        if not response or response.strip() == "":
            return 0.0  # No response is very low confidence

        # Step 2: Measure the length of the response
        length_score = self._get_length_score(response)

        # Step 3: Check for critical uncertainty words
        uncertainty_score = self._get_uncertainty_score(response)

        # Step 4: Adjust based on fallback model usage
        fallback_penalty = 0.2 if use_fallback else 0.0

        # Combine the factors to generate the final confidence score
        confidence = length_score - uncertainty_score - fallback_penalty

        # Ensure confidence score is between 0 and 1
        return max(0.0, min(confidence, 1.0))

    def _get_length_score(self, response: str) -> float:
        """
        Calculate the confidence based on the length of the response.
        The longer and more detailed the response, the higher the score.
        """
        length = len(response.split())
        if length < MIN_RESPONSE_LENGTH:
            return 0.2  # Short responses are less confident
        elif length > MAX_RESPONSE_LENGTH:
            return 1.0  # Long, detailed responses are highly confident
        return (length - MIN_RESPONSE_LENGTH) / (MAX_RESPONSE_LENGTH - MIN_RESPONSE_LENGTH)

    def _get_uncertainty_score(self, response: str) -> float:
        """
        Check for uncertainty phrases that could indicate lower confidence.
        """
        lower_response = response.lower()
        score = 0.0
        for word in CRITICAL_WORDS:
            if word in lower_response:
                score += 0.2  # Increase uncertainty score if any critical word is found
        return score

    def evaluate_multiple_responses(self, responses: list) -> float:
        """
        Evaluate confidence by comparing multiple responses. Consistency can improve confidence.
        """
        if len(responses) < 2:
            return self.get_confidence_score(responses[0])

        consistency_score = 0.0
        base_response = responses[0]

        for response in responses[1:]:
            if base_response.strip() == response.strip():
                consistency_score += 0.1  # More consistent responses add confidence

        return self.get_confidence_score(base_response) + consistency_score




    # ── Internal ──────────────────────────────────────────────────────────────

    def _rule_based_validate(self, text: str) -> dict:
        """Offline fallback when Groq is also unavailable."""
        import re
        checks = [
            (r"primary endpoint|primary outcome",
             "[WARNING] Primary endpoint may not be clearly defined"),
            (r"adverse event|SAE",
             "[INFO] Adverse event reporting language detected"),
            (r"ICH E6|GCP",
             "[INFO] GCP reference detected"),
        ]
        issues = [
            msg for pattern, msg in checks
            if not re.search(pattern, text, re.IGNORECASE)
            and ("[WARNING]" in msg or "[CRITICAL]" in msg)
        ]
        return {
            "is_compliant":  not any("[CRITICAL]" in i for i in issues),
            "issues":        issues,
            "raw_response":  "Rule-based check (Groq unavailable)",
            "validator":     "rule-based",
        }

    def _log_startup(self) -> None:
        s = self.status()
        ol = f"✓ {s['ollama']['model']}" if s["ollama"]["available"] else "✗ unavailable"
        gr = f"✓ {s['groq']['fallback_model']}" if s["groq"]["available"] else "✗ unavailable"
        logger.info(
            f"LLMClient ready | "
            f"Ollama(primary): {ol} | "
            f"Groq(validator/fallback): {gr} | "
            f"Active: {s['active_generator']}"
        )

    def __repr__(self) -> str:
        s = self.status()
        return (
            f"<LLMClient "
            f"primary=ollama({'✓' if s['ollama']['available'] else '✗'}) "
            f"fallback=groq({'✓' if s['groq']['available'] else '✗'}) "
            f"active={s['active_generator']}>"
        )
