import json
import re
from typing import Optional
from curl_cffi import requests

from scrapers.base_scraper import BaseScraper


class DuckDuckGoScraper(BaseScraper):
    BASE_URL = "https://duckduckgo.com"
    SEARCH_URL = "https://links.duckduckgo.com/d.js"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def get_cookies(self):
        pass

    def get_vqd_param(self, q: str) -> Optional[str]:
        """ extract vqd value via sending same search term query to duckduckgo.com """
        params = {
            "q": q
        }
        response = requests.get(self.BASE_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES,
                                headers=self.HEADERS, params=params)
        re_vqd_cookie = re.compile(r"vqd=\"?([\d\-]+)\"?")
        vqd_cookie = re_vqd_cookie.search(response.text)
        if vqd_cookie:
            return vqd_cookie.group(1)

        self.logger.error("vqd cookie not found")
        return None

    def get_search_results(self, search_query: str, max_pages: int = 10):
        """ get search results """

        vqd_param = self.get_vqd_param(search_query)
        all_links = []
        for page in range(1, max_pages + 1):
            start = (page - 1) * 10
            params = {
                "q": search_query,
                "s": start,
                "vqd": vqd_param,
            }
            response = requests.get(
                self.SEARCH_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES, headers=self.HEADERS,
                cookies=self.COOKIES, params=params
            )

            if response.status_code != 200:
                self.logger.error(f"Page {page} failed status code: {response.status_code}")
                continue

            links = self.extract_links_from_response(response)
            self.logger.info(f"Page {page} Extracted {len(links)} links")
            all_links.extend(links)

        self.logger.info(f"Total links {len(all_links)}")
        return all_links

    @staticmethod
    def extract_links_from_response(response: requests.Response):
        """ extracts links from response """
        re_data = re.compile(r"DDG\.pageLayout\.load\('d',(\[.*\])\)")

        data = re_data.search(response.text)

        if not data:
            raise Exception('data not found')

        data = data.group(1)
        data_json = json.loads(data)
        links = []
        for entry in data_json:
            if not entry.get("u") or not entry.get("t"):
                continue

            link = {
                "url": entry["u"],
                "title": entry["t"],
            }
            links.append(link)

        return links


if __name__ == "__main__":
    # proxy = "http://127.0.0.1:8080"
    proxy = None
    headers = {}
    cookies = {}
    duckduckgo_scraper = DuckDuckGoScraper(headers, cookies, proxy)

    query = "childhood cancer"
    duckduckgo_scraper.get_search_results(query)
