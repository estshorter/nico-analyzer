# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
# ]
# ///

import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def main():
    category = "onboard"
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"File not found: {pickle_path}")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    # フィルタ条件:
    # 「投稿祭」が含まれる（シンプル車載等すべて含む）
    mask_fest = df["tags"].str.contains("投稿祭", na=False)
    
    filtered_df = df[mask_fest].copy()
    
    filtered_df["startTime"] = pd.to_datetime(filtered_df["startTime"])
    filtered_df["year"] = filtered_df["startTime"].dt.year
    
    # 年別の件数を集計
    counts_by_year = filtered_df.groupby("year").size().reset_index(name="count")
    
    # グラフ設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.titlesize'] = 20
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(12, 7))
    sns.barplot(data=counts_by_year, x="year", y="count", color="salmon")
    
    # バーの上に数値を表示
    for i, count in enumerate(counts_by_year["count"]):
        plt.text(i, count + 0.1, str(count), ha='center', va='bottom', fontweight='bold')

    plt.xlabel("年")
    plt.ylabel("投稿数")
    plt.title("車載カテゴリ 投稿祭関連動画数 (年別)\n※シンプル車載動画投稿祭を含むすべて")
    plt.grid(True, axis="y", linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    output_path = Path("results/onboard/fest_count_all.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved: {output_path}")
    print("\n年別件数 (全投稿祭):")
    print(counts_by_year)

if __name__ == "__main__":
    main()
