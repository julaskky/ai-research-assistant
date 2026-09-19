import math
import re
from collections import Counter
from backend.app.services.metadata_service import normalize_extracted_text

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "has", "have", "in", "is", "it", "its", "of",
    "on", "or", "that", "the", "their", "this", "to", "was",
    "were", "will", "with", "we", "which", "these", "those",
    "can", "could", "may", "might", "should", "than", "then",
    "them", "they", "you", "your"
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]*\b", text.lower())

    return [
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 40
    ]


def summarize_text(text: str, max_sentences: int = 5) -> str:
    text = normalize_extracted_text(text)

    sentences = split_sentences(text)

    if not sentences:
        return text[:2000]

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    word_counts = Counter(tokenize(text))

    if not word_counts:
        return " ".join(sentences[:max_sentences])

    max_frequency = max(word_counts.values())

    normalized_frequencies = {
        word: count / max_frequency
        for word, count in word_counts.items()
    }

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        words = tokenize(sentence)

        if not words:
            continue

        score = sum(
            normalized_frequencies.get(word, 0)
            for word in words
        ) / math.sqrt(len(words))

        scored_sentences.append((score, index, sentence))

    top_sentences = sorted(
        scored_sentences,
        key=lambda item: item[0],
        reverse=True
    )[:max_sentences]

    top_sentences = sorted(
        top_sentences,
        key=lambda item: item[1]
    )

    return " ".join(
        sentence
        for _, _, sentence in top_sentences
    )


def split_into_chunks(
    text: str,
    chunk_size: int = 1200
) -> list[str]:
    words = text.split()

    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start:start + chunk_size])

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def cosine_similarity(
    query_vector: Counter,
    document_vector: Counter
) -> float:
    common_words = set(query_vector) & set(document_vector)

    numerator = sum(
        query_vector[word] * document_vector[word]
        for word in common_words
    )

    query_norm = math.sqrt(
        sum(value ** 2 for value in query_vector.values())
    )

    document_norm = math.sqrt(
        sum(value ** 2 for value in document_vector.values())
    )

    if query_norm == 0 or document_norm == 0:
        return 0.0

    return numerator / (query_norm * document_norm)


def retrieve_relevant_chunks(
    text: str,
    query: str,
    top_k: int = 3
) -> list[str]:
    text = normalize_extracted_text(text)

    chunks = split_into_chunks(text)
    
    query_tokens = Counter(tokenize(query))

    if not query_tokens:
        return chunks[:top_k]

    scored_chunks = []

    for chunk in chunks:
        chunk_tokens = Counter(tokenize(chunk))

        score = cosine_similarity(
            query_tokens,
            chunk_tokens
        )

        scored_chunks.append((score, chunk))

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]


def answer_from_context(
    query: str,
    context: str,
    max_sentences: int = 3
) -> str:
    relevant_sentences = split_sentences(context)

    query_tokens = Counter(tokenize(query))

    if not query_tokens:
        return "I could not identify meaningful terms in the question."

    scored_sentences = []

    for index, sentence in enumerate(relevant_sentences):
        sentence_tokens = Counter(tokenize(sentence))

        score = cosine_similarity(
            query_tokens,
            sentence_tokens
        )

        scored_sentences.append(
            (score, index, sentence)
        )

    scored_sentences.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = [
        item
        for item in scored_sentences[:max_sentences]
        if item[0] > 0
    ]

    if not selected:
        return (
            "I could not find information in the paper "
            "that directly addresses this question."
        )

    selected.sort(key=lambda item: item[1])

    return " ".join(
        sentence
        for _, _, sentence in selected
    )