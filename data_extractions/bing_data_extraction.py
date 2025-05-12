from bs4 import BeautifulSoup
from curl_cffi import requests
import pandas as pd

search_query = "childhood cancer"
URL = "https://www.bing.com/search"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
}

cookies = {
    'MUID':'2674D0E49B3A67DE0576C55B9ACC6687', 
    'MUIDB':'2674D0E49B3A67DE0576C55B9ACC6687',
}

links = []
proxies = None

for page in range(1, 100):
    if len(links) >= 250:
        break

    first = (page - 1) * 10 + 1
    params = {'q': search_query, 'first': first}

    r = requests.get(URL, impersonate="chrome119", verify=False, proxies=proxies, headers=headers,cookies=cookies, params=params)

    if r.status_code != 200:
        print(f"Page {page} failed with status code: {r.status_code}")
        continue

    soup = BeautifulSoup(r.content, 'html5lib')

    results = soup.select('li[class*="b_algo"]')

    print(f"Page {page} scraped, found {len(results)} results")

    for result in results:
        if len(links) >= 250:
            break

        h2 = result.find('h2')
        if h2:
            a_tag = h2.find('a')
            if a_tag and a_tag.get('href'):
                href = a_tag['href']
                print("Captured URL:", href)  # 👈 debug print
                links.append({
                    "url": href
                })

# Convert to DataFrame
bing_results = pd.DataFrame(links)
print(f"Done. Extracted {len(bing_results)} organic result links.")
print(bing_results.head())

# Optional: Save to CSV
# bing_results.to_csv("bing_organic_links.csv", index=False)