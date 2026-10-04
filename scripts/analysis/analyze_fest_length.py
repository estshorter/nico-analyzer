import pickle
import pandas as pd
import os

def main():
    if not os.path.exists('results/onboard.pickle'):
        print("Error: results/onboard.pickle not found.")
        return

    print("Loading data...")
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    df['is_fest'] = df['tags'].str.contains("祭", na=False)
    
    results = []
    years = sorted(df['year'].unique())
    # Filter years 2020-2025
    years = [y for y in years if 2020 <= y <= 2025]
    
    for year in years:
        year_df = df[df['year'] == year]
        
        fest_df = year_df[year_df['is_fest']]
        non_fest_df = year_df[~year_df['is_fest']]
        
        fest_median = fest_df['lengthSeconds'].median() if not fest_df.empty else 0
        non_fest_median = non_fest_df['lengthSeconds'].median() if not non_fest_df.empty else 0
        
        fest_mean = fest_df['lengthSeconds'].mean() if not fest_df.empty else 0
        non_fest_mean = non_fest_df['lengthSeconds'].mean() if not non_fest_df.empty else 0
        
        # Look at the percentage of short videos (< 3 minutes, < 5 minutes)
        fest_short_3m = (fest_df['lengthSeconds'] <= 180).mean() * 100 if not fest_df.empty else 0
        non_fest_short_3m = (non_fest_df['lengthSeconds'] <= 180).mean() * 100 if not non_fest_df.empty else 0
        
        results.append({
            'Year': year,
            'Fest Median (s)': f"{fest_median:.0f}",
            'Non-Fest Median (s)': f"{non_fest_median:.0f}",
            'Fest <3m (%)': f"{fest_short_3m:.1f}%",
            'Non-Fest <3m (%)': f"{non_fest_short_3m:.1f}%",
        })
        
    res_df = pd.DataFrame(results)
    print("\n--- 祭動画 vs 通常動画 の再生時間比較 (2020-2025) ---")
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    main()
