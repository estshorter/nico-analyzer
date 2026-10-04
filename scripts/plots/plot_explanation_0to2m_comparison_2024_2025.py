# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "seaborn",
# ]
# ///

import pickle
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import numpy as np
import seaborn as sns
import string

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    return df

def get_heavy_users_all_years(df, target_years):
    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    all_heavy_users = set()
    
    for year in target_years:
        df_year = df[df["year"] == year]
        mask = (df_year["lengthSeconds"] >= 0) & (df_year["lengthSeconds"] <= 120)
        df_short = df_year[mask]
        counts = df_short[user_id_col].value_counts()
        heavy = counts[counts >= 100].index.tolist()
        all_heavy_users.update(map(int, heavy))
    
    sorted_users = sorted(list(all_heavy_users))
    palette = sns.color_palette("tab10", len(sorted_users))
    
    # IDをマスクするためのマッピング作成
    labels = list(string.ascii_uppercase)
    if len(sorted_users) > len(labels):
        labels = [f"{i+1}" for i in range(len(sorted_users))]
    
    user_info_map = {}
    for i, uid in enumerate(sorted_users):
        user_info_map[uid] = {
            "color": palette[i],
            "label": f"投稿者{labels[i]}"
        }
    
    return user_info_map

def main():
    category = "explanation"
    label = "解説"
    df = preprocess(category)
    if df is None: return
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    target_years = [2024, 2025]
    user_info_map = get_heavy_users_all_years(df, target_years)

    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 28
    plt.rcParams['axes.labelsize'] = 22
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['xtick.labelsize'] = 18
    plt.rcParams['ytick.labelsize'] = 20
    plt.rcParams['figure.dpi'] = 200

    fig, ax = plt.subplots(figsize=(15, 8))

    for idx, year in enumerate(target_years):
        df_year = df[df["year"] == year]
        mask = (df_year["lengthSeconds"] >= 0) & (df_year["lengthSeconds"] <= 120)
        df_short = df_year[mask]
        
        user_counts = df_short[user_id_col].value_counts().reset_index()
        user_counts.columns = ["userId", "videoCount"]
        total_videos = user_counts["videoCount"].sum()
        
        heavy_users = user_counts[user_counts["videoCount"] >= 100].copy()
        others_sum = total_videos - heavy_users["videoCount"].sum()
        
        current_left = 0
        y_pos = 1 - idx
        
        for i, row in heavy_users.iterrows():
            uid = int(row['userId'])
            count = row['videoCount']
            info = user_info_map.get(uid)
            
            ax.barh([y_pos], [count], left=[current_left], color=info["color"], height=0.6)
            
            # ラベル表示 (本数のみ)
            if count > 50:
                ax.text(current_left + count/2, y_pos, f"{int(count)}", 
                        ha='center', va='center', color='white', fontweight='bold', fontsize=16)
            current_left += count
            
        # その他
        ax.barh([y_pos], [others_sum], left=[current_left], color="#d1d5db", height=0.6)
        if others_sum > 50:
            ax.text(current_left + others_sum/2, y_pos, f"{int(others_sum)}", 
                    ha='center', va='center', color='black', fontweight='bold', fontsize=16)
            
        # 合計本数を右端に表示 (数字のみ)
        ax.text(total_videos + 20, y_pos, f"{int(total_videos)}", va='center', fontweight='bold', fontsize=22)

    plt.title(f"{label}ジャンル 0-2分動画の投稿数比較", pad=35)
    plt.xlabel("投稿本数 (本)", labelpad=15)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["2024年", "2025年"], fontsize=18)
    
    # X軸の範囲を調整
    ax.set_xlim(0, 2800)
    plt.grid(True, axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout()
    output_path = "results/explanation/explanation_0to2m_comparison_2024_2025.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Comparison graph saved to: {output_path}")

if __name__ == "__main__":
    main()
