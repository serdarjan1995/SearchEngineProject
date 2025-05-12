from bs4 import BeautifulSoup
from curl_cffi import requests
from urllib.parse import unquote

from .base_scraper import BaseScraper


class YahooScraper(BaseScraper):
    BASE_URL = "https://search.yahoo.com"
    SEARCH_URL = BASE_URL + "/search"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def get_cookies(self):
        pass

    def get_search_results(self, search_query: str, max_pages: int = 10):
        """ get search results """

        all_links = []
        for page in range(1, max_pages + 1):
            start = (page - 1) * 10
            params = {
                "p": search_query,
            }
            if start:
                params['b'] = str(start)
            response = requests.get(
                self.SEARCH_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES, headers=self.HEADERS,
                cookies=self.COOKIES, params=params
            )

            if response.status_code != 200:
                self.logger.error(f"Page {page} failed status code: {response.status_code}")
                continue

            links = self.extract_links_from_response(response)
            self.logger.info(f"Page {page} Extracted {len(links)} links")
            if not links:
                break
            all_links.extend(links)

        self.logger.info(f"Total links {len(all_links)}")
        return all_links

    @staticmethod
    def extract_links_from_response(response: requests.Response):
        """ extracts links from response """
        soup = BeautifulSoup(response.content, 'html5lib')

        # Target <div id="web" class="web-res">
        web_div = soup.find('div', {'id': 'web', 'class': 'web-res'})
        if not web_div:
            raise Exception("web div not found")

        links = []
        for li_tag in web_div.find_all('li'):
            div_tag = li_tag.find('div', class_='compTitle options-toggle')
            if not div_tag:
                continue

            a_tag = div_tag.find('a')
            href = a_tag['href']
            # Decode Yahoo redirect URL if present
            if "r.search.yahoo.com" in href and "RU=" in href:
                try:
                    ru_index = href.index("RU=") + 3
                    real_url_encoded = href[ru_index:]
                    real_url = unquote(real_url_encoded.split("/")[0])
                    href = real_url
                except Exception:
                    pass  # fallback to original href

            title = a_tag.h3.text if a_tag.h3 else a_tag.get('aria-label')
            link = {
                "url": href,
                "title": title,
            }
            links.append(link)

        return links


# proxy = "http://127.0.0.1:8080"
proxy = None
headers = {}
cookies = {}
yahoo_scraper = YahooScraper(headers, cookies, proxy)

if __name__ == "__main__":
    query = "childhood cancer"
    yahoo_scraper.get_search_results(query)
