import requests
import dotenv
import json

dotenv.load_dotenv()
SERPER_API_KEY = dotenv.get_key(dotenv.find_dotenv(), 'SERPER_API_KEY')
def search_serper(query, num_results=5):
    """
    Perform a Google-style search via Serper.dev API
    and return a list of top search results.
    """

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results  # optional: limit number of results
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return []

    data = response.json()
    results = []

    # Extract the organic search results
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results


if __name__ == "__main__":
    query = "latest trends in reinforcement learning 2025"
    search_results = search_serper(query)

    print(json.dumps(search_results, indent=2))
