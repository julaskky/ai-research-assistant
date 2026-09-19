from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from all pages of a PDF document."""
    text = []

    with pymupdf.open(file_path) as document:
        for page in document:
            text.append(page.get_text())

    return "\n".join(text).strip()


def extract_title_from_pdf(file_path: Path) -> str:
    """Extract the paper title from the first page of a PDF document."""
    with pymupdf.open(file_path) as document:
        first_page_text = document[0].get_text()

    lines = [
        line.strip()
        for line in first_page_text.splitlines()
        if line.strip()
    ]

    try:
        article_index = lines.index("Article")
    except ValueError:
        return ""

    title_lines = []

    for line in lines[article_index + 1:]:
        # Academic author lines commonly end with a numeric affiliation marker.
        if title_lines and line[-1].isdigit():
            break

        title_lines.append(line)

    return " ".join(title_lines).strip()




def extract_authors_from_pdf(file_path: Path) -> str:
    """Extract author names from the citation block on the first page."""
    with pymupdf.open(file_path) as document:
        first_page_text = document[0].get_text()

    lines = [
        line.strip()
        for line in first_page_text.splitlines()
        if line.strip()
    ]

    try:
        citation_index = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("Citation:")
        )
    except StopIteration:
        return ""

    author_lines = []

    first_line = lines[citation_index]

    authors = first_line.replace("Citation:", "").strip()

    if authors:
        author_lines.append(authors)

    for line in lines[citation_index + 1:]:
        if line.startswith("eXplainable"):
            break

        author_lines.append(line)

    return " ".join(author_lines).strip()