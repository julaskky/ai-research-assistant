import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "local"
)


gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={"api_version": "v1"}
    )



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
    chunk_size: int = 900
) -> list[str]:
    """
    Split academic text into sentence-aware chunks.

    Chunks are created from complete sentences rather than
    arbitrary word boundaries.
    """

    sentences = split_sentences(text)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_word_count = len(sentence.split())

        # If adding this sentence would exceed the target size,
        # save the current chunk first.
        if (
            current_chunk
            and current_word_count + sentence_word_count > chunk_size
        ):
            chunks.append(" ".join(current_chunk))

            current_chunk = []
            current_word_count = 0

        current_chunk.append(sentence)
        current_word_count += sentence_word_count

    # Add the final chunk.
    if current_chunk:
        chunks.append(" ".join(current_chunk))

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

    # Terms that often indicate useful academic evidence.
    priority_terms = {
        "dataset",
        "data",
        "method",
        "methodology",
        "result",
        "results",
        "performance",
        "accuracy",
        "f1",
        "auc",
        "evaluation",
        "experiment",
        "finding",
        "findings",
        "conclusion",
    }

    query_lower = query.lower()

    for chunk in chunks:
        chunk_tokens = Counter(tokenize(chunk))

        similarity_score = cosine_similarity(
            query_tokens,
            chunk_tokens
        )

        chunk_lower = chunk.lower()

        # Give a small boost when important terms from the
        # question appear explicitly in the retrieved chunk.
        keyword_boost = sum(
            1
            for term in priority_terms
            if term in query_lower and term in chunk_lower
        )

        score = similarity_score + (
            keyword_boost * 0.05
        )

        scored_chunks.append(
            (score, chunk)
        )

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












def summarize_with_gemini(
    text: str,
    max_words: int = 250
) -> str:
    """
    Generate a research-paper summary using Gemini.
    """

    if gemini_client is None:
        raise RuntimeError(
            "Gemini API client is not configured."
        )

    if not text.strip():
        return "No text was provided for summarization."

    prompt = f"""
You are an academic research assistant.

Summarize the following academic paper text for a researcher.

Requirements:
- Focus on the research problem, objective, methodology,
  dataset/data, main findings, and conclusion.
- Ignore pseudocode, code listings, file paths, configuration
  details, table formatting, and repetitive implementation details.
- Do not invent information that is not present in the text.
- Preserve important quantitative results when they are explicitly
  reported.
- Use clear academic language.
- Produce a coherent summary rather than a list of unrelated sentences.
- Keep the summary below {max_words} words.

Paper text:
{text}
"""

    response = gemini_client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt
    )

    return response.output_text.strip()






def answer_with_gemini(
    question: str,
    context: str
) -> str:
    """
    Generate a research-grounded answer using Gemini
    and retrieved passages from an academic paper.
    """

    if gemini_client is None:
        raise RuntimeError(
            "Gemini API client is not configured."
        )

    if not question.strip():
        return "No question was provided."

    if not context.strip():
        return (
            "I could not find relevant information "
            "in the paper."
        )

    prompt = f"""
You are an academic research assistant.

Answer the user's question using ONLY the information
explicitly stated in the retrieved passages from the academic paper.

Strict grounding rules:
- Use only facts explicitly stated in the retrieved passages.
- Do not infer, interpret, explain implications, or draw conclusions
  that are not explicitly stated in the retrieved passages.
- Do not add information from the broader paper or your general knowledge.
- Do not introduce causal explanations unless they are explicitly stated.
- Do not characterize results as indicating, suggesting, demonstrating,
  confirming, or implying something unless the retrieved passages
  explicitly make that statement.
- Preserve quantitative results exactly as stated.
- Prioritize the information directly requested by the user's question.
- Do not include secondary results, ablation studies, training dynamics,
  per-class analysis, or other additional details unless they are necessary
  to answer the question.
- If the retrieved passages do not contain enough information to answer
  part of the question, clearly say that the retrieved passages do not
  provide that information.
- Answer only the question that was asked.
- Do not add unrelated observations or background information.
- Use professional academic language.
- Do not mention that you are an AI unless necessary.

User question:
{question}

Retrieved passages:
{context}
"""

    response = gemini_client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt
    )

    return response.output_text.strip()