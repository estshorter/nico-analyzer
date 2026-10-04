import pickle
import pandas as pd
import json
import urllib.request
import re
import time
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def parse_args():
    parser = argparse.ArgumentParser(description="Extract users whose first onboard video was posted in a specified year or all years.")
    parser.add_argument("year", nargs="?", default=None, help="Target year (e.g. 2025) or 'all'")
    parser.add_argument("--year", "-y", dest="opt_year", default=None, help="Target year (e.g. 2025) or 'all'")
    parser.add_argument("--all", "-a", action="store_true", help="Extract all years")
    parser.add_argument("--pickle", "-p", default="results/onboard.pickle", help="Path to onboard pickle file")
    args = parser.parse_args()
    
    if args.all:
        target_year = "all"
    elif args.opt_year is not None:
        target_year = str(args.opt_year).lower()
    elif args.year is not None:
        target_year = str(args.year).lower()
    else:
        target_year = "all"

    if target_year != "all":
        try:
            target_year = int(target_year)
        except ValueError:
            target_year = "all"

    return target_year, args.pickle

def main():
    target_year, pickle_path = parse_args()
    
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

    print(f"Loading data from {pickle_path}...")
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
        df = pd.json_normalize(data['data'])
    
    df['userId'] = pd.to_numeric(df['userId'], errors='coerce').astype('Int64')
    df['startTime'] = pd.to_datetime(df['startTime'], utc=True).dt.tz_convert('Asia/Tokyo')

    # Sort by startTime
    df_sorted = df.dropna(subset=['userId']).sort_values('startTime')

    # Calculate first post and latest post per user
    first_posts = df_sorted.groupby('userId').first().reset_index()
    latest_posts = df_sorted.groupby('userId').last().reset_index()

    latest_dataset_time = df_sorted['startTime'].max()
    threshold_1year = latest_dataset_time - pd.DateOffset(years=1)
    print(f"Dataset latest video time: {latest_dataset_time}")
    print(f"1-year threshold: {threshold_1year}")

    # Filter for target year based on first post
    if target_year == "all":
        target_df = first_posts
        print(f"Extracting all {len(target_df)} users.")
        output_path = 'results/first_onboard_all.csv'
    else:
        target_df = first_posts[first_posts['startTime'].dt.year == target_year]
        print(f"Found {len(target_df)} users who posted their first video in {target_year}.")
        output_path = f'results/first_onboard_{target_year}.csv'

    latest_dict = latest_posts.set_index('userId').to_dict('index')

    results = []
    for i, row in target_df.iterrows():
        uid = row['userId']
        uname = get_username(uid)
        latest_row = latest_dict.get(uid, {})

        latest_time = latest_row.get('startTime')
        has_latest = latest_time is not None and pd.notna(latest_time)
        latest_time_str = latest_time.strftime('%Y-%m-%d %H:%M:%S') if has_latest else ''
        latest_title = latest_row.get('title', '')
        latest_content_id = latest_row.get('contentId', '')
        is_active = bool(has_latest and latest_time >= threshold_1year)
        debut_year = int(row['startTime'].year)

        results.append({
            'userId': int(uid) if pd.notna(uid) else None,
            'userName': uname,
            'debutYear': debut_year,
            'firstPostTime': row['startTime'].strftime('%Y-%m-%d %H:%M:%S'),
            'firstTitle': row['title'],
            'firstContentId': row['contentId'],
            'latestPostTime': latest_time_str,
            'latestTitle': latest_title,
            'latestContentId': latest_content_id,
            'isActiveRecent1Year': is_active
        })
        if len(results) % 50 == 0:
            print(f"Processed {len(results)}/{len(target_df)}", flush=True)
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
    out_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved CSV to {output_path}")

    json_path = output_path.replace('.csv', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON to {json_path}")

if __name__ == "__main__":
    main()
