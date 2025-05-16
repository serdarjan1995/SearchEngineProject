from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship, declarative_base

from utils.base_utils import datetime_now

Base = declarative_base()


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(BigInteger, primary_key=True)
    query = Column(String(255))
    query_hash = Column(String(50), unique=True)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    # Relationships
    keywords = relationship("QueryKeyword", back_populates="search_query")
    scrape_tasks = relationship("SeScrapeTask", back_populates="search_query")
    stats = relationship("SearchQueryStats", back_populates="search_query", uselist=False)  #

    # Fix: Use primaryjoin instead of ForeignKey
    # stats = relationship(
    #     "SearchQueryStats",
    #     primaryjoin="SearchQuery.query_hash == foreign(SearchQueryStats.query_hash)",
    #     backref="search_query",
    #     lazy='dynamic'
    # )


class SearchQueryStats(Base):
    __tablename__ = "search_query_stats"

    id = Column(BigInteger, primary_key=True)
    query_hash = Column(String(255), ForeignKey("search_queries.query_hash"))  # No FK, but join is done manually
    unique_urls = Column(Integer)
    total_urls = Column(Integer)
    unscraped_urls = Column(Integer)
    ad_urls = Column(Integer)
    promo_urls = Column(Integer)
    dupe_urls = Column(Integer)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    search_query = relationship("SearchQuery", back_populates="stats")


class QueryKeyword(Base):
    __tablename__ = "query_keywords"

    id = Column(BigInteger, primary_key=True)
    keyword = Column(String(255))
    keyword_hash = Column(String(50))
    query_hash = Column(String(255), ForeignKey("search_queries.query_hash"))
    created_at = Column(DateTime, default=datetime_now)

    search_query = relationship("SearchQuery", back_populates="keywords")

    __table_args__ = (
        UniqueConstraint('keyword_hash', 'query_hash', name='uq_keyword_query_hash'),
    )

    # query = relationship(
    #     "SearchQuery",
    #     primaryjoin="foreign(QueryKeyword.query_hash) == SearchQuery.query_hash",
    #     backref="keywords"
    # )


class SeScrapeTask(Base):
    __tablename__ = "se_scrape_tasks"

    id = Column(BigInteger, primary_key=True)
    query_hash = Column(String(50), ForeignKey("search_queries.query_hash"))
    engine = Column(String(50))
    scraped = Column(Boolean, default=False)
    scraped_at = Column(DateTime, nullable=True)
    scraped_urls_cnt = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    search_query = relationship("SearchQuery", back_populates="scrape_tasks")
    scrape_results = relationship("SeScrapeResult", back_populates="scrape_task")

    # Explicit join to SearchQuery
    # query = relationship(
    #     "SearchQuery",
    #     primaryjoin="foreign(ScrapeTask.query_hash) == SearchQuery.query_hash",
    #     backref="scrape_tasks"
    # )


class SeScrapeResult(Base):
    __tablename__ = "se_scrape_results"

    id = Column(BigInteger, primary_key=True)
    se_scrape_task_id = Column(BigInteger, ForeignKey("se_scrape_tasks.id"))
    url = Column(Text)
    url_hash = Column(String(50))
    title = Column(Text)
    is_ad = Column(Boolean, default=False)
    is_promo = Column(Boolean, default=False)
    is_dupe = Column(Boolean, default=False)
    scraped = Column(Boolean, default=False)
    scraped_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    scrape_task = relationship("SeScrapeTask", back_populates="scrape_results")

    url_scrape_result = relationship(
        "UrlScrapeResult",
        back_populates="se_scrape_results",
        primaryjoin="foreign(SeScrapeResult.url_hash)==UrlScrapeResult.url_hash"
    )

    # task = relationship(
    #     "ScrapeTask",
    #     primaryjoin="foreign(ScrapeResult.se_scrape_task_id) == ScrapeTask.id",
    #     backref="results"
    # )


class UrlScrapeResult(Base):
    __tablename__ = "url_scrape_results"

    id = Column(BigInteger, primary_key=True)
    url_hash = Column(String(50))
    text_content = Column(MEDIUMTEXT)
    info_type = Column(String(50))
    is_successful = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    se_scrape_results = relationship(
        "SeScrapeResult",
        back_populates="url_scrape_result",
        primaryjoin="UrlScrapeResult.url_hash==foreign(SeScrapeResult.url_hash)"
    )


class KeywordFreq(Base):
    __tablename__ = "keyword_freq"

    id = Column(BigInteger, primary_key=True)
    keyword_hash = Column(String(50))
    url_hash = Column(String(50))
    frequency = Column(Integer)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    keywords = relationship(
        "QueryKeyword",
        primaryjoin="KeywordFreq.keyword_hash==foreign(QueryKeyword.keyword_hash)"
    )

    url = relationship(
        "SeScrapeResult",
        primaryjoin="KeywordFreq.url_hash==foreign(SeScrapeResult.url_hash)"
    )


class QueryRank(Base):
    __tablename__ = "query_rank"

    id = Column(BigInteger, primary_key=True)
    query_hash = Column(String(50), ForeignKey("search_queries.query_hash"))
    url_hash = Column(String(50))
    rank = Column(Integer)
    total_matches = Column(Integer)
    updated_at = Column(DateTime, default=datetime_now)
    created_at = Column(DateTime, default=datetime_now)

    search_query = relationship("SearchQuery")
