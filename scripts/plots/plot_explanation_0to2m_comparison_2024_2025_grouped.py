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

def main():
    category = "explanation"
    label = "解説"
    df = preprocess(category)
    if df is None: return
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    target_years = [2024, 2025]

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
        heavy_users_sum = heavy_users["videoCount"].sum()
        others_sum = total_videos - heavy_users_sum
        
        y_pos = 1 - idx
        
        # 100件以上投稿しているユーザー群
        ax.barh([y_pos], [heavy_users_sum], left=[0], color="#ef4444", height=0.6)
        if heavy_users_sum > 50:
            ax.text(heavy_users_sum/2, y_pos, f"{int(heavy_users_sum)}", 
                    ha='center', va='center', color='white', fontweight='bold', fontsize=16)
            
        # その他
        ax.barh([y_pos], [others_sum], left=[heavy_users_sum], color="#d1d5db", height=0.6)
        if others_sum > 50:
            ax.text(heavy_users_sum + others_sum/2, y_pos, f"{int(others_sum)}", 
                    ha='center', va='center', color='black', fontweight='bold', fontsize=16)
            
        # 合計本数を右端に表示
        ax.text(total_videos + 20, y_pos, f"{int(total_videos)}", va='center', fontweight='bold', fontsize=22)

    plt.title(f"{label}ジャンル 0-2分動画の投稿数比較 (量産群統合)", pad=35)
    plt.xlabel("投稿本数 (本)", labelpad=15)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["2024年", "2025年"], fontsize=18)
    
    # X軸の範囲を調整
    ax.set_xlim(0, 2800)
    plt.grid(True, axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout()
    output_path = "results/explanation/explanation_0to2m_comparison_2024_2025_grouped.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Comparison graph saved to: {output_path}")

if __name__ == "__main__":
    main()
