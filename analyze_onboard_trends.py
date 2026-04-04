import pickle
import pandas as pd
from datetime import datetime
import json

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

def analyze_length(df):
    print("--- Hypothesis 1: Video Length Shortening ---")
    results = []
    # Filter only years with significant data
    years = sorted(df['year'].unique())
    for year in years:
        year_df = df[df['year'] == year]
        # Top 1000 by viewCounter
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        mean_len = top_1000['lengthSeconds'].mean()
        median_len = top_1000['lengthSeconds'].median()
        count = len(top_1000)
        
        results.append({
            'year': year,
            'mean_length': mean_len,
            'median_length': median_len,
            'count': count
        })
    
    res_df = pd.DataFrame(results)
    print(res_df)
    return res_df

def extract_titles_for_gemini(df):
    print("\n--- Hypothesis 2: Shift to Project-Oriented (Data for Gemini) ---")
    years = sorted(df['year'].unique())
    # Take more recent years and some old years for comparison
    sample_years = [y for y in years if y >= 2012] 
    
    summary = {}
    for year in sample_years:
        year_df = df[df['year'] == year]
        # Top 50 titles
        top_50 = year_df.sort_values('viewCounter', ascending=False).head(50)
        summary[str(year)] = top_50['title'].tolist()
    
    with open('results/onboard_titles_sample.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Top 50 titles for years {sample_years} saved to results/onboard_titles_sample.json")

def analyze_keywords(df):
    print("\n--- Keyword Frequency (Simple Proxy for Project-Oriented) ---")
    keywords = {
        '企画': 'kikaku', 
        '検証': 'kensho', 
        'RTA': 'rta', 
        'チャレンジ': 'challenge', 
        '日本一周': 'japan_tour', 
        '走ってみた': 'driven', 
        'キャンプ': 'camp', 
        '料理': 'cooking', 
        '酷道': 'kokudo'
    }
    
    results = []
    years = sorted(df['year'].unique())
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        row = {'year': year}
        for kw_jp, kw_en in keywords.items():
            # Simple substring match
            count = top_1000['title'].str.contains(kw_jp, case=False, na=False).sum()
            row[kw_jp] = count / len(top_1000) if len(top_1000) > 0 else 0
        results.append(row)
    
    kw_df = pd.DataFrame(results)
    print(kw_df.to_string(index=False))
    return kw_df

if __name__ == "__main__":
    df = load_data()
    analyze_length(df)
    analyze_keywords(df)
    extract_titles_for_gemini(df)
