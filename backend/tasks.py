from datetime import timedelta

from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session

from db import with_db
from scrapers import url_scrape_processor
from utils.ads_detector import is_ad_url, is_promo_heuristic
from models import SearchQuery, QueryKeyword, SeScrapeTask, SeScrapeResult, UrlScrapeResult, KeywordFreq, \
    SearchQueryStats, QueryRank
from utils.base_utils import logger, md5_hash, datetime_now, split_query_to_keywords, search_engines


MAX_PAGE_SCRAPE = 25


@with_db
def scrape_search_engines(query: str, db: Session):
    logger.info(f"[STEP 1:] Creating/Updating SearchQuery and QueryKeyword for: {query=}")
    query_hash = md5_hash(query)

    db_search_query = db.query(SearchQuery).filter_by(query_hash=query_hash).first()

    # check if updated last 7 days
    seven_days_ago = datetime_now() - timedelta(days=7)
    if db_search_query and db_search_query.updated_at > seven_days_ago:
        return  # avoid rescraping query if it is updated in last 7 days

    if db_search_query:
        refresh = True
    else:
        refresh = False
        search_query = SearchQuery(
            query=query,
            query_hash=query_hash,
        )
        db.add(search_query)
        keywords = split_query_to_keywords(query)
        for keyword in keywords:
            query_keyword = QueryKeyword(
                keyword=keyword,
                keyword_hash=md5_hash(keyword),
                query_hash=query_hash
            )
            db.add(query_keyword)

        db.commit()

    create_tasks(query, query_hash, refresh)


@with_db
def create_tasks(query: str, query_hash: str, refresh: bool, db: Session):
    logger.info(f"[STEP 2] Creating/Updating SeScrapeTask for: {query}")
    if refresh:
        # refresh already existing scraped data
        update_data = {
            SeScrapeTask.scraped: False,
            SeScrapeTask.scraped_at: None,
            SeScrapeTask.scraped_urls_cnt: 0,
            SeScrapeTask.updated_at: datetime_now()
        }
        db.query(SeScrapeTask).filter(
            SeScrapeTask.query_hash == query_hash
        ).update(update_data, synchronize_session=True)
        db.commit()
        tasks = db.query(SeScrapeTask).filter_by(query_hash=query_hash).all()
        run_se_scrape_tasks(query, query_hash, refresh, tasks)
        return

    # create a new SeScrapeTask
    tasks = []
    for se_engine in search_engines.keys():
        se_scrape_task = SeScrapeTask(
            query_hash=query_hash,
            engine=se_engine,
            scraped=False,
            scraped_at=None,
            scraped_urls_cnt=0,
        )
        db.add(se_scrape_task)
        tasks.append(se_scrape_task)
    db.commit()
    run_se_scrape_tasks(query, query_hash, refresh, tasks)


@with_db
def run_se_scrape_tasks(query: str, query_hash: str, refresh: bool, tasks: list[SeScrapeTask], db: Session):
    logger.info(f"[STEP 3] Creating/Updating SeScrapeResult for: {query}")
    if refresh:
        # TODO implement refresh scrape task results
        return

    all_unique_urls = {}
    for task in tasks:
        scraper = search_engines[task.engine]
        results = scraper.get_search_results(query, max_pages=MAX_PAGE_SCRAPE)
        unique_urls = set()
        for result in results:
            title = result["title"]
            url = result["url"]
            url_hash = md5_hash(url)
            all_unique_urls[url_hash] = url
            is_ad = is_ad_url(url)
            is_promo = is_promo_heuristic(url)
            is_dupe = True
            if url not in unique_urls:
                unique_urls.add(url)
                is_dupe = False

            # if the url is already in all_unique_urls, then this is dupe accross search engines
            if url in all_unique_urls:
                is_dupe = True

            se_scrape_result = SeScrapeResult(
                se_scrape_task_id=task.id,
                url=url,
                url_hash=url_hash,
                title=title,
                is_ad=is_ad,
                is_promo=is_promo,
                is_dupe=is_dupe,
                scraped=False,
                scraped_at=None,
            )
            db.add(se_scrape_result)
        task.scraped = True
        task.scraped_at = datetime_now()
        task.scraped_urls_cnt = len(unique_urls)
        db.commit()

    run_url_scrape_tasks(query, query_hash, refresh, all_unique_urls)


@with_db
def run_url_scrape_tasks(query: str, query_hash: str, refresh: bool, all_unique_urls: dict, db: Session):
    logger.info(f"[STEP 4] Creating/Updating UrlScrapeResult for: {query}")
    if refresh:
        # TODO implement refresh url scrape task results
        return

    successful_urls = {}
    for url_hash, url in all_unique_urls.items():
        try:
            result = url_scrape_processor.process_url(url)
        except Exception as e:
            logger.error(f"Failed to scrape content for url: {url}. Error: {e}")
            result = {"url": url, "text": "", "info_type": "error", "success": False}

        is_successful = result["success"]
        if is_successful:
            successful_urls[url_hash] = url
        url_scrape_result = UrlScrapeResult(
            url_hash=url_hash,
            text_content=result["text"],
            info_type=result["info_type"],
            is_successful=is_successful,
        )
        db.add(url_scrape_result)
        if is_successful:
            db.query(SeScrapeResult).filter_by(url_hash=url_hash).update({
                SeScrapeResult.scraped: True,
                SeScrapeResult.scraped_at: datetime_now()
            })
    db.commit()

    count_keyword_freq(query, query_hash, refresh, successful_urls)


@with_db
def count_keyword_freq(query: str, query_hash: str, refresh: bool, successful_urls: dict, db: Session):
    logger.info(f"[STEP 5] Creating/Updating KeywordFreq for: {query}")
    # get query keywords
    keywords = db.query(QueryKeyword).filter_by(query_hash=query_hash).all()

    for url_hash, url in successful_urls.items():
        url_scrape_result = db.query(UrlScrapeResult).filter_by(url_hash=url_hash).first()
        if not url_scrape_result:
            continue

        for kw in keywords:
            keyword = kw.keyword
            keyword_hash = kw.keyword_hash
            keyword_freq = url_scrape_result.text_content.lower().count(keyword)
            keyword_freq_result = db.query(KeywordFreq).filter_by(keyword_hash=keyword_hash, url_hash=url_hash).first()
            if keyword_freq_result:
                keyword_freq_result.keyword_freq = keyword_freq
                keyword_freq_result.updated_at = datetime_now()
            else:
                keyword_freq_result = KeywordFreq(
                    keyword_hash=keyword_hash,
                    url_hash=url_hash,
                    frequency=keyword_freq,
                )
                db.add(keyword_freq_result)
        db.commit()

    create_search_query_stats_task(query, query_hash, refresh)


@with_db
def create_search_query_stats_task(query: str, query_hash: str, refresh: bool, db: Session):
    logger.info(f"[STEP 6] Creating/Updating QueryStats for: {query}")

    tasks = db.query(SeScrapeTask).filter_by(query_hash=query_hash).all()

    task_ids = [task.id for task in tasks]

    result = db.query(
        func.count(distinct(SeScrapeResult.url_hash)).label("distinct_urls"),
        func.count(case((SeScrapeResult.is_ad == True, 1))).label("ad_count"),
        func.count(case((SeScrapeResult.is_promo == True, 1))).label("promo_count"),
        func.count(case((SeScrapeResult.is_dupe == True, 1))).label("dupe_count"),
    ).filter(
        SeScrapeResult.se_scrape_task_id.in_(task_ids)
    ).one()

    total_urls = db.query(func.count()).filter(
        SeScrapeResult.se_scrape_task_id.in_(task_ids)
    ).scalar()

    search_query_stats = SearchQueryStats(
        query_hash=query_hash,
        unique_urls=result.distinct_urls,
        total_urls=total_urls,
        ad_urls=result.ad_count,
        promo_urls=result.promo_count,
        dupe_urls=result.dupe_count,
    )

    db.add(search_query_stats)
    db.commit()

    create_ranking(query, query_hash, refresh)


@with_db
def create_ranking(query: str, query_hash: str, refresh: bool, db: Session):
    logger.info(f"[STEP 7] Creating/Updating QueryRank for: {query}")

    tasks = db.query(SeScrapeTask).filter_by(query_hash=query_hash).all()
    task_ids = [task.id for task in tasks]

    subquery = db.query(
        func.min(SeScrapeResult.id).label("min_id")
    ).filter(
        SeScrapeResult.se_scrape_task_id.in_(task_ids),
        SeScrapeResult.scraped == True,
        SeScrapeResult.url_hash.is_not(None)
    ).group_by(SeScrapeResult.url_hash).subquery()

    # Main query to get full rows, joining with subquery
    db_query = db.query(SeScrapeResult).join(
        subquery, SeScrapeResult.id == subquery.c.min_id
    )

    all_results = db_query.all()

    items = []
    query_keywords = db.query(QueryKeyword).filter_by(query_hash=query_hash).all()
    for result in all_results:
        search_term_freq = {}
        for query_keyword in query_keywords:
            keyword_freq = db.query(KeywordFreq).filter(
                KeywordFreq.url_hash == result.url_hash,
                KeywordFreq.keyword_hash == query_keyword.keyword_hash,
            ).one()
            search_term_freq[query_keyword.keyword] = keyword_freq.frequency
        data = {
            "url_hash": result.url_hash,
            "query_hash": query_hash,
            "search_term_freq": search_term_freq,
            "total_matches": sum(list(search_term_freq.values())),
        }
        items.append(data)

    items = sorted(items, key=lambda x: x["total_matches"], reverse=True)
    for i, item in enumerate(items):
        db.add(QueryRank(
            query_hash=item["query_hash"],
            url_hash=item["url_hash"],
            rank=i,
            total_matches=item["total_matches"],
        ))
    db.commit()
    logger.info(f"[] Finished processing: {query}")
