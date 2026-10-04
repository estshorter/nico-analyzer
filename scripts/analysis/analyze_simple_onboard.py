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

def load_data():
    print("1. Loading raw pickle data...")
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
    all_onboard = all_onboard.sort_values('startTime').reset_index(drop=True)
    
    all_st = pd.concat([df_st, df_so], ignore_index=True).drop_duplicates(subset=['contentId'])
    all_st = all_st.sort_values('startTime').reset_index(drop=True)

    return df_so, all_onboard, all_st

def run_analysis():
    df_so, all_onboard, all_st = load_data()
    
    ob_by_user = {uid: group.sort_values('startTime') for uid, group in all_onboard.groupby('userId')}
    st_by_user = {uid: group.sort_values('startTime') for uid, group in all_st.groupby('userId')}

    periods = {
        2023: {
            'name': '2023 (第1回)',
            'start': pd.Timestamp('2023-07-04 00:00:00+0900'),
            'end': pd.Timestamp('2023-07-18 00:00:00+0900'),
            'calendar_year': 2023
        },
        2024: {
            'name': '2024 (第2回・延期開催)',
            'start': pd.Timestamp('2024-08-19 00:00:00+0900'),
            'end': pd.Timestamp('2024-09-02 00:00:00+0900'),
            'calendar_year': 2024
        },
        2025: {
            'name': '2025 (第3回)',
            'start': pd.Timestamp('2025-07-08 00:00:00+0900'),
            'end': pd.Timestamp('2025-07-22 00:00:00+0900'),
            'calendar_year': 2025
        },
        2026: {
            'name': '2026 (第4回)',
            'start': pd.Timestamp('2026-07-07 00:00:00+0900'),
            'end': pd.Timestamp('2026-07-21 00:00:00+0900'),
            'calendar_year': 2026
        }
    }
    
    df_so['calendar_year'] = df_so['startTime'].dt.year

    so_users_by_year = {}
    so_df_by_year = {}
    daily_counts_list = []

    print("\n2. Aggregating daily post counts...")
    for year, info in periods.items():
        start_t = info['start']
        end_t = info['end']
        
        df_period = df_so[(df_so['startTime'] >= start_t) & (df_so['startTime'] <= end_t)].copy()
        so_df_by_year[year] = df_period
        so_users_by_year[year] = set(df_period['userId'].dropna().unique())

        df_period['date_str'] = df_period['startTime'].dt.strftime('%Y-%m-%d')
        
        end_day_str = (end_t - pd.Timedelta(seconds=1)).strftime('%Y-%m-%d')
        full_dates = pd.date_range(start=start_t.strftime('%Y-%m-%d'), end=end_day_str, freq='D').strftime('%Y-%m-%d')
        
        daily = (
            df_period.groupby('date_str')
            .size()
            .reindex(full_dates, fill_value=0)
            .reset_index(name='count')
            .rename(columns={'index': 'date_str'})
        )
        
        end_day_exact = end_t.strftime('%Y-%m-%d')
        exact_end_count = len(df_period[df_period['date_str'] == end_day_exact])
        if exact_end_count > 0:
            daily = pd.concat([daily, pd.DataFrame([{'date_str': end_day_exact, 'count': exact_end_count}])], ignore_index=True)
            
        daily['year'] = year
        daily['day_num'] = np.arange(1, len(daily) + 1)
        daily_counts_list.append(daily)

    df_daily_all = pd.concat(daily_counts_list, ignore_index=True)
    df_daily_all.to_csv(OUT_DIR / "daily_post_counts.csv", index=False, encoding='utf-8-sig')

    print("\n3. Analyzing creator breakdown & metrics...")
    summary_rows = []
    gap_records = {}
    all_gaps_list = []

    for year, info in periods.items():
        df_year = so_df_by_year[year]
        unique_users = df_year['userId'].dropna().unique()
        total_creators = len(unique_users)
        total_videos = len(df_year)
        
        df_cal = df_so[df_so['calendar_year'] == year]
        cal_total_videos = len(df_cal)
        cal_total_creators = df_cal['userId'].nunique()

        first_time_ob_users = []
        first_time_st_users = []
        returning_ob_users = []
        returning_st_users = []
        regular_ob_users = []
        regular_st_users = []
        user_gaps = []

        for uid in unique_users:
            user_so_posts = df_year[df_year['userId'] == uid].sort_values('startTime')
            first_so_row = user_so_posts.iloc[0]
            first_so_time = first_so_row['startTime']
            so_title = first_so_row['title']
            so_content_id = first_so_row['contentId']
            
            user_ob = ob_by_user.get(uid, pd.DataFrame())
            prior_ob = user_ob[user_ob['startTime'] < first_so_time] if not user_ob.empty else pd.DataFrame()

            user_st = st_by_user.get(uid, pd.DataFrame())
            prior_st = user_st[user_st['startTime'] < first_so_time] if not user_st.empty else pd.DataFrame()

            posted_prev_so = (year - 1) in so_users_by_year and uid in so_users_by_year[year - 1]

            is_first_ob = (len(prior_ob) == 0)
            is_first_st = (len(prior_st) == 0)

            days_gap_ob = None
            days_gap_st = None
            last_ob_time = None
            last_ob_title = ""
            last_st_time = None
            last_st_title = ""

            if is_first_ob:
                first_time_ob_users.append(uid)
            else:
                last_ob_row = prior_ob.iloc[-1]
                last_ob_time = last_ob_row['startTime']
                days_gap_ob = (first_so_time - last_ob_time).total_seconds() / 86400.0
                last_ob_title = last_ob_row.get('title', '')

            if is_first_st:
                first_time_st_users.append(uid)
            else:
                last_st_row = prior_st.iloc[-1]
                last_st_time = last_st_row['startTime']
                days_gap_st = (first_so_time - last_st_time).total_seconds() / 86400.0
                last_st_title = last_st_row.get('title', '')

            is_returning_ob = (days_gap_ob is not None and days_gap_ob > 365 and not posted_prev_so)
            is_returning_st = (days_gap_st is not None and days_gap_st > 365 and not posted_prev_so)

            if not is_first_ob:
                if is_returning_ob:
                    returning_ob_users.append(uid)
                else:
                    regular_ob_users.append(uid)

            if not is_first_st:
                if is_returning_st:
                    returning_st_users.append(uid)
                else:
                    regular_st_users.append(uid)

            if not is_first_ob:
                record = {
                    'year': year,
                    'userId': uid,
                    'first_so_time': first_so_time.strftime('%Y-%m-%d %H:%M'),
                    'so_content_id': so_content_id,
                    'so_title': so_title,
                    'last_ob_time': last_ob_time.strftime('%Y-%m-%d %H:%M') if last_ob_time else '',
                    'last_ob_title': last_ob_title,
                    'days_gap': round(days_gap_ob, 1) if days_gap_ob is not None else np.nan,
                    'days_gap_int': int(days_gap_ob) if days_gap_ob is not None else np.nan,
                    'days_gap_ob': round(days_gap_ob, 1) if days_gap_ob is not None else np.nan,
                    'days_gap_st': round(days_gap_st, 1) if days_gap_st is not None else np.nan,
                    'last_st_time': last_st_time.strftime('%Y-%m-%d %H:%M') if last_st_time else '',
                    'last_st_title': last_st_title,
                    'posted_prev_so': posted_prev_so,
                    'is_returning': is_returning_ob,
                    'is_returning_ob': is_returning_ob,
                    'is_returning_st': is_returning_st
                }
                user_gaps.append(record)
                all_gaps_list.append(record)

        gap_records[year] = pd.DataFrame(user_gaps)

        disappeared_ob_count = 0
        disappeared_st_count = 0
        prev_total_users = 0

        if (year - 1) in so_users_by_year:
            prev_users = so_users_by_year[year - 1]
            prev_df = so_df_by_year[year - 1]
            prev_total_users = len(prev_users)
            
            for p_uid in prev_users:
                last_prev_so_time = prev_df[prev_df['userId'] == p_uid]['startTime'].max()
                
                u_ob = ob_by_user.get(p_uid, pd.DataFrame())
                later_ob = u_ob[u_ob['startTime'] > last_prev_so_time] if not u_ob.empty else pd.DataFrame()
                
                u_st = st_by_user.get(p_uid, pd.DataFrame())
                later_st = u_st[u_st['startTime'] > last_prev_so_time] if not u_st.empty else pd.DataFrame()
                
                if len(later_ob) == 0:
                    disappeared_ob_count += 1
                if len(later_st) == 0:
                    disappeared_st_count += 1

        summary_rows.append({
            'year': year,
            'period_name': info['name'],
            'event_start': info['start'].strftime('%Y-%m-%d %H:%M'),
            'event_end': info['end'].strftime('%Y-%m-%d %H:%M'),
            'period_videos': total_videos,
            'period_creators': total_creators,
            'calendar_videos': cal_total_videos,
            'calendar_creators': cal_total_creators,
            'first_time_count': len(first_time_ob_users),
            'first_time_pct': round(len(first_time_ob_users) / total_creators * 100, 1),
            'first_time_st_count': len(first_time_st_users),
            'first_time_st_pct': round(len(first_time_st_users) / total_creators * 100, 1),
            'returning_count': len(returning_ob_users),
            'returning_pct': round(len(returning_ob_users) / total_creators * 100, 1),
            'returning_st_count': len(returning_st_users),
            'returning_st_pct': round(len(returning_st_users) / total_creators * 100, 1),
            'regular_count': len(regular_ob_users),
            'regular_pct': round(len(regular_ob_users) / total_creators * 100, 1),
            'regular_st_count': len(regular_st_users),
            'regular_st_pct': round(len(regular_st_users) / total_creators * 100, 1),
            'prev_year_creators': prev_total_users,
            'disappeared_ob_count': disappeared_ob_count,
            'disappeared_ob_pct': round(disappeared_ob_count / prev_total_users * 100, 1) if prev_total_users > 0 else 0,
            'disappeared_st_count': disappeared_st_count,
            'disappeared_st_pct': round(disappeared_st_count / prev_total_users * 100, 1) if prev_total_users > 0 else 0,
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(OUT_DIR / "summary_metrics.csv", index=False, encoding='utf-8-sig')

    df_all_gaps = pd.DataFrame(all_gaps_list)
    df_all_gaps.to_csv(OUT_DIR / "all_user_gaps.csv", index=False, encoding='utf-8-sig')

    for year in [2023, 2024, 2025, 2026]:
        df_gaps = gap_records[year]
        if len(df_gaps) == 0:
            continue
        
        # 1. Longest gap > 365d (復帰者)
        df_top50_ret = df_gaps[df_gaps['is_returning']].sort_values('days_gap', ascending=False).head(50).copy()
        usernames_ret = [get_username(r['userId']) for _, r in df_top50_ret.iterrows()]
        df_top50_ret['user_name'] = usernames_ret
        cols = ['year', 'userId', 'user_name', 'days_gap_ob', 'days_gap_st', 'first_so_time', 'so_title', 'so_content_id', 'last_ob_time', 'last_ob_title', 'last_st_time', 'last_st_title', 'posted_prev_so']
        df_top50_ret = df_top50_ret[cols]
        df_top50_ret.to_csv(OUT_DIR / f"top50_longest_gap_{year}.csv", index=False, encoding='utf-8-sig')

        # 2. Regular / Continuous creators (常連・継続投稿者)
        df_reg = df_gaps[~df_gaps['is_returning']].sort_values('days_gap', ascending=False).head(50).copy()
        usernames_reg = [get_username(r['userId']) for _, r in df_reg.iterrows()]
        df_reg['user_name'] = usernames_reg
        df_reg = df_reg[cols]
        df_reg.to_csv(OUT_DIR / f"top50_gap_regular_{year}.csv", index=False, encoding='utf-8-sig')

        # 3. Within 1 year gap (<= 365d)
        df_w1y = df_gaps[df_gaps['days_gap'] <= 365].sort_values('days_gap', ascending=False).head(50).copy()
        usernames_w1y = [get_username(r['userId']) for _, r in df_w1y.iterrows()]
        df_w1y['user_name'] = usernames_w1y
        df_w1y = df_w1y[cols]
        df_w1y.to_csv(OUT_DIR / f"top50_gap_within1y_{year}.csv", index=False, encoding='utf-8-sig')

    print("2023-2026 full analysis complete! All CSVs exported.")

if __name__ == '__main__':
    run_analysis()
