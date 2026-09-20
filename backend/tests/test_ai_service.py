from types import SimpleNamespace

import backend.app.services.ai_service as ai_service


def test_summarize_with_gemini_uses_configured_client(monkeypatch):
    class FakeInteractions:
        def create(self, model, input):
            assert model == ai_service.GEMINI_MODEL
            assert "academic research assistant" in input.lower()

            return SimpleNamespace(
                output_text="This is a research-focused summary."
            )

    fake_client = SimpleNamespace(
        interactions=FakeInteractions()
    )

    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        fake_client
    )

    result = ai_service.summarize_with_gemini(
        "This is a sample academic paper."
    )

    assert result == "This is a research-focused summary."


def test_answer_with_gemini_uses_retrieved_context(monkeypatch):
    class FakeInteractions:
        def create(self, model, input):
            assert model == ai_service.GEMINI_MODEL
            assert "What dataset was used?" in input
            assert "3,000 annotated lesson objectives" in input

            return SimpleNamespace(
                output_text="The study used 3,000 annotated lesson objectives."
            )

    fake_client = SimpleNamespace(
        interactions=FakeInteractions()
    )

    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        fake_client
    )

    result = ai_service.answer_with_gemini(
        "What dataset was used?",
        "The study used 3,000 annotated lesson objectives."
    )

    assert (
        result
        == "The study used 3,000 annotated lesson objectives."
    )


def test_summarize_with_gemini_requires_client(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        None
    )

    try:
        ai_service.summarize_with_gemini(
            "Sample academic paper text."
        )
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "Gemini API client is not configured" in str(exc)


def test_answer_with_gemini_requires_client(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        None
    )

    try:
        ai_service.answer_with_gemini(
            "What was the result?",
            "The result was 91.8%."
        )
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "Gemini API client is not configured" in str(exc)


def test_answer_with_gemini_handles_empty_question(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        SimpleNamespace()
    )

    result = ai_service.answer_with_gemini(
        "",
        "Some retrieved context."
    )

    assert result == "No question was provided."


def test_answer_with_gemini_handles_empty_context(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "gemini_client",
        SimpleNamespace()
    )

    result = ai_service.answer_with_gemini(
        "What was the result?",
        ""
    )

    assert (
        result
        == "I could not find relevant information "
           "in the paper."
    )
    # This test requires the Gemini client to be configured.
    # If it is not configured, the function raises before
    # checking the context.
    assert (
        result
        == "I could not find relevant information "
           "in the paper."
    )