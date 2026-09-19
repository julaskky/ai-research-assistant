import re
from pathlib import Path
from typing import Optional
from wordfreq import zipf_frequency
import pymupdf


DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
    re.IGNORECASE
)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")


def get_pdf_metadata(file_path: Path) -> dict:
    """Return embedded metadata stored inside a PDF."""
    with pymupdf.open(file_path) as document:
        metadata = document.metadata or {}

    return {
        "title": clean_value(metadata.get("title")),
        "authors": clean_value(metadata.get("author")),
        "subject": clean_value(metadata.get("subject")),
        "keywords": clean_value(metadata.get("keywords")),
    }


def clean_value(value: Optional[str]) -> Optional[str]:
    """Normalize an extracted metadata value."""
    if not value:
        return None

    value = " ".join(value.split())

    return value if value else None


def normalize_extracted_text(text: Optional[str]) -> Optional[str]:
    """Normalize common PDF extraction artifacts."""
    if not text:
        return None

    def replace_hyphenated_match(match: re.Match) -> str:
        """Decide whether a hyphen should be removed."""
        first_word = match.group(1)
        second_word = match.group(2)

        joined_word = f"{first_word}{second_word}"
        hyphenated_word = f"{first_word}-{second_word}"

        joined_frequency = zipf_frequency(
            joined_word,
            "en"
        )

        hyphenated_frequency = zipf_frequency(
            hyphenated_word,
            "en"
        )

        # Remove the hyphen only when the joined form is clearly
        # more likely to be a normal English word.
        if (
            joined_frequency >= 3.0
            and joined_frequency > hyphenated_frequency
        ):
            return joined_word

        return hyphenated_word

    # Handle words that were split by PDF line extraction, such as:
    # "auto- mated" -> "automated"
    # "taxonomy- conditioned" -> "taxonomy-conditioned"
    text = re.sub(
        r"\b([A-Za-z]+)-\s+([a-z]+)\b",
        replace_hyphenated_match,
        text
    )

    # Normalize whitespace.
    text = " ".join(text.split())

    return text if text else None



def extract_doi(text: str) -> Optional[str]:
    """Extract the first DOI-like identifier from document text."""
    match = DOI_PATTERN.search(text)

    if not match:
        return None

    doi = match.group(0).rstrip(".,;)]}")

    return doi


def extract_publication_year(text: str) -> Optional[int]:
    """
    Extract a plausible publication year from document text.

    The function searches for years from 1900 to the current year.
    """
    years = []

    for match in YEAR_PATTERN.finditer(text):
        year = int(match.group(0))

        if 1900 <= year <= 2100:
            years.append(year)

    if not years:
        return None

    return years[0]


def extract_section(
    text: str,
    section_names: list[str],
    stop_sections: list[str]
) -> Optional[str]:
    """
    Extract text between a section heading and the next recognized section.

    The function supports both standalone headings such as:

        Keywords

    and headings followed by content on the same line, such as:

        Keywords: artificial intelligence; software engineering

    Returns None if the requested section cannot be found or contains no text.
    """
    lines = text.splitlines()

    start_index = None

    # Locate the requested section heading.
    for index, line in enumerate(lines):
        stripped_line = line.strip()
        normalized = stripped_line.lower().rstrip(":.")

        if normalized in section_names:
            start_index = index + 1
            break

    if start_index is None:
        return None

    extracted_lines = []

    # Extract content until the next recognized section.
    for line in lines[start_index:]:
        stripped_line = line.strip()

        if not stripped_line:
            continue

        normalized = stripped_line.lower().rstrip(":.")

        # Stop at a standalone section heading.
        if normalized in stop_sections:
            break

        # Stop when a section heading is followed by content
        # on the same line, for example:
        # "Keywords: artificial intelligence"
        # "Keywords — artificial intelligence"
        # "Keywords - artificial intelligence"
        is_stop_section = any(
            normalized.startswith(section)
            and (
                normalized == section
                or normalized[len(section):].lstrip().startswith(
                    (":", "—", "-")
                )
            )
            for section in stop_sections
        )

        if is_stop_section:
            break

        extracted_lines.append(stripped_line)

    if not extracted_lines:
        return None

    return normalize_extracted_text(" ".join(extracted_lines))


def extract_abstract(text: str) -> Optional[str]:
    """Extract an abstract using common academic section headings."""
    return extract_section(
        text=text,
        section_names=["abstract"],
        stop_sections=[
            "keywords",
            "key words",
            "introduction",
            "1 introduction",
            "1. introduction",
        ],
    )


def extract_keywords(text: str) -> Optional[str]:
    """Extract keywords using common academic section headings."""
    return extract_section(
        text=text,
        section_names=[
            "keywords",
            "key words",
            "index terms",
            "index terms—",
        ],
        stop_sections=[
            "introduction",
            "1 introduction",
            "1. introduction",
        ],
    )


def extract_metadata(file_path: Path) -> dict:
    """
    Extract generic bibliographic metadata from a PDF.

    The function combines embedded PDF metadata with
    text-based extraction strategies.
    """
    with pymupdf.open(file_path) as document:
        text = "\n".join(page.get_text() for page in document)

    pdf_metadata = get_pdf_metadata(file_path)

    return {
        "title": pdf_metadata.get("title"),
        "authors": pdf_metadata.get("authors"),
        "abstract": extract_abstract(text),
        "publication_year": extract_publication_year(text),
        "doi": extract_doi(text),
        "journal": None,
        "keywords": (
            pdf_metadata.get("keywords")
            or extract_keywords(text)
        ),
    }