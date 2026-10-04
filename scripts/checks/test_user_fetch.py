import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_username(user_id):
    url = f"https://www.nicovideo.jp/user/{user_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            html = res.read().decode('utf-8', errors='ignore')
            m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if m:
                name = m.group(1).replace(' さんのユーザーページ - ニコニコ', '').replace(' - ニコニコ', '').replace('さんのユーザーページ', '')
                return name.strip()
    except Exception as e:
        pass
    return f"User {user_id}"

if __name__ == "__main__":
    print(get_username(347413))
