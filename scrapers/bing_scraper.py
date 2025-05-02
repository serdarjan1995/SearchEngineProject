from bs4 import BeautifulSoup
from curl_cffi import requests

from scrapers.base_scraper import BaseScraper


class BingScraper(BaseScraper):
    BASE_URL = "https://www.bing.com"
    SEARCH_URL = BASE_URL + "/search"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def get_cookies(self):
        """ we can get cookies just visiting bing.com """
        response = requests.get(self.BASE_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES,
                                headers=self.HEADERS)
        self.COOKIES = response.cookies.get_dict()

    def get_search_results(self, search_query: str, max_pages: int = 10):
        """ get search results """

        all_links = []
        for page in range(1, max_pages + 1):
            start = (page - 1) * 10 + 1
            params = {
                "q": search_query,
                "first": start,
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
        soup = BeautifulSoup(response.content, 'html5lib')

        li_tags = soup.select('li[class*="b_algo"]')

        if not li_tags:
            raise Exception("li[cass=b_algo] not found")

        links = []
        for li_tag in li_tags:
            h2 = li_tag.find('h2')
            if not h2:
                continue

            a_tag = h2.find('a')
            if a_tag and a_tag.get('href'):
                href = a_tag['href']
                link = {
                    "url": href,
                    "title": a_tag.text,
                }
                links.append(link)

        return links


if __name__ == "__main__":
    proxy = "http://127.0.0.1:8080"
    headers = {}
    # cookies = {
    #     'MUID': '2674D0E49B3A67DE0576C55B9ACC6687',
    #     'MUIDB': '2674D0E49B3A67DE0576C55B9ACC6687',
    # }
    cookies = {}
    bing_scraper = BingScraper(headers, cookies, proxy)

    query = "childhood cancer"
    bing_scraper.get_search_results(query)
