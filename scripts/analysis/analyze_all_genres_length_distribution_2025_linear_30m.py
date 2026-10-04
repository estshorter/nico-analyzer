# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "scipy",
# ]
# ///

import pickle
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
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
    target_categories = ["onboard", "travel", "game", "theater", "kitchen", "explanation"]
    year_target = 2025
    
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(12, 8))
    
    label_map = {
        "onboard": "車載",
        "travel": "旅行",
        "game": "実況",
        "theater": "劇場",
        "kitchen": "キッチン",
        "explanation": "解説"
    }
    colors = plt.get_cmap("Dark2").colors

    for i, category in enumerate(target_categories):
        df = preprocess(category)
        if df is None: continue
        # 30分以下のデータに絞るのではなく、描画範囲を30分にする（分布自体は全体で計算）
        year_data = df[df["year"] == year_target]["lengthSeconds"]
        year_data = year_data / 60.0 # 分に変換
        
        sns.kdeplot(year_data, label=label_map[category], 
                    color=colors[i % 8], linewidth=4, alpha=0.8)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("密度 (Density)")
    plt.title(f"{year_target}年 主要ジャンル別再生時間分布 (0-30分)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper right')
    
    plt.xlim(0, 30) # 0分から30分に限定
    plt.xticks(range(0, 31, 5)) # 5分おきに目盛り
    
    plt.tight_layout()
    output_path = "results/all_genres_length_distribution_2025_linear_30m.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
