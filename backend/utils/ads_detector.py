from adblockparser import AdblockRules
from urllib.parse import urlparse, parse_qs
from backend import settings
import pandas as pd

# load raw rules
with open(settings.EASY_LIST_PATH, encoding="utf-8") as f:
    raw_rules = f.readlines()
    rules = AdblockRules(raw_rules)

# Heuristic definitions
AD_DOMAINS = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "bing.com/aclick", "yahoo.com/ads", "duckduckgo.com/y.js",
    "adservice", "adsystem", "sponsored", "promo", "affiliate"
]

AD_QUERY_PARAMS = {"utm_source", "utm_campaign", "gclid", "fbclid", "clickid", "ref", "affid", "adid", "track"}

PROMO_KEYWORDS_IN_PATH = {"deal", "promo", "discount", "offer", "coupon", "bargain", "save"}
PROMO_DOMAINS = {"slickdeals.net", "retailmenot.com", "groupon.com", "offers.com", "coupon", "deal", "promo"}
PROMO_QUERY_PARAMS = {"promo", "code", "discount", "coupon", "dealid", "offer", "save"}


def is_ad_heuristic(url):
    parsed = urlparse(url)
    if any(domain in parsed.netloc.lower() for domain in AD_DOMAINS):
        return True
    if any(keyword in parsed.path.lower() for keyword in AD_DOMAINS):
        return True
    query_params = parse_qs(parsed.query)
    if AD_QUERY_PARAMS & set(query_params.keys()):
        return True
    return False


def is_ad_url(url):
    return rules.should_block(url) or is_ad_heuristic(url)


def is_promo_heuristic(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()
    query_params = parse_qs(parsed.query)

    if any(domain in netloc for domain in PROMO_DOMAINS):
        return True
    if any(keyword in path for keyword in PROMO_KEYWORDS_IN_PATH):
        return True
    if PROMO_QUERY_PARAMS & set(query_params.keys()):
        return True
    return False


def tag_ads_and_duplicates(df: pd.DataFrame, url_column: str = "url") -> pd.DataFrame:
    # Apply ad detection
    df = df.copy()
    df['is_ad'] = df[url_column].apply(is_ad_url)
    df['is_promo'] = df[url_column].apply(is_promo_heuristic)

    # Detect duplicates
    df['is_duplicate'] = df.duplicated(subset=url_column, keep=False)

    return df
