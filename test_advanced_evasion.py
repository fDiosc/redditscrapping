import json
try:
    from curl_cffi import requests
except ImportError:
    print("ERROR: curl_cffi not installed. Please run: pip install curl_cffi")
    exit(1)

def test_evasion(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=5"
    
    print(f"--- Advanced Evasion Test (curl_cffi) ---")
    print(f"Target: {url}")
    
    try:
        # curl_cffi can impersonate a specific browser's TLS/JA3 fingerprint
        response = requests.get(
            url, 
            impersonate="chrome110", 
            headers={
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            print(f"SUCCESS! Fetched {len(posts)} posts from r/{subreddit}")
            if posts:
                print(f"Latest post: {posts[0]['data']['title']}")
        elif response.status_code == 403:
            print("FAILURE: 403 Forbidden. Reddit is still blocking based on IP-range.")
            print("Conclusion: TLS Impersonation is not enough. Proxies are required.")
        else:
            print(f"Unexpected Status: {response.status_code}")
            print(f"Body snippet: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a known accessible subreddit
    test_evasion("indiehackers")
