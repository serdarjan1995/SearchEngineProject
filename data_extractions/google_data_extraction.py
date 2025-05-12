# pip install bs4 curl_cffi html5lib

from bs4 import BeautifulSoup
from curl_cffi import requests

search_query = "childhood cancer"

URL = f"https://www.google.com/search?q={search_query}"

proxy = ""  # "http://127.0.0.1:8080"
proxies = {"http": proxy, "https": proxy} if proxy else None

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'dnt': '1',
    'downlink': '10',
    'priority': 'u=0, i',
    'rtt': '50',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Chromium";v="131", "Not:A-Brand";v="24", "Google Chrome";v="131"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-form-factors': '"Desktop"',
    'sec-ch-ua-full-version': '"131.0.6998.88"',
    'sec-ch-ua-full-version-list': '"Chromium";v="131.0.6998.88", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="131.0.6998.88"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '"6.1.0"',
    'sec-ch-ua-wow64': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'x-browser-channel': 'stable',
    'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
    'x-browser-validation': 'Xu3McleZcKTT6TgGB8KFHwGJApU=',
    'x-browser-year': '2025',
}

cookies = {
    'AEC': 'AVcja2fqLn3YYsgaOJRHPXG2ksCBOtQ4I4Vgm6tAJlUZWJ-xwjHX7mVwVeo',
    'NID': '522=mecL14YgWSjL5s1GVOIosnNmxPcaLKeSItPCsk_dAmMmDKnC5yitVjPm_cY1DdWbyYKYraDeF14ONfTHd89pAITY2iGMWhM5UriAZh4ifMH5DClyKltqFP7UuGR_Wj5yDdEPuF-2R8irSj1RHQBShf_-LjxBHeBBKzYSGKwu5Gwg07zRBOMdd2omIUPQzj5PBeLy--YuveNFms3cnrTve6B3ndXRXO9PWITTaLB4TZf6nqJp5TLwZ1j8T7ca9wqUeakZM7y3vLL8QwyBwwc',
}

start = 0
links = []
for page in range(1, 11):
    start = (page - 1) * 10
    params = {}
    if start:
        params['start'] = start
    r = requests.get(
        URL, impersonate="chrome131", verify=False, proxies=proxies, headers=headers, cookies=cookies, params=params
    )

    if r.status_code != 200:
        print(f"Page {page} failed status code: {r.status_code}")

    soup = BeautifulSoup(r.content, 'html5lib')
    # print(soup.prettify())

    main_div = soup.find('div', attrs={'role': 'main'})

    for a_tag in main_div.find_all('a'):
        if not a_tag.h3:
            continue
        a_url = a_tag['href']
        link = {
            "url": a_url,
            "title": a_tag.h3.text,
        }
        links.append(link)

    print(f"Page {page} scraped")

print(f"done. extracted links: {len(links)}")
print(links)
