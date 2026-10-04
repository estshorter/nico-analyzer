import pickle
import pandas as pd
import re

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

def analyze_naming_trends(df):
    results = []
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    print("--- Comparison of Series Naming: 'part' vs '話' ---")
    
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        # Count 'part' / 'Part'
        part_count = top_1000['title'].str.contains('part', case=False, na=False).sum()
        
        # Count '話' (excluding words like '世話' or '話題')
        # We look for digits followed by '話' or '話' preceded by digits/kanji numbers
        hana_pattern = r'\d+話|[一二三四五六七八九十]+話|第.+話'
        hana_count = top_1000['title'].str.contains(hana_pattern, na=False).sum()
        
        results.append({
            'year': year,
            'part_count': part_count,
            'hana_count': hana_count,
            'total_top': len(top_1000)
        })
    
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    
    # Identify top users for '話' style in 2024-2025
    print("\n--- Top '話' (Episode) style users (2024-2025) ---")
    recent_df = df[df['year'].isin([2024, 2025])]
    recent_top = recent_df.sort_values('viewCounter', ascending=False).head(2000)
    hana_videos = recent_top[recent_top['title'].str.contains(hana_pattern, na=False)]
    
    if not hana_videos.empty:
        user_counts = hana_videos['userId'].value_counts().head(5)
        for user_id, count in user_counts.items():
            sample = hana_videos[hana_videos['userId'] == user_id]['title'].iloc[0]
            print(f"User ID {user_id}: {count} videos (Sample: {sample})")

if __name__ == "__main__":
    df = load_data()
    analyze_naming_trends(df)
