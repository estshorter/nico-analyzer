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
    year_target = 2024
    min_len = 60 # 1分
    max_len = 120 # 2分
    
    df = preprocess(category)
    if df is None: return

    # userIdの列名
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    # 2025年の1-2分動画
    df_2025 = df[df["year"] == year_target]
    mask_short = (df_2025["lengthSeconds"] >= min_len) & (df_2025["lengthSeconds"] <= max_len)
    df_short = df_2025[mask_short]
    
    # 投稿数カウント
    user_counts = df_short[user_id_col].value_counts().reset_index()
    user_counts.columns = ["userId", "videoCount"]
    total_videos = user_counts["videoCount"].sum()
    
    # 上位2名
    top2 = user_counts.head(2).copy()
    top2_sum = top2["videoCount"].sum()
    others_sum = total_videos - top2_sum
    
    print(f"Total 1-2min videos: {total_videos}")
    print(f"Top 1: {int(top2.iloc[0]['userId'])} - {top2.iloc[0]['videoCount']} videos ({(top2.iloc[0]['videoCount']/total_videos*100):.1f}%)")
    print(f"Top 2: {int(top2.iloc[1]['userId'])} - {top2.iloc[1]['videoCount']} videos ({(top2.iloc[1]['videoCount']/total_videos*100):.1f}%)")
    print(f"Top 2 Total: {top2_sum} videos ({(top2_sum/total_videos*100):.1f}%)")

    # グラフ設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['figure.dpi'] = 200

    fig, ax = plt.subplots(figsize=(14, 4))
    
    # データ準備
    p1 = top2.iloc[0]['videoCount'] / total_videos * 100
    p2 = top2.iloc[1]['videoCount'] / total_videos * 100
    p_others = others_sum / total_videos * 100
    
    # 積み上げバー
    colors = ["#1f77b4", "#ff7f0e", "#d1d5db"] # Blue, Orange, Gray
    
    ax.barh([0], [p1], color=colors[0], label=f"User {int(top2.iloc[0]['userId'])}", height=0.6)
    ax.barh([0], [p2], left=[p1], color=colors[1], label=f"User {int(top2.iloc[1]['userId'])}", height=0.6)
    ax.barh([0], [p_others], left=[p1+p2], color=colors[2], label="Others", height=0.6)
    
    # ラベル追加
    ax.text(p1/2, 0, f"{p1:.1f}%\n({int(top2.iloc[0]['videoCount'])}本)", ha='center', va='center', color='white', fontweight='bold')
    ax.text(p1 + p2/2, 0, f"{p2:.1f}%\n({int(top2.iloc[1]['videoCount'])}本)", ha='center', va='center', color='white', fontweight='bold')
    ax.text(p1 + p2 + p_others/2, 0, f"その他\n({others_sum}本)", ha='center', va='center', color='black', fontweight='bold')

    # タイトルと軸の設定
    plt.title("2025年 解説ジャンル 1分-2分動画の投稿者占有率", pad=20)
    ax.set_xlabel("シェア (%)")
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    output_path = "results/explanation/explanation_short_stacked_bar_2025.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
