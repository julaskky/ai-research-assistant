from pathlib import Path

from backend.app.services.metadata_service import (
    extract_abstract,
    extract_doi,
    extract_keywords,
    extract_publication_year,
    get_pdf_metadata,
)


PDF_PATH = Path("data/computers-14-00494.pdf")


def test_extract_doi():
    text = """
    This study presents a new framework.
    DOI: 10.3390/computers14040094
    """

    assert extract_doi(text) == "10.3390/computers14040094"


def test_extract_doi_without_label():
    text = """
    Published online.
    https://doi.org/10.1234/example.2026
    """

    assert extract_doi(text) == "10.1234/example.2026"


def test_extract_doi_returns_none_when_missing():
    text = "This document does not contain a DOI."

    assert extract_doi(text) is None


def test_extract_publication_year():
    text = """
    Published in 2024.
    The study evaluates an artificial intelligence framework.
    """

    assert extract_publication_year(text) == 2024


def test_extract_publication_year_returns_none_when_missing():
    text = "No publication date is available in this document."

    assert extract_publication_year(text) is None


def test_extract_abstract():
    text = """
    Title of the Paper

    Abstract
    This paper proposes a generic metadata extraction framework
    for academic research documents.

    Keywords
    artificial intelligence; metadata extraction; research

    Introduction
    Academic papers use many different formats.
    """

    result = extract_abstract(text)

    assert result is not None
    assert "generic metadata extraction framework" in result


def test_extract_keywords():
    text = """
    Abstract
    This paper presents a research assistant.

    Keywords
    artificial intelligence; software engineering; research assistant

    Introduction
    This section introduces the study.
    """

    result = extract_keywords(text)

    assert result is not None
    assert "artificial intelligence" in result
    assert "software engineering" in result


def test_extract_abstract_returns_none_when_missing():
    text = """
    Title of the Paper

    Introduction
    This paper discusses academic research.
    """

    assert extract_abstract(text) is None


def test_get_pdf_metadata():
    metadata = get_pdf_metadata(PDF_PATH)

    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "authors" in metadata
    assert "subject" in metadata
    assert "keywords" in metadata


def test_extract_abstract_normalizes_pdf_hyphenation():
    text = """
    Abstract
    This paper presents an auto-
    mated framework for human-in-the-loop
    educational systems.

    Keywords
    artificial intelligence

    Introduction
    This section introduces the study.
    """

    result = extract_abstract(text)

    assert result is not None
    assert "automated framework" in result
    assert "human-in-the-loop" in result



def test_extract_abstract_stops_at_inline_keywords():
    text = """
    Abstract
    This paper presents a generic research assistant.
    Keywords: artificial intelligence; software engineering

    Introduction
    This section introduces the study.
    """

    result = extract_abstract(text)

    assert result is not None
    assert "generic research assistant" in result
    assert "Keywords:" not in result