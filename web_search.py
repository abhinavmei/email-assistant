import requests

def google_search(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,        # Make sure api_key is passed in as a string
        "cx": cse_id,          # Make sure cse_id is passed in as a string
        "q": query,
        "num": num_results,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()

    search_results = []
    for item in results.get("items", []):
        search_results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        })

    return search_results
