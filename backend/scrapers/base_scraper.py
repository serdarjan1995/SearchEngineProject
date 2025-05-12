import logging
from abc import ABC
from typing import Union

from curl_cffi import requests


class BaseScraper(ABC):
    BASE_URL: str
    SEARCH_URL: str
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def __init__(self, headers: Union[None, dict], cookies: Union[None, dict], proxy: Union[str, None] = None):
        self.headers = headers
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s @ %(filename)s:%(funcName)s:%(lineno)d')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        if proxy:
            self.PROXIES = {"http": proxy, "https": proxy}

        if headers:
            self.HEADERS.update(headers)

        # init with cookies
        if cookies:
            self.COOKIES = cookies
        else:
            self.get_cookies()

    def get_cookies(self) -> dict:
        pass

    def get_search_results(self, search_query: str, max_pages: int = 10) -> list[dict]:
        pass

    @staticmethod
    def extract_links_from_response(response: requests.Response) -> list[dict]:
        pass

