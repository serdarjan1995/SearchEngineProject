from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up headless Chrome browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Open DuckDuckGo search page
search_url = "https://duckduckgo.com/?q=childhood+cancer&t=h_&ia=web"
driver.get(search_url)

# Let results load
time.sleep(2)

collected_urls = set()
more_clicks = 0  # Counter for "More Results" button presses

while len(collected_urls) < 250:
    # Find all <li> elements with data-layout="organic"
    organic_results = driver.find_elements(By.CSS_SELECTOR, 'li[data-layout="organic"]')

    for result in organic_results:
        try:
            h2_link = result.find_element(By.CSS_SELECTOR, 'h2 a[href]')
            href = h2_link.get_attribute('href')
            if href and href.startswith('http') and href not in collected_urls:
                collected_urls.add(href)
                print(f"[{len(collected_urls)}] {href}")  # Print each result as it's collected
        except:
            continue
        if len(collected_urls) >= 250:
            break

    # Try clicking "More Results" button if it exists
    try:
        more_button = driver.find_element(By.ID, 'more-results')
        driver.execute_script("arguments[0].click();", more_button)
        more_clicks += 1  # Increment click counter
        time.sleep(2)  # Wait for new results
    except:
        print("No more 'More results' button found.")
        break

# Close browser
driver.quit()

# Final summary
print(f"\nTotal collected URLs: {len(collected_urls)}")
print(f"'More Results' button clicked: {more_clicks} times")

