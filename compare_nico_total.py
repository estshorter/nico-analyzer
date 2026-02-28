"""
Processing Overview:
外部サイト（nicochart.jp）からニコニコ動画全体の年間統計情報（投稿数・再生数）を取得します。
得られた全体データとボイロ界隈（software_talkカテゴリ）のデータを統合し、
ボイロ界隈がニコニコ全体に占める動画数・再生数の比率（シェア）を算出・保存します。
"""

import urllib.request
import csv
import time
import os
import pandas as pd

# Define the years to process
years = range(2011, 2026)

# Store results
nico_stats = []

print("Fetching data from nicochart.jp...")
for year in years:
    try:
        # 1. Fetch January Data (Start of Year)
        url_jan = f"https://www.nicochart.jp/total/{year}01.tsv"
        print(f"Fetching {url_jan}...")
        with urllib.request.urlopen(url_jan) as response:
            content = response.read().decode('utf-8').strip()
            lines = content.split('\n')
            # Take the FIRST data line
            first_line = lines[0].split('\t')
            # Format: [Date] [Time] [Epoch] [TotalVideos] [TotalViews] [TotalComments]
            start_videos = int(first_line[3])
            start_views = int(first_line[4])

        # 2. Fetch December Data (End of Year)
        url_dec = f"https://www.nicochart.jp/total/{year}12.tsv"
        print(f"Fetching {url_dec}...")
        with urllib.request.urlopen(url_dec) as response:
            content = response.read().decode('utf-8').strip()
            lines = content.split('\n')
            # Take the LAST data line
            last_line = lines[-1].split('\t')
            end_videos = int(last_line[3])
            end_views = int(last_line[4])

        # 3. Calculate Yearly Increase
        yearly_videos = end_videos - start_videos
        yearly_views = end_views - start_views

        nico_stats.append({
            'year': year,
            'nico_total_videos': yearly_videos,
            'nico_total_views': yearly_views
        })
        print(f"Stats for {year}: Videos={yearly_videos}, Views={yearly_views}")
        time.sleep(1) 

    except Exception as e:
        print(f"Error fetching data for {year}: {e}")
        nico_stats.append({
            'year': year,
            'nico_total_videos': 0,
            'nico_total_views': 0
        })

# Create DataFrame for Nico stats
df_nico = pd.DataFrame(nico_stats)

# Load Voiceroid stats
voiceroid_csv_path = 'results/comparison/genre_comparison_yearly.csv'

if os.path.exists(voiceroid_csv_path):
    print("Loading Voiceroid stats...")
    df_voiro = pd.read_csv(voiceroid_csv_path)
    
    # Aggregate Voiceroid stats by year (ONLY software_talk to represent overall)
    df_voiro_agg = df_voiro[df_voiro['category'] == 'software_talk'].copy()
    df_voiro_agg = df_voiro_agg[['year', 'post_count', 'total_views']]
    df_voiro_agg.rename(columns={'post_count': 'voiro_videos', 'total_views': 'voiro_views'}, inplace=True)
    
    # Merge datasets
    df_merged = pd.merge(df_nico, df_voiro_agg, on='year', how='left')
    
    # Calculate Ratios
    # Handle division by zero if any
    df_merged['video_ratio_percent'] = (df_merged['voiro_videos'] / df_merged['nico_total_videos']) * 100
    df_merged['view_ratio_percent'] = (df_merged['voiro_views'] / df_merged['nico_total_views']) * 100
    
    # Fill NaN with 0
    df_merged.fillna(0, inplace=True)

    # Display comparison
    print("\nComparison Results (Nico Total vs Voiceroid Total):")
    print(df_merged.to_string(index=False))
    
    # Save to CSV
    output_path = 'results/comparison/nico_vs_voiro.csv'
    df_merged.to_csv(output_path, index=False)
    print(f"\nSaved comparison to {output_path}")

else:
    print(f"Error: {voiceroid_csv_path} not found.")
