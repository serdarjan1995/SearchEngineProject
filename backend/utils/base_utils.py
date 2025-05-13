import hashlib
import logging
import os
import nltk
import scrapers
from datetime import datetime, timezone
from settings import BASE_DIR

nltk.data.path.append(os.path.join(BASE_DIR, "static_data/nltk_data"))

datetime_now = lambda: datetime.now(timezone.utc).replace(tzinfo=None)

logger = logging.getLogger("SearchEngine")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s @ %(filename)s:%(funcName)s:%(lineno)d')
ch.setFormatter(formatter)
logger.addHandler(ch)

search_engines = {
    "google": scrapers.google_scraper,
    "yahoo": scrapers.yahoo_scraper,
    "bing": scrapers.bing_scraper,
    "duckduckgo": scrapers.duckduckgo_scraper,
}


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def split_query_to_keywords(query: str) -> list[str]:
    stop_words = set(nltk.corpus.stopwords.words("english"))
    word_tokens = set(nltk.word_tokenize(query.lower()))
    keywords = [word for word in word_tokens if word.isalpha() and word not in stop_words]
    keywords = list(set(keywords))
    return keywords
