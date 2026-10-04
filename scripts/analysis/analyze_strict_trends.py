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

def analyze_strict_trends(df):
    results = []
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    # Strict regex patterns for series
    patterns = {
        'part_style': r'(?i)part\s*\d+',
        'episode_style': r'第[一二三四五六七八九十\d]+話|[一二三四五六七八九十\d]+話',
        'symbol_style': r'#\d{1,3}\b|No\.\d{1,3}\b|vol\.\d{1,3}\b',
        'bracket_style': r'[【（\(\[［](?!20[12]\d|1080|720|4k|4K)\d{1,3}[】）\)\]］]',
        'prefix_style': r'第[一二三四五六七八九十\d]+[回 ]|其の[一二三四五六七八九十\d]+|その\d+(?:\.\d+)?|Phase\s*\d+|SS\.\d+',
        # Bare numbers at the end: Requires a preceding space or hyphen, 1 to 3 digits (no more to avoid years like 2024)
        'bare_number_style': r'[\s\-]\d{1,3}$'
    }

    print("--- Strict Analysis: All Videos vs Top 1000 ---")
    
    for year in years:
        year_df = df[df['year'] == year]
        if len(year_df) == 0:
            continue
            
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        # 1. Length Analysis (Median)
        all_median_len = year_df['lengthSeconds'].median()
        top_median_len = top_1000['lengthSeconds'].median()
        
        # 2. Series Detection (Strict)
        def is_series(text):
            if not isinstance(text, str): return False
            for p in patterns.values():
                if re.search(p, text): return True
            return False

        all_series_mask = year_df['title'].apply(is_series)
        top_series_mask = top_1000['title'].apply(is_series)
        
        all_series_ratio = all_series_mask.sum() / len(year_df)
        top_series_ratio = top_series_mask.sum() / len(top_1000)
        
        results.append({
            'year': year,
            'all_count': len(year_df),
            'all_median_len': all_median_len,
            'top_median_len': top_median_len,
            'all_series_ratio': f"{all_series_ratio:.1%}",
            'top_series_ratio': f"{top_series_ratio:.1%}"
        })
        
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    df = load_data()
    analyze_strict_trends(df)
