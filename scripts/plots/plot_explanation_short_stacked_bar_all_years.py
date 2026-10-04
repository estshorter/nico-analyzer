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

def generate_graph(df, year, category_label, output_path):
    # userIdの列名
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    # 指定年の1-2分動画
    df_year = df[df["year"] == year]
    min_len = 60
    max_len = 120
    mask_short = (df_year["lengthSeconds"] >= min_len) & (df_year["lengthSeconds"] <= max_len)
    df_short = df_year[mask_short]
    
    # 投稿数カウント
    user_counts = df_short[user_id_col].value_counts().reset_index()
    user_counts.columns = ["userId", "videoCount"]
    total_videos = user_counts["videoCount"].sum()
    
    if total_videos == 0:
        print(f"No data for year {year}")
        return

    # 上位2名
    top2 = user_counts.head(2).copy()
    top2_sum = top2["videoCount"].sum()
    others_sum = total_videos - top2_sum
    
    # データ準備
    p1 = top2.iloc[0]['videoCount'] / total_videos * 100
    p2 = top2.iloc[1]['videoCount'] / total_videos * 100 if len(top2) > 1 else 0
    p_others = others_sum / total_videos * 100
    
    # グラフ設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['figure.dpi'] = 200

    fig, ax = plt.subplots(figsize=(14, 4))
    
    # 積み上げバー
    colors = ["#1f77b4", "#ff7f0e", "#d1d5db"] # Blue, Orange, Gray
    
    ax.barh([0], [p1], color=colors[0], label=f"Top 1", height=0.6)
    if p2 > 0:
        ax.barh([0], [p2], left=[p1], color=colors[1], label=f"Top 2", height=0.6)
    ax.barh([0], [p_others], left=[p1+p2], color=colors[2], label="Others", height=0.6)
    
    # ラベル追加 (シェアが大きい場合のみテキスト表示)
    if p1 > 5:
        ax.text(p1/2, 0, f"{p1:.1f}%\n({int(top2.iloc[0]['videoCount'])}本)", ha='center', va='center', color='white', fontweight='bold')
    if p2 > 5:
        ax.text(p1 + p2/2, 0, f"{p2:.1f}%\n({int(top2.iloc[1]['videoCount'])}本)", ha='center', va='center', color='white', fontweight='bold')
    if p_others > 5:
        ax.text(p1 + p2 + p_others/2, 0, f"その他\n({int(others_sum)}本)", ha='center', va='center', color='black', fontweight='bold')

    # タイトルと軸の設定
    plt.title(f"{year}年 {category_label}ジャンル 1分-2分動画の投稿者占有率", pad=20)
    ax.set_xlabel("シェア (%)")
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path} (Top2 Share: {(p1+p2):.1f}%)")

def main():
    category = "explanation"
    label = "解説"
    df = preprocess(category)
    if df is None: return

    for year in [2023, 2024, 2025]:
        output_path = f"results/explanation/explanation_short_stacked_bar_{year}.png"
        generate_graph(df, year, label, output_path)

if __name__ == "__main__":
    main()
