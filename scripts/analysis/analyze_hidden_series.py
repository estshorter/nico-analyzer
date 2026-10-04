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

def analyze_all_numbering_styles(df):
    results = []
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    # Define regex patterns for different series styles
    patterns = {
        'part_style': r'part|Part',
        'episode_style': r'\d+話|[一二三四五六七八九十]+話|第.+話',
        'symbol_style': r'#\d+|No\.\d+|vol\.\d+',
        'bracket_style': r'[【（\(\[［]\d+[】）\)\]］]',
        'prefix_style': r'第\d+[回 ]|其の[一二三四五六七八九十\d]+',
        'suffix_num_style': r'\s\d{1,3}$' # Ends with 1-3 digits space-separated
    }
    
    print("--- Detailed Series Naming Trends (Top 1000 each year) ---")
    
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        counts = {'year': year}
        any_series_mask = pd.Series([False] * len(top_1000), index=top_1000.index)
        
        for name, pattern in patterns.items():
            mask = top_1000['title'].str.contains(pattern, case=False, na=False)
            counts[name] = mask.sum()
            any_series_mask |= mask
            
        counts['TOTAL_SERIES'] = any_series_mask.sum()
        results.append(counts)
    
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    
    # Sample check for 'symbol_style' and 'bracket_style' in 2024
    print("\n--- Samples of 'Symbol/Bracket/Suffix' style in 2024 ---")
    df_2024 = df[df['year'] == 2024].sort_values('viewCounter', ascending=False).head(1000)
    hidden_patterns = f"({patterns['symbol_style']}|{patterns['bracket_style']}|{patterns['suffix_num_style']})"
    samples = df_2024[df_2024['title'].str.contains(hidden_patterns, case=False, na=False)]['title'].head(10).tolist()
    for s in samples:
        print(f"  - {s}")

if __name__ == "__main__":
    df = load_data()
    analyze_all_numbering_styles(df)
