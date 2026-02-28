"""
Processing Overview:
既存のニコニコ全体統計データ（nico_vs_voiro.csv）を、最新のボイロ全体（software_talk）の集計結果で更新します。
ボイロ界隈の投稿数・再生数がニコニコ全体のどの程度の割合（シェア）を占めているかを再計算し、
分析結果の一貫性を保つためのデータメンテナンスを行います。
"""

import pandas as pd
import os

def main():
    # 1. Load existing Nico stats (to avoid re-fetching)
    nico_csv_path = 'results/comparison/nico_vs_voiro.csv'
    if os.path.exists(nico_csv_path):
        print(f"Loading existing Nico stats from {nico_csv_path}")
        df_existing = pd.read_csv(nico_csv_path)
        # Keep only Nico columns
        df_nico = df_existing[['year', 'nico_total_videos', 'nico_total_views']].copy()
    else:
        print("Error: nico_vs_voiro.csv not found. Cannot update without base Nico data.")
        return

    # 2. Load Voiro stats
    voiro_csv_path = 'results/comparison/genre_comparison_yearly.csv'
    if not os.path.exists(voiro_csv_path):
        print(f"Error: {voiro_csv_path} not found.")
        return

    print(f"Loading Voiro stats from {voiro_csv_path}")
    df_voiro = pd.read_csv(voiro_csv_path)

    # 3. Filter for 'software_talk' category ONLY
    # This represents the true 'Overall' count
    df_voiro_overall = df_voiro[df_voiro['category'] == 'software_talk'].copy()
    
    if df_voiro_overall.empty:
        print("Error: No 'software_talk' category found in genre stats.")
        return

    df_voiro_agg = df_voiro_overall[['year', 'post_count', 'total_views']].copy()
    df_voiro_agg.rename(columns={'post_count': 'voiro_videos', 'total_views': 'voiro_views'}, inplace=True)

    # 4. Merge
    df_merged = pd.merge(df_nico, df_voiro_agg, on='year', how='left')

    # 5. Calculate Ratios
    df_merged['video_ratio_percent'] = (df_merged['voiro_videos'] / df_merged['nico_total_videos']) * 100
    df_merged['view_ratio_percent'] = (df_merged['voiro_views'] / df_merged['nico_total_views']) * 100
    
    # Fill NaN with 0
    df_merged.fillna(0, inplace=True)

    # 6. Save
    output_path = 'results/comparison/nico_vs_voiro.csv'
    df_merged.to_csv(output_path, index=False)
    print(f"Updated comparison saved to {output_path}")
    print(df_merged.to_string(index=False))

if __name__ == "__main__":
    main()
