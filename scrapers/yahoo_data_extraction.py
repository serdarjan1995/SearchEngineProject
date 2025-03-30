from bs4 import BeautifulSoup
from curl_cffi import requests
from urllib.parse import unquote
import pandas as pd

search_query = "childhood cancer"
base_url = "https://search.yahoo.com/search"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36',
    'upgrade-insecure-requests': '1',
}

proxies = None
links = []
results_per_page = 10
start_index = 1
max_links = 600

while len(links) < max_links:
    params = {
        'p': search_query,
        'b': start_index,
    }

    try:
        r = requests.get(
            base_url,
            impersonate="chrome119",
            verify=False,
            proxies=proxies,
            headers=headers,
            params=params
        )
    except Exception as e:
        print(f"❌ Request failed at b={start_index}: {e}")
        break

    if r.status_code != 200:
        print(f"❌ Failed to load page at b={start_index}. Status code: {r.status_code}")
        break

    soup = BeautifulSoup(r.content, 'html5lib')

    # Target <div id="web" class="web-res">
    web_div = soup.find('div', {'id': 'web', 'class': 'web-res'})

    if not web_div:
        print("⚠️ <div id='web' class='web-res'> not found. Stopping.")
        break

    new_links = 0

    for tag in web_div.find_all(href=True):
        href = tag['href']

        # Decode Yahoo redirect URL if present
        if "r.search.yahoo.com" in href and "RU=" in href:
            try:
                ru_index = href.index("RU=") + 3
                real_url_encoded = href[ru_index:]
                real_url = unquote(real_url_encoded.split("/")[0])
                href = real_url
            except Exception:
                pass  # fallback to original href

        title = tag.get('title', '')
        links.append({'url': href, 'title': title})
        new_links += 1

        if len(links) >= max_links:
            break

    print(f"✅ Found {new_links} hrefs from start index {start_index}. Total: {len(links)}")

    if new_links == 0:
        print("⚠️ No more hrefs found. Stopping.")
        break

    start_index += results_per_page

# Save to DataFrame
yahoo_results = pd.DataFrame(links)
print(f"\n🎯 Scraping complete. Total results: {len(yahoo_results)}")
print(yahoo_results.head())

# Optionally save to CSV
# yahoo_results.to_csv('yahoo_search_results.csv', index=False)
