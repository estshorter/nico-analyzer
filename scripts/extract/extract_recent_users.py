import pickle
import pandas as pd
import json
import urllib.request
import re
import time
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("Loading data from onboard.pickle...", flush=True)
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
        df = pd.json_normalize(data['data'])
    
    df['userId'] = pd.to_numeric(df['userId'], errors='coerce').astype('Int64')
    df['startTime'] = pd.to_datetime(df['startTime'], utc=True).dt.tz_convert('Asia/Tokyo')

    max_time = df['startTime'].max()
    threshold = max_time - pd.DateOffset(years=1)
    
    print(f"Latest post time in data: {max_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"1-year threshold: {threshold.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    recent_videos = df[df['startTime'] >= threshold]
    recent_users = recent_videos['userId'].dropna().unique()
    print(f"Found {len(recent_users)} users who posted within this 1-year period.", flush=True)
    
    CACHE_FILE = Path("results/simple_onboard/user_cache.json")
    USER_CACHE = {}
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            USER_CACHE = {int(k): v for k, v in json.load(f).items()}

    def get_username(user_id):
        if pd.isna(user_id): return "Unknown"
        user_id = int(user_id)
        if user_id in USER_CACHE: return USER_CACHE[user_id]
        
        url = f"https://www.nicovideo.jp/user/{user_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                html = res.read().decode('utf-8', errors='ignore')
                m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                if m:
                    name = m.group(1).replace(' さんのユーザーページ - ニコニコ', '').replace(' - ニコニコ', '').replace('さんのユーザーページ', '').strip()
                    USER_CACHE[user_id] = name
                    time.sleep(0.5)
                    return name
        except Exception:
            pass
        return f"User {user_id}"

    results = []
    latest_per_user = recent_videos.sort_values('startTime').groupby('userId').last().reset_index()

    for i, row in latest_per_user.iterrows():
        uid = row['userId']
        uname = get_username(uid)
        results.append({
            'userId': uid,
            'userName': uname,
            'latestPostTime': row['startTime'].strftime('%Y-%m-%d %H:%M:%S'),
            'latestTitle': row['title'],
            'latestContentId': row['contentId']
        })
        if len(results) % 50 == 0:
            print(f"Processed {len(results)}/{len(recent_users)}", flush=True)
            try:
                CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(USER_CACHE, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(USER_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values('latestPostTime', ascending=False)
    out_df.to_csv('results/recent_1year_onboard_users.csv', index=False, encoding='utf-8-sig')
    print("Saved to results/recent_1year_onboard_users.csv", flush=True)

if __name__ == "__main__":
    main()
