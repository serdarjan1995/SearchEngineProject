from fastapi import FastAPI, Query, BackgroundTasks, Depends
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session

from backend.download_nltk import download_nltk_packages
from db import get_db
from models import SearchQuery, SeScrapeResult, SearchQueryStats, SeScrapeTask, QueryKeyword, KeywordFreq
from tasks import scrape_search_engines
from utils.base_utils import md5_hash

download_nltk_packages()
app = FastAPI()


@app.get("/")
def index():
    return {"message": "OK"}


@app.get("/search")
def search(q: str = Query(..., min_length=1), p: int = Query(1, ge=1), ps: int = Query(10, ge=1, le=100),
           background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
    query_hash = md5_hash(q)

    offset = (p - 1) * ps
    result = db.query(SearchQuery).filter(SearchQuery.query_hash == query_hash).one_or_none()
    if not result:
        # Queue background processing
        background_tasks.add_task(scrape_search_engines, q)
        return {"status": "processing", "message": f"No cached result for '{q}'. Processing started."}

    # check query_stats exists
    query_stats = db.query(SearchQueryStats).filter(SearchQueryStats.query_hash == query_hash).one_or_none()
    if not query_stats:
        return {"status": "scraping", "message": f"No cached result for '{q}'. Scraping task is still in progress."}

    # scraping is finished: data is ready
    tasks = db.query(SeScrapeTask).filter_by(query_hash=query_hash).all()
    task_ids = [task.id for task in tasks]

    total_results = db.query(func.count(distinct(SeScrapeResult.url_hash))).filter(
        SeScrapeResult.se_scrape_task_id.in_(task_ids),
        SeScrapeResult.scraped == True,
    ).scalar()

    db_query = db.query(SeScrapeResult).filter(
        SeScrapeResult.se_scrape_task_id.in_(task_ids),
        SeScrapeResult.scraped == True,
    ).order_by("id")
    results = db_query.offset(offset).limit(ps).all()

    result_data = []
    query_keywords = db.query(QueryKeyword).filter_by(query_hash=query_hash).all()
    for result in results:
        search_term_freq = {}
        for query_keyword in query_keywords:
            keyword_freq = db.query(KeywordFreq).filter(
                KeywordFreq.url_hash == result.url_hash,
                KeywordFreq.keyword_hash == query_keyword.keyword_hash,
            ).one()
            search_term_freq[query_keyword.keyword] = keyword_freq.frequency
        data = {
            "id": result.id,
            "url": result.url,
            "url_hash": result.url_hash,
            "title": result.title,
            "search_term_freq": search_term_freq,
        }
        result_data.append(data)

    result = {
        "query": q,
        "stats": {
            "total_urls": query_stats.total_urls,
            "unique_urls": query_stats.unique_urls,
            "ad_urls": query_stats.ad_urls,
            "promo_urls": query_stats.promo_urls,
            "dupe_urls": query_stats.dupe_urls,
        },
        "total_results": total_results,
        "results": result_data
    }
    return {"status": "ok", "data": result}
