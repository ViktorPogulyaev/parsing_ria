import logging
import re

logger = logging.getLogger(__name__)


def extract_keywords(text: str, max_keywords: int = 15) -> list[str]:
    """Извлечение ключевых слов из текста"""
    if not text or len(text) < 50:
        return []
    try:
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        tokens = word_tokenize(text.lower(), language="russian")
        try:
            stop = set(stopwords.words("russian")) | set(stopwords.words("english"))
        except OSError:
            stop = set()

        words = [
            w for w in tokens
            if w.isalpha() and len(w) > 3 and w not in stop
        ]

        # Frequency-based selection
        freq: dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq, key=lambda w: freq[w], reverse=True)
        return sorted_words[:max_keywords]

    except Exception as exc:
        logger.debug("Keyword extraction failed: %s", exc)
        return _simple_keywords(text, max_keywords)


def generate_summary(text: str, sentence_count: int = 3) -> str | None:
    """Генерация обобщения текста используя sumy или fallback по первым предложениям."""
    if not text or len(text) < 200:
        return None
    try:
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.summarizers.lsa import LsaSummarizer

        parser = PlaintextParser.from_string(text, Tokenizer("russian"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, sentence_count)
        result = " ".join(str(s) for s in summary_sentences)
        return result or None
    except Exception:
        pass

    # Fallback: возвращаем первые N предложений
    return _first_sentences(text, sentence_count)


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Оценка времени чтения в минутах."""
    if not text:
        return 0
    word_count = len(text.split())
    return max(1, round(word_count / wpm))


# def detect_has_video(html: str) -> bool:
#     """Эвристическая проверка наличия видео в HTML."""
#     patterns = [
#         r"<video\b",
#         r"<iframe[^>]+youtube",
#         r"<iframe[^>]+vimeo",
#         r'class=["\'][^"\']*video',
#         r"jwplayer",
#         r"videojs",
#     ]
#     html_lower = html.lower()
#     return any(re.search(p, html_lower) for p in patterns)


# ---- private helpers ----

def _simple_keywords(text: str, max_keywords: int) -> list[str]:
    """Извлечение ключевых слов из текста"""
    words = re.findall(r"\b[а-яёА-ЯЁa-zA-Z]{4,}\b", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=lambda w: freq[w], reverse=True)[:max_keywords]


def _first_sentences(text: str, n: int) -> str | None:
    """Возвращаем первые N предложений из текста"""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    result = " ".join(sentences[:n])
    return result or None