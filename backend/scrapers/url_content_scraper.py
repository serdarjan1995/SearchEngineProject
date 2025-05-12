import logging
from typing import Union, Optional

from bs4 import BeautifulSoup
from curl_cffi import requests


class UrlContentScraper:
    PROXIES = None
    HEADERS = {}

    def __init__(self, headers: Union[None, dict], proxy: Union[str, None] = None):
        self.headers = headers
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s @ %(filename)s:%(funcName)s:%(lineno)d')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        if proxy:
            self.PROXIES = {"http": proxy, "https": proxy}

        if headers:
            self.HEADERS.update(headers)

    def scrape_content(self, url: str) -> Optional[str]:
        """ get content from url """
        response = requests.get(url, impersonate="chrome131", verify=False, proxies=self.PROXIES, headers=self.HEADERS)
        if response.status_code != 200:
            self.logger.error(f"Failed status code: {response.status_code} {url}")
            return None

        soup = BeautifulSoup(response.content, 'html5lib')
        body = soup.body

        # Remove <script>, <style>, <link> and <footer> tags from the body
        for tag in body(['script', 'style', 'link', 'nav', 'footer']):
            tag.decompose()  # Removes the tag from the tree

        text = body.get_text(separator='\n', strip=True)

        return text


proxy = None  # or "http://127.0.0.1:8080"
headers = {}
content_scraper = UrlContentScraper(headers, proxy)

if __name__ == "__main__":
    url = "https://www.cancer.gov/types/childhood-cancers"
    text = content_scraper.scrape_content(url)
    print(text)