import pickle
import sys
import os
import re
import json
import urllib.request
import pandas as pd
import numpy as np
from pathlib import Path
from common_utils import filter_software_talk

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = Path("results/simple_onboard")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = OUT_DIR / "user_cache.json"
USER_CACHE = {}
if CACHE_FILE.exists():
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            USER_CACHE = json.load(f)
            USER_CACHE = {int(k): v for k, v in USER_CACHE.items()}
    except Exception:
        USER_CACHE = {}

def save_cache():
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(USER_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_username(user_id):
    if pd.isna(user_id):
        return "Unknown"
    user_id = int(user_id)
    if user_id in USER_CACHE:
        return USER_CACHE[user_id]
        
    url = f"https://www.nicovideo.jp/user/{user_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=3) as res:
            html = res.read().decode('utf-8', errors='ignore')
            m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if m:
                name = m.group(1).replace(' さんのユーザーページ - ニコニコ', '').replace(' - ニコニコ', '').replace('さんのユーザーページ', '').strip()
                USER_CACHE[user_id] = name
                save_cache()
                return name
    except Exception:
        pass
    name = f"User {user_id}"
    USER_CACHE[user_id] = name
    save_cache()
    return name

def analyze_tanabata_creators():
    print("1. Loading raw pickle data for Tanabata creators analysis...")
    with open('results/software_talk.pickle', 'rb') as f:
        df_st = pd.json_normalize(pickle.load(f)['data'])
    df_st = filter_software_talk(df_st)
    
    with open('results/onboard.pickle', 'rb') as f:
        df_ob = pd.json_normalize(pickle.load(f)['data'])

    with open('results/simple_onboard.pickle', 'rb') as f:
        df_so = pd.json_normalize(pickle.load(f)['data'])

    for df in [df_st, df_ob, df_so]:
        df['userId'] = pd.to_numeric(df['userId'], errors='coerce').astype('Int64')
        df['startTime'] = pd.to_datetime(df['startTime'], utc=True).dt.tz_convert('Asia/Tokyo')

    df_st_onboard = df_st[df_st['tags'].astype(str).str.contains('車載', na=False)]
    all_onboard = pd.concat([df_st_onboard, df_ob, df_so], ignore_index=True).drop_duplicates(subset=['contentId'])
    all_st = pd.concat([df_st, df_so], ignore_index=True).drop_duplicates(subset=['contentId'])

    so_user_counts = df_so.groupby('userId').size()
    ob_user_counts = all_onboard.groupby('userId').size()
    st_user_counts = all_st.groupby('userId').size()

    # 複数回参加しているリピーター (参加年数・回数が2以上)
    multi_year_uids = [uid for uid, cnt in so_user_counts.items() if cnt >= 2]

    # 車載視点での純度100%七夕投稿者（他車載投稿0本）
    tanabata_ob_uids = [uid for uid in multi_year_uids if ob_user_counts.get(uid, 0) == so_user_counts.get(uid, 0)]
    # ボイロ活動視点での純度100%七夕投稿者（他ボイロ投稿0本）
    tanabata_st_uids = [uid for uid in multi_year_uids if st_user_counts.get(uid, 0) == so_user_counts.get(uid, 0)]

    print(f"\nリピーター総数 (2回以上参加): {len(multi_year_uids)}名")
    print(f"・純度100%七夕投稿者 [車載視点]: {len(tanabata_ob_uids)}名 ({len(tanabata_ob_uids)/len(multi_year_uids)*100:.1f}%)")
    print(f"・純度100%七夕投稿者 [ボイロ活動視点]: {len(tanabata_st_uids)}名 ({len(tanabata_st_uids)/len(multi_year_uids)*100:.1f}%)")

    # CSV出力用のリスト構築
    def build_records(uids, label):
        records = []
        for uid in uids:
            name = get_username(uid)
            user_so = df_so[df_so['userId'] == uid].sort_values('startTime')
            so_cnt = len(user_so)
            years = sorted(user_so['startTime'].dt.year.unique().tolist())
            latest_title = user_so.iloc[-1]['title']
            records.append({
                'userId': uid,
                'user_name': name,
                'simple_onboard_count': so_cnt,
                'participated_years': ", ".join(map(str, years)),
                'latest_video_title': latest_title,
                'type': label
            })
        return pd.DataFrame(records).sort_values('simple_onboard_count', ascending=False)

    df_tanabata_ob = build_records(tanabata_ob_uids, "車載視点七夕投稿者")
    df_tanabata_st = build_records(tanabata_st_uids, "ボイロ活動視点七夕投稿者")

    df_tanabata_ob.to_csv(OUT_DIR / "tanabata_creators_onboard.csv", index=False, encoding='utf-8-sig')
    df_tanabata_st.to_csv(OUT_DIR / "tanabata_creators_voiceroid.csv", index=False, encoding='utf-8-sig')

    print("Exported tanabata_creators_onboard.csv and tanabata_creators_voiceroid.csv successfully.")

if __name__ == '__main__':
    analyze_tanabata_creators()
