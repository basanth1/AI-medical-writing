"""
Unit tests for GroqClient — no real API calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from backend.core.groq_client import GroqClient, GROQ_MODELS


class TestGroqClientInit:
    def test_no_key_sets_fallback(self):
        client = GroqClient(api_key="")
        assert not client.is_available()

    def test_model_resolution(self):
        client = GroqClient(api_key="")
        assert client.model_name == GROQ_MODELS["medical"]

    def test_fast_model_resolution(self):
        client = GroqClient(api_key="", model="fast")
        assert client.model_name == GROQ_MODELS["fast"]

    def test_repr(self):
        client = GroqClient(api_key="")
        r = repr(client)
        assert "GroqClient" in r
        # new repr shows "unavailable" instead of "no-key"
        assert "unavailable" in r or "no-key" in r


class TestGroqClientFallback:
    def setup_method(self):
        self.client = GroqClient(api_key="")   # no key → fallback

    def test_chat_returns_fallback(self):
        result = self.client.chat("Write a protocol intro for Oncology")
        assert "TEMPLATE CONTENT" in result or "GROQ_API_KEY" in result

    def test_call_shorthand(self):
        result = self.client("test prompt")
        assert isinstance(result, str) and len(result) > 0

    def test_batch_returns_list(self):
        results = self.client.batch(["prompt1", "prompt2"])
        assert isinstance(results, list)
        assert len(results) == 2

    def test_stream_yields(self):
        chunks = list(self.client.stream("test"))
        assert isinstance(chunks, list)
        assert len(chunks) > 0


class TestGroqClientWithMock:
    def setup_method(self):
        mock_groq = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Mock LLM response for clinical trial"
        mock_groq.chat.completions.create.return_value = MagicMock(
            choices=[mock_choice]
        )
        with patch("backend.core.groq_client.Groq", return_value=mock_groq):
            self.client = GroqClient(api_key="test-key-123")
        self.mock_groq = mock_groq

    def test_chat_calls_groq(self):
        result = self.client.chat("Write protocol intro")
        assert result == "Mock LLM response for clinical trial"
        self.mock_groq.chat.completions.create.assert_called_once()

    def test_chat_with_system(self):
        result = self.client.chat_with_system("You are a medical writer", "Write intro")
        assert result == "Mock LLM response for clinical trial"

    def test_is_available(self):
        assert self.client.is_available()

    def test_count_tokens(self):
        assert self.client.count_tokens("hello world") == 2  # 11 chars // 4

    def test_batch_calls_multiple(self):
        results = self.client.batch(["p1", "p2", "p3"], delay=0)
        assert len(results) == 3
        assert self.mock_groq.chat.completions.create.call_count == 3
