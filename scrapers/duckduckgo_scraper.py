import json
import re
# from curl_cffi import requests
import requests
from scrapers.base_scraper import BaseScraper


class DuckDuckGoScraper(BaseScraper):
    BASE_URL = "https://duckduckgo.com"
    SEARCH_BASE_URL = "https://links.duckduckgo.com"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def get_cookies(self):
        pass

    def get_first_url(self, q: str) -> str:
        """ extract the first url to getch first page """
        params = {
            "q": q,
            "t": "_h",
            "ia": "web",
        }
        response = requests.get(
            self.BASE_URL, verify=False, proxies=self.PROXIES, headers=self.HEADERS, params=params,
            # impersonate="chrome131",
        )

        re_first_url = re.compile(r"DDG.deep.initialize\('?(.*)',")
        url_match = re_first_url.search(response.text)
        if not url_match:
            raise Exception("perf_id param not found")

        return self.SEARCH_BASE_URL + url_match.group(1)

    def get_next_url(self, response: requests.Response):
        """ extracts next page url from response """
        re_next_url = re.compile(r"n\":\"(/d\.js\?[^\"]+)")

        url_match = re_next_url.search(response.text)
        if not url_match:
            raise Exception("perf_id param not found")

        return self.SEARCH_BASE_URL + url_match.group(1)

    def get_search_results(self, search_query: str, max_pages: int = 10):
        """ get search results """

        url = self.get_first_url(search_query)
        all_links = []
        self.HEADERS["Referer"] = self.BASE_URL
        for page in range(1, max_pages + 1):
            response = requests.get(
                url, verify=False, proxies=self.PROXIES, headers=self.HEADERS, cookies=self.COOKIES,
                # impersonate="chrome131",
            )

            if response.status_code != 200:
                self.logger.error(f"Page {page} failed status code: {response.status_code}")
                continue

            links, url = self.extract_links_from_response(response)
            # url = self.get_next_url(response)
            page_load_url = self.extract_page_load_url(response)
            if page_load_url:
                requests.get(
                    page_load_url, verify=False, proxies=self.PROXIES, headers=self.HEADERS, cookies=self.COOKIES,
                    # impersonate="chrome131",
                )
            self.logger.info(f"Page {page} Extracted {len(links)} links")
            all_links.extend(links)

        self.logger.info(f"Total links {len(all_links)}")
        return all_links

    def extract_links_from_response(self, response: requests.Response):
        """ extracts links from response """
        re_data = re.compile(r"DDG\.pageLayout\.load\('d',(\[.*\])\)")

        data = re_data.search(response.text)

        if not data:
            raise Exception('data not found')

        data = data.group(1)
        data_json = json.loads(data)
        links = []
        next_url = None
        for entry in data_json:
            if (not entry.get("u") or not entry.get("t")) and entry.get("n"):
                next_url = self.SEARCH_BASE_URL + entry["n"]
                continue

            link = {
                "url": entry["u"],
                "title": entry["t"],
            }
            links.append(link)

        return links, next_url

    @staticmethod
    def extract_page_load_url(response: requests.Response):
        """ extracts page load url from response """
        re_data = re.compile(r"page_load_url\"? ?: ?\"?(.*?)\"")

        data = re_data.search(response.text)

        if not data:
            return None

        url = data.group(1)
        return url


if __name__ == "__main__":
    proxy = None  #  or "http://127.0.0.1:8080"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Dnt': '1',
        'Sec-Gpc': '1',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'Priority': 'u=1',
        'Referer': 'https://duckduckgo.com/',
    }
    cookies = {}
    duckduckgo_scraper = DuckDuckGoScraper(headers, cookies, proxy)

    query = "childhood cancer"
    duckduckgo_scraper.get_search_results(query, max_pages=10)
