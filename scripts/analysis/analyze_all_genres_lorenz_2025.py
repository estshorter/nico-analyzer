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
import sys
import tomllib
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

from common_utils import filter_software_talk

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    return df

def calculate_gini(values):
    """ジニ係数を計算する"""
    if len(values) == 0:
        return 0
    sorted_values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_values) / (n * np.sum(sorted_values))) - (n + 1) / n

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    plt.figure(figsize=(10, 10))
    # 均等分配線
    plt.plot([0, 100], [0, 100], 'k--', label="完全均等分配線", alpha=0.5)

    categories = list(cfg.keys())
    # 全体データは最後に描画
    if "software_talk" in categories:
        categories.remove("software_talk")
        categories.append("software_talk")

    colors = sns.color_palette("husl", len(categories))
    
    year_target = 2025
    has_plot = False

    for i, category in enumerate(categories):
        df = preprocess(category)
        if df is None:
            continue
            
        year_data = df[df["year"] == year_target]["viewCounter"]
        if len(year_data) == 0:
            continue
            
        sorted_views = np.sort(year_data.values)
        n = len(sorted_views)
        
        # 累積個数割合
        x_lorenz = np.arange(0, n + 1) / n
        # 累積再生数割合
        y_lorenz = np.insert(np.cumsum(sorted_views), 0, 0)
        y_lorenz = y_lorenz / y_lorenz[-1]
        
        gini = calculate_gini(sorted_views)
        
        label_base = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        label = f"{label_base} (Gini: {gini:.3f})"
        
        linewidth = 3 if category == "software_talk" else 2
        linestyle = "--" if category == "software_talk" else "-"
        alpha = 0.8 if category != "software_talk" else 1.0
        
        plt.plot(x_lorenz * 100, y_lorenz * 100, label=label, color=colors[i], 
                 linewidth=linewidth, linestyle=linestyle, alpha=alpha)
        has_plot = True

    if not has_plot:
        print("No data found for 2025.")
        return

    plt.xlabel("動画の累積割合 (下位からの累積 %)")
    plt.ylabel("再生数の累積割合 (%)")
    plt.title(f"{year_target}年 ジャンル別ローレンツ曲線 比較")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    output_path = Path("results/all_genres_lorenz_2025.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
