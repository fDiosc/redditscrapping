import requests
import json

def test_json_fetch(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    try:
        print(f"Testing URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            print(f"Successfully fetched {len(posts)} posts!")
            if posts:
                print(f"First post title: {posts[0]['data']['title']}")
        else:
            print(f"Response Body: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Error: {e}")

test_json_fetch("aitools")
test_json_fetch("indiehackers")
