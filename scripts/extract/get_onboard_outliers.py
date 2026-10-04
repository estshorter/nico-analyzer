import pickle
import pandas as pd
import os

def main():
    # Load data
    if not os.path.exists('results/onboard.pickle'):
        print("Error: results/onboard.pickle not found.")
        return

    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    
    # Filter years 2020-2025
    df = df[(df['year'] >= 2020) & (df['year'] <= 2025)]
    
    # Group by userId and year to get post count per user per year
    user_year_counts = df.groupby(['userId', 'year']).size().reset_index(name='post_count')
    
    results = []
    years = sorted(user_year_counts['year'].unique())
    
    print("--- 統計学的な外れ値（Q3 + 1.5*IQR 超え）のトップユーザー ---")
    
    for year in years:
        year_data = user_year_counts[user_year_counts['year'] == year]
        q1 = year_data['post_count'].quantile(0.25)
        q3 = year_data['post_count'].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        
        outliers = year_data[year_data['post_count'] > upper_bound].sort_values('post_count', ascending=False)
        
        print(f"\n【{year}年】(外れ値の境界線: {upper_bound:.1f}本以上)")
        print(f"外れ値ユーザー数: {len(outliers)}人 / 全投稿者: {len(year_data)}人")
        print("トップ10ユーザー:")
        print(outliers.head(10).to_string(index=False))
        
        results.append({
            'year': year,
            'upper_bound': upper_bound,
            'outlier_count': len(outliers),
            'top_outlier_id': outliers.iloc[0]['userId'] if not outliers.empty else None,
            'top_outlier_count': outliers.iloc[0]['post_count'] if not outliers.empty else None
        })

if __name__ == "__main__":
    main()
