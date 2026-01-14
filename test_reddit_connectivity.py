import requests
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def test_fetch(url, headers):
    try:
        print(f"\nTesting URL: {url}")
        print(f"Headers: {headers.get('User-Agent')[:50]}...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully fetched the page!")
            print(f"Result Preview: {response.text[:100].strip()}...")
        else:
            print(f"Failed to fetch. Content length: {len(response.text)}")
    except Exception as e:
        print(f"Error during fetch: {e}")

subreddits = ["aitools", "indiehackers", "news"]
urls = []
for sub in subreddits:
    urls.append(f"https://old.reddit.com/r/{sub}/new/")
    urls.append(f"https://www.reddit.com/r/{sub}/new/")

# Test with a very clean header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

for url in urls:
    test_fetch(url, headers)
