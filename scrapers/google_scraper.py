from bs4 import BeautifulSoup
from curl_cffi import requests

from scrapers.base_scraper import BaseScraper


class GoogleScraper(BaseScraper):
    BASE_URL = "https://www.google.com"
    SEARCH_URL = BASE_URL + "/search"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def get_cookies(self):
        """ we can get cookies just visiting google.com """
        response = requests.get(self.BASE_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES,
                                headers=self.HEADERS)
        self.COOKIES = response.cookies.get_dict()

    def get_search_results(self, search_query: str, max_pages: int = 10):
        """ get search results """

        all_links = []
        for page in range(1, max_pages + 1):
            start = (page - 1) * 10
            params = {
                "q": search_query,
            }
            if start:
                params['start'] = str(start)

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
        main_div = soup.find('div', attrs={'role': 'main'})
        if not main_div:
            raise Exception("main div not found")

        links = []
        for a_tag in main_div.find_all('a'):
            if not a_tag.h3:
                continue
            a_url = a_tag['href']
            link = {
                "url": a_url,
                "title": a_tag.h3.text,
            }
            links.append(link)

        return links


if __name__ == "__main__":
    # proxy = "http://127.0.0.1:8080"
    proxy = None
    headers = {}
    cookies = {
        'AEC': 'AVcja2fqLn3YYsgaOJRHPXG2ksCBOtQ4I4Vgm6tAJlUZWJ-xwjHX7mVwVeo',
        'NID': '522=mecL14YgWSjL5s1GVOIosnNmxPcaLKeSItPCsk_dAmMmDKnC5yitVjPm_cY1DdWbyYKYraDeF14ONfTHd89pAITY2iGMWhM5UriAZh4ifMH5DClyKltqFP7UuGR_Wj5yDdEPuF-2R8irSj1RHQBShf_-LjxBHeBBKzYSGKwu5Gwg07zRBOMdd2omIUPQzj5PBeLy--YuveNFms3cnrTve6B3ndXRXO9PWITTaLB4TZf6nqJp5TLwZ1j8T7ca9wqUeakZM7y3vLL8QwyBwwc',
    }
    google_scraper = GoogleScraper(headers, cookies, proxy)

    query = "childhood cancer"
    google_scraper.get_search_results(query)
