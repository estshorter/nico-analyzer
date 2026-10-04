import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# フォント設定
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'

def main():
    # Load data
    print("Loading data...")
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
    
    # Ensure post_count > 0 (Though .size() on grouped data usually yields >= 1, we make it explicit as requested)
    user_year_counts = user_year_counts[user_year_counts['post_count'] > 0]
    
    # Plotting
    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams['font.family']})
    
    # Boxplot showing ONLY the box (25th, 50th, 75th percentiles)
    # whis=0 removes the whiskers, showfliers=False removes outliers
    ax = sns.boxplot(
        x='year', y='post_count', data=user_year_counts, 
        hue='year', palette="viridis", legend=False,
        showfliers=False, whis=0
    )
    
    # Add title and labels
    plt.title('車載カテゴリ 投稿者別の年間投稿数分布 (2020-2025)\n※25, 50, 75パーセンタイルのみ表示', fontsize=22, pad=25)
    plt.xlabel('年', fontsize=18)
    plt.ylabel('年間投稿数', fontsize=18)
    
    # Set reasonable Y-axis limit for the boxes (the 75th percentile is around 6-7)
    plt.ylim(0, user_year_counts.groupby('year')['post_count'].quantile(0.75).max() + 2)
    
    # Add detailed percentile values and N= counts as text on the plot
    years = sorted(user_year_counts['year'].unique())
    stats = user_year_counts.groupby('year')['post_count'].describe(percentiles=[.25, .5, .75])
    counts = user_year_counts.groupby('year')['post_count'].count()
    
    for i, year in enumerate(years):
        p25 = stats.loc[year, '25%']
        p50 = stats.loc[year, '50%']
        p75 = stats.loc[year, '75%']
        count_val = counts[year]
        
        # Label 75th percentile
        ax.text(i, p75 + 0.1, f'75%: {p75:.0f}', ha='center', va='bottom', fontsize=12, color='blue')
        # Label Median
        ax.text(i, p50 + 0.1, f'50%: {p50:.0f}', ha='center', va='bottom', fontsize=12, color='darkred', fontweight='bold')
        # Label 25th percentile
        ax.text(i, p25 - 0.1, f'25%: {p25:.0f}', ha='center', va='top', fontsize=12, color='green')
        
        # Label sample size at the bottom
        ax.text(i, -0.5, f'N={count_val}', ha='center', va='top', fontsize=14, fontweight='normal')

    # Ensure output directory exists
    os.makedirs('results/onboard', exist_ok=True)
    
    output_path = 'results/onboard/annual_post_count_quartiles.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    main()
