from bs4 import BeautifulSoup
import requests
import json
from searchurl import search_serper  # make sure searchurl.py exists and works

def scrape_webpage(url):
    """Scrape clean text content from a webpage."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"Failed to retrieve {url} | Status code: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'noscript', 'iframe']):
            tag.decompose()

        # Extract readable text
        text = soup.get_text(separator=' ', strip=True)
        return text

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

if __name__ == "__main__":
    query = "latest trends in reinforcement learning 2025"
    print(f"🔍 Searching: {query}")
    
    search_results = search_serper(query)
    all_results = []

    for result in search_results:
        url = result.get('link')
        title = result.get('title')
        snippet = result.get('snippet')

        print(f"🕸 Scraping: {title}")
        content = scrape_webpage(url)

        if len(content) < 200:
            print(f"Skipping {url} — too short")
            continue

        all_results.append({
            "query": query,
            "url": url,
            "title": title,
            "snippet": snippet,
            "content": content
        })

    # ===== Save to JSON =====
    if all_results:
        with open("backend/node/scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(all_results)} records to scraped_data.json successfully!")
    else:
        print("No valid results scraped. Please check your search_serper or scraping logic.")
