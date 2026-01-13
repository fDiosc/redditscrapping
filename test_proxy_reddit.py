from curl_cffi import requests
import json

# Bright Data Residential Proxy Credentials from your screenshot
PROXY_HOST = "brd.superproxy.io:33335"
PROXY_USER = "brd-customer-hl_06b63b6a-zone-residential_proxy1"
PROXY_PASS = "rf06422hv83l"

# Constructing the proxy URL
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

def test_reddit_proxy(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=5"
    
    print(f"--- Bright Data Proxy Test (curl_cffi) ---")
    print(f"Target: {url}")
    print(f"Using Proxy: {PROXY_HOST}")
    
    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL
    }
    
    try:
        # Using impersonate="chrome110" + Residential Proxy
        # verify=False is used because of the "self signed certificate" error with Bright Data/EC2
        response = requests.get(
            url, 
            impersonate="chrome110", 
            proxies=proxies,
            headers={"Accept": "application/json"},
            timeout=30,
            verify=False
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            print(f"SUCCESS! Fetched {len(posts)} posts from r/{subreddit} via Proxy.")
            if posts:
                print(f"Latest post: {posts[0]['data']['title']}")
        else:
            print(f"FAILURE: Status {response.status_code}")
            print(f"Body snippet: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error connecting via proxy: {e}")

if __name__ == "__main__":
    test_reddit_proxy("indiehackers")
