import requests
import re
import html

def scrape_nico_ranking():
    url = "https://www.nicovideo.jp/ranking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the page: {e}")
        return

    # Decode HTML entities so that &quot; becomes "
    unescaped_text = html.unescape(response.text)
    
    # In the React state, ranking items are usually represented as objects with an "id" field.
    # The format looks like "id":"sm12345" or "id":"so12345"
    # We will search for all video IDs. We can assume the first 100 unique valid IDs 
    # appearing in the main ranking data structure represent the ranking.
    
    # We will use a regular expression to find all instances of "id":"(sm|so|nm)\d+"
    # This avoids matching channel IDs like "ch12345" which are nested objects.
    
    matches = re.finditer(r'"id":"((?:sm|so|nm)\d+)"', unescaped_text)
    
    unique_ids = []
    seen = set()
    for match in matches:
        vid = match.group(1)
        if vid not in seen:
            seen.add(vid)
            unique_ids.append(vid)
            
    # Print the top 100 unique video IDs
    print("Rank : Video ID")
    print("-" * 20)
    for i, vid in enumerate(unique_ids[:100], 1):
        print(f"{i}: {vid}")

if __name__ == "__main__":
    scrape_nico_ranking()
